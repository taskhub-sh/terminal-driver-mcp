#!/usr/bin/env python3
"""Main entry point for Terminal Control MCP Server"""

import os
import signal
import sys
import atexit
import asyncio

from terminal_control_mcp.logging_config import setup_logging
from terminal_control_mcp.server import mcp, sessions, cleanup_all_sessions


def main():
    """Main entry point"""
    
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")  # Optional log file path
    
    setup_logging(
        level=log_level,
        log_file=log_file,
        enable_console=True
    )
    
    mcp.run()
    
if __name__ == "__main__":
    main()
