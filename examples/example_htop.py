#!/usr/bin/env python3
"""
Example script demonstrating terminal control with htop using xterm approach
- Spawns htop in xterm with virtual display
- Presses F3 to search
- Takes actual PNG screenshots
- Uses xdotool for input simulation

Updated to use the async XTermSession from the terminal_control_mcp package
"""

import asyncio
import base64
from pathlib import Path

from terminal_control_mcp.xterm_session import XTermSession
from terminal_control_mcp.logging_config import setup_logging


async def save_screenshot_from_base64(base64_data: str, filename: str) -> bool:
    """Save base64 encoded screenshot data to file"""
    try:
        image_data = base64.b64decode(base64_data)
        with open(filename, "wb") as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"Failed to save screenshot {filename}: {e}")
        return False


async def main():
    print("Starting htop terminal control example with async XTermSession...")
    
    # Setup logging
    setup_logging(level="INFO", enable_console=True)

    # Create session with larger terminal size for better htop display
    session = XTermSession(command="htop", width=120, height=40)

    try:
        # Start the session (virtual display + xterm)
        print("Starting virtual display and xterm session...")
        await session.start()

        # Wait longer for htop to fully load
        print("Waiting for htop to fully load...")
        await asyncio.sleep(3)

        # Take initial screenshot
        print("Taking initial screenshot...")
        try:
            screenshot_data = await session.capture_screenshot()
            if await save_screenshot_from_base64(screenshot_data["image_data"], "htop_initial.png"):
                print("✓ Initial screenshot saved: htop_initial.png")
                print(f"  Metadata: {screenshot_data['metadata']}")
            else:
                print("✗ Failed to save initial screenshot")
        except Exception as e:
            print(f"✗ Failed to capture initial screenshot: {e}")

        # Press F3 for search
        print("\nPressing F3 (search)...")
        await session.send_key("F3")
        await asyncio.sleep(2)  # Give more time for search dialog to appear

        # Take screenshot after F3
        print("Taking search dialog screenshot...")
        try:
            screenshot_data = await session.capture_screenshot()
            if await save_screenshot_from_base64(screenshot_data["image_data"], "htop_search.png"):
                print("✓ Search dialog screenshot saved: htop_search.png")
            else:
                print("✗ Failed to save search screenshot")
        except Exception as e:
            print(f"✗ Failed to capture search screenshot: {e}")

        # Type search term
        print("\nTyping 'python'...")
        await session.send_text("python")
        await asyncio.sleep(2)  # Give more time for text to appear

        # Take final screenshot
        print("Taking final screenshot...")
        try:
            screenshot_data = await session.capture_screenshot()
            if await save_screenshot_from_base64(screenshot_data["image_data"], "htop_search_term.png"):
                print("✓ Final screenshot saved: htop_search_term.png")
            else:
                print("✗ Failed to save final screenshot")
        except Exception as e:
            print(f"✗ Failed to capture final screenshot: {e}")

        # Press Escape to close search
        print("\nClosing search dialog...")
        await session.send_key("Escape")
        await asyncio.sleep(0.5)

        # Quit htop
        print("Quitting htop...")
        await session.send_key("q")
        await asyncio.sleep(0.5)

        print("\nDone! Check the PNG files for visual screenshots.")

        # List generated files
        for filename in ["htop_initial.png", "htop_search.png", "htop_search_term.png"]:
            if Path(filename).exists():
                size = Path(filename).stat().st_size
                print(f"  {filename}: {size} bytes")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up session...")
        await session.cleanup()
        print("Cleanup completed")


if __name__ == "__main__":
    asyncio.run(main())
