# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Terminal Control MCP server - a Model Context Protocol server that enables AI agents to interact with terminal-based TUI applications through a virtual X11 display approach using Xvfb, xterm, xdotool, and ImageMagick for PNG screenshot capture.

## Development Commands

- **Run main application**: `python main.py`
- **Run example**: `python examples/example_htop.py` (demonstrates full xterm session with htop)
- **Package management**: Uses `uv` package manager with `pyproject.toml` configuration
- **Virtual environment**: `.venv/` directory (activate with `source .venv/bin/activate`)

## Architecture

### Core Components

1. **XTermSession Class** (`examples/example_htop.py`): Reference implementation showing the complete terminal control pattern
   - Virtual X11 display management using Xvfb
   - xterm process spawning with custom geometry and styling
   - Window ID detection using multiple xdotool search strategies
   - Input simulation via xdotool (keyboard and text)
   - PNG screenshot capture using ImageMagick `import` command

2. **System Dependencies**: Requires Xvfb, xterm, xdotool, ImageMagick for headless terminal operation

3. **MCP Server Structure** (planned):
   - FastMCP-based server implementation
   - Tools: `terminal_launch`, `terminal_input`, `terminal_capture`, `terminal_close`
   - PNG screenshot output with base64 encoding for MCP responses

### Implementation Pattern

The system uses a **virtual X11 display approach** rather than direct TTY manipulation:
- Xvfb creates headless virtual display (`:99` default)
- xterm launches within virtual display with configurable geometry
- xdotool provides reliable input simulation and window management
- ImageMagick captures actual PNG screenshots showing real terminal output

### Key Technical Details

- **Window ID Detection**: Multiple fallback strategies in `get_window_id()` method
- **Input Methods**: `send_key()` for special keys, `send_text()` for alphanumeric input
- **Resource Management**: Proper cleanup of Xvfb and xterm processes with timeout handling
- **Screenshot Capture**: Uses `import -window root filename.png` for full display capture

## Development Notes

- The `src/` directory structure is currently empty - main implementation will go in `src/terminal_control_mcp/`
- `examples/example_htop.py` serves as the reference implementation and working proof of concept
- Project uses modern Python packaging with `pyproject.toml` and uv package manager
- System must have X11 tools installed: `apt-get install xvfb xterm xdotool imagemagick`

## Task Management Workflow

- **Mark tasks as completed when finishing a task in TASKS.md**
- **Always run `uv run ruff check --fix` after finishing a task**