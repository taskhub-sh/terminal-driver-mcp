"""MCP Server for Terminal Control

FastMCP-based server implementation providing terminal interaction tools
through virtual X11 displays.
"""

from typing import Dict, Any, Optional
from fastmcp import FastMCP

from .xterm_session import XTermSession
from .logging_config import get_logger

logger = get_logger(__name__)

# Global MCP instance and sessions dictionary
mcp = FastMCP("Terminal Control MCP")
sessions: Dict[str, XTermSession] = {}


@mcp.tool()
async def terminal_launch(
    command: str = "bash", width: int = 80, height: int = 24
) -> Dict[str, Any]:
    """Launch a new terminal session with virtual X11 display

    Args:
        command: Command to run in terminal (default: bash)
        width: Terminal width in characters (default: 80)
        height: Terminal height in characters (default: 24)

    Returns:
        Dictionary with session_id and status
    """
    try:
        session = XTermSession(command=command, width=width, height=height)
        await session.start()

        session_id = session.session_id
        sessions[session_id] = session

        logger.info(
            f"Launched terminal session {session_id} with command: {command}"
        )
        return {
            "session_id": session_id,
            "status": "launched",
            "command": command,
            "width": width,
            "height": height,
        }

    except Exception as e:
        logger.error(f"Failed to launch terminal session: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def terminal_input(
    session_id: str, input_text: Optional[str] = None, key: Optional[str] = None
) -> Dict[str, Any]:
    """Send input to a terminal session

    Args:
        session_id: ID of the terminal session
        input_text: Text to type (for alphanumeric input)
        key: Special key to send (Return, Tab, Escape, etc.)

    Returns:
        Dictionary with status and input confirmation
    """
    if session_id not in sessions:
        return {"status": "error", "error": f"Session {session_id} not found"}

    session = sessions[session_id]

    try:
        if input_text is not None:
            await session.send_text(input_text)
            action = f"typed text: {input_text}"
        elif key is not None:
            await session.send_key(key)
            action = f"sent key: {key}"
        else:
            return {
                "status": "error",
                "error": "Must provide either input_text or key",
            }

        logger.info(f"Session {session_id}: {action}")
        return {"session_id": session_id, "status": "sent", "action": action}

    except Exception as e:
        logger.error(f"Failed to send input to session {session_id}: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def terminal_capture(session_id: str) -> Dict[str, Any]:
    """Capture terminal screen as PNG screenshot

    Args:
        session_id: ID of the terminal session

    Returns:
        Dictionary with base64-encoded PNG image and metadata
    """
    if session_id not in sessions:
        return {"status": "error", "error": f"Session {session_id} not found"}

    session = sessions[session_id]

    try:
        screenshot_data = await session.capture_screenshot()

        logger.info(f"Captured screenshot for session {session_id}")
        return {
            "session_id": session_id,
            "status": "captured",
            "image_data": screenshot_data["image_data"],
            "metadata": screenshot_data["metadata"],
        }

    except Exception as e:
        logger.error(
            f"Failed to capture screenshot for session {session_id}: {e}"
        )
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def terminal_close(session_id: str) -> Dict[str, Any]:
    """Close a terminal session and cleanup resources

    Args:
        session_id: ID of the terminal session

    Returns:
        Dictionary with cleanup status
    """
    if session_id not in sessions:
        return {"status": "error", "error": f"Session {session_id} not found"}

    session = sessions[session_id]

    try:
        await session.cleanup()
        del sessions[session_id]

        logger.info(f"Closed terminal session {session_id}")
        return {"session_id": session_id, "status": "closed"}

    except Exception as e:
        logger.error(f"Failed to close session {session_id}: {e}")
        return {"status": "error", "error": str(e)}


async def cleanup_all_sessions():
    """Cleanup all active sessions"""
    logger.info("Cleaning up all terminal sessions")
    
    for session_id, session in list(sessions.items()):
        try:
            await session.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
    
    sessions.clear()


if __name__ == "__main__":
    import asyncio
    import signal
    
    async def main():
        """Main entry point for the server"""
        logger.info("Starting Terminal Control MCP Server")
        
        # Setup cleanup on shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup_all_sessions()))
        
        try:
            await mcp.run()
        finally:
            await cleanup_all_sessions()

    asyncio.run(main())
