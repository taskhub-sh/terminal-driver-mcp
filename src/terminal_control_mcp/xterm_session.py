"""XTerm Session Management

Manages xterm sessions with virtual X11 displays for terminal interaction.
Based on the pattern from examples/example_htop.py but adapted for async operations.
"""

import asyncio
import os
import time
import base64
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

from .logging_config import get_logger

logger = get_logger(__name__)


class XTermSession:
    """Manages an xterm session with virtual X11 display"""

    def __init__(self, command: str = "bash", width: int = 80, height: int = 24):
        self.session_id = str(uuid.uuid4())
        self.command = command
        self.terminal_width = width
        self.terminal_height = height

        # Display settings
        self.display_width = max(1024, width * 12)  # Approximate pixel width
        self.display_height = max(768, height * 20)  # Approximate pixel height
        # Find a free display number
        self.display = self._find_free_display()

        # Process handles
        self.xvfb_proc: Optional[asyncio.subprocess.Process] = None
        self.xterm_proc: Optional[asyncio.subprocess.Process] = None

        # State tracking
        self.is_running = False
        self.temp_dir = None

    def _find_free_display(self, start: int = 100, max_attempts: int = 100) -> str:
        """Find a free X11 display number by checking socket files"""
        for display_num in range(start, start + max_attempts):
            socket_path = f"/tmp/.X11-unix/X{display_num}"
            if not os.path.exists(socket_path):
                logger.debug(f"Found free display: :{display_num}")
                return f":{display_num}"
        
        # Fallback to a high number if all checked ports are taken
        fallback_display = start + max_attempts
        logger.warning(f"All displays {start}-{start + max_attempts - 1} appear taken, using :{fallback_display}")
        return f":{fallback_display}"

    async def start(self):
        """Start the virtual display and xterm session"""
        try:
            await self._start_virtual_display()
            await self._start_xterm()
            self.is_running = True
            logger.info(f"Session {self.session_id} started successfully")

        except Exception as e:
            logger.error(f"Failed to start session {self.session_id}: {e}")
            await self.cleanup()
            raise

    async def _start_virtual_display(self):
        """Start Xvfb virtual display"""
        logger.debug(f"Starting virtual X display {self.display}")

        cmd = [
            "Xvfb",
            self.display,
            "-screen",
            "0",
            f"{self.display_width}x{self.display_height}x24",
            "-dpi",
            "100",
            "-ac",
            "+extension",
            "GLX",
        ]

        self.xvfb_proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for display to start
        await asyncio.sleep(2)

        if self.xvfb_proc.returncode is not None:
            _, stderr = await self.xvfb_proc.communicate()
            error_msg = stderr.decode() if stderr else "No stderr output"
            raise RuntimeError(
                f"Xvfb failed to start with return code {self.xvfb_proc.returncode}: {error_msg}"
            )

    async def _start_xterm(self):
        """Start xterm with the specified command"""
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        logger.debug(f"Starting xterm with command: {self.command}")

        cmd = [
            "xterm",
            "-geometry",
            f"{self.terminal_width}x{self.terminal_height}",
            "-fn",
            "-*-fixed-medium-r-*-*-14-*-*-*-*-*-*-*",
            "-bg",
            "black",
            "-fg",
            "white",
            "-e",
            self.command,
        ]

        self.xterm_proc = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )

        # Wait for xterm to start
        await asyncio.sleep(3)

        if self.xterm_proc.returncode is not None:
            raise RuntimeError(
                f"xterm failed to start with return code {self.xterm_proc.returncode}"
            )

    async def get_window_id(self) -> Optional[str]:
        """Get the xterm window ID using multiple search strategies"""
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        # Try multiple approaches to find the window
        search_methods = [
            ["xdotool", "search", "--class", "XTerm"],
            ["xdotool", "search", "--name", "xterm"],
            ["xdotool", "search", "--class", "xterm"],
            ["xdotool", "getactivewindow"],  # Get any active window
        ]

        for search_method in search_methods:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *search_method,
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await proc.communicate()

                if proc.returncode == 0:
                    window_id = stdout.decode().strip().split("\n")[0]
                    if window_id:
                        logger.debug(
                            f"Found window ID: {window_id} using {' '.join(search_method)}"
                        )
                        return window_id

            except Exception as e:
                logger.debug(f"Search method {search_method} failed: {e}")
                continue

        logger.warning(f"No window found for session {self.session_id}")
        return None

    async def send_key(self, key: str):
        """Send a key to the xterm window"""
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        window_id = await self.get_window_id()
        if not window_id:
            raise RuntimeError("No xterm window found")

        logger.debug(f"Sending key '{key}' to window {window_id}")

        # Focus the window first
        focus_proc = await asyncio.create_subprocess_exec(
            "xdotool",
            "windowfocus",
            window_id,
            env=env,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await focus_proc.wait()

        await asyncio.sleep(0.2)

        # Send the key
        key_proc = await asyncio.create_subprocess_exec(
            "xdotool",
            "key",
            "--window",
            window_id,
            key,
            env=env,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await key_proc.wait()

    async def send_text(self, text: str):
        """Send text to the xterm window"""
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        window_id = await self.get_window_id()
        if not window_id:
            raise RuntimeError("No xterm window found")

        logger.debug(f"Sending text '{text}' to window {window_id}")

        # Focus the window first
        focus_proc = await asyncio.create_subprocess_exec(
            "xdotool",
            "windowfocus",
            window_id,
            env=env,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await focus_proc.wait()

        await asyncio.sleep(0.2)

        # Send the text
        type_proc = await asyncio.create_subprocess_exec(
            "xdotool",
            "type",
            "--window",
            window_id,
            text,
            env=env,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await type_proc.wait()

    async def capture_screenshot(self) -> Dict[str, Any]:
        """Capture terminal screen as PNG screenshot and return base64 data"""
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        # Create temporary file for screenshot
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix=f"terminal_mcp_{self.session_id}_")

        screenshot_path = Path(self.temp_dir) / f"screenshot_{int(time.time())}.png"

        logger.debug(f"Taking screenshot: {screenshot_path}")

        try:
            # Take screenshot using ImageMagick import
            proc = await asyncio.create_subprocess_exec(
                "import",
                "-window",
                "root",
                str(screenshot_path),
                env=env,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Screenshot capture failed: {error_msg}")

            if not screenshot_path.exists():
                raise RuntimeError("Screenshot file was not created")

            # Read and encode the image
            with open(screenshot_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Get file metadata
            file_stats = screenshot_path.stat()
            metadata = {
                "timestamp": int(time.time()),
                "file_size": file_stats.st_size,
                "display_size": f"{self.display_width}x{self.display_height}",
                "terminal_size": f"{self.terminal_width}x{self.terminal_height}",
                "session_id": self.session_id,
            }

            # Clean up the temporary file
            screenshot_path.unlink()

            return {"image_data": image_data, "metadata": metadata}

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            # Clean up partial file if it exists
            if screenshot_path.exists():
                screenshot_path.unlink()
            raise

    async def cleanup(self):
        """Clean up processes and temporary files"""
        logger.debug(f"Cleaning up session {self.session_id}")

        self.is_running = False

        # Terminate xterm process
        if self.xterm_proc and self.xterm_proc.returncode is None:
            self.xterm_proc.terminate()
            try:
                await asyncio.wait_for(self.xterm_proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("xterm process didn't terminate gracefully, killing it")
                self.xterm_proc.kill()
                await self.xterm_proc.wait()

        # Terminate Xvfb process
        if self.xvfb_proc and self.xvfb_proc.returncode is None:
            self.xvfb_proc.terminate()
            try:
                await asyncio.wait_for(self.xvfb_proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Xvfb process didn't terminate gracefully, killing it")
                self.xvfb_proc.kill()
                await self.xvfb_proc.wait()

        # Clean up temporary directory
        if self.temp_dir:
            try:
                import shutil

                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.temp_dir = None
            except Exception as e:
                logger.warning(f"Failed to clean up temp dir: {e}")

        # Small delay to let X server cleanup
        await asyncio.sleep(0.5)

        logger.info(f"Session {self.session_id} cleanup completed")
