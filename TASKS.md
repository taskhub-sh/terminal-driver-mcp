# Terminal Control MCP - Implementation Tasks

## Overview
This file contains tasks for implementing the minimal viable product (MVP) of the Terminal Control MCP server using the xterm + Xvfb approach. Each task is designed to provide sufficient context for an LLM coding agent to implement independently.

## Implementation Approach
Based on `examples/example_htop.py`, the system uses:
- **Xvfb**: Virtual X11 display for headless operation
- **xterm**: Terminal emulator within the virtual display
- **xdotool**: Input simulation and window management
- **ImageMagick**: PNG screenshot capture

## Core Implementation Tasks

### 1. Project Structure & Dependencies
- [ ] Set up basic Python project structure with proper package organization
- [ ] Configure pyproject.toml with required dependencies (FastMCP, asyncio, subprocess for system calls)
- [ ] Create main module structure: `terminal_control_mcp/` with `__init__.py`, `server.py`, `xterm_session.py`
- [ ] Set up basic logging configuration for debugging and monitoring
- [ ] Ensure system dependencies: Xvfb, xterm, xdotool, ImageMagick (import command)

### 2. MCP Server Foundation
- [ ] Implement basic FastMCP server setup in `server.py` with proper initialization
- [ ] Register core MCP tools: `terminal_launch`, `terminal_input`, `terminal_capture`, `terminal_close`
- [ ] Add basic error handling and logging for MCP operations
- [ ] Implement server startup and shutdown procedures with proper cleanup

### 3. XTerm Session Management
- [ ] Create `XTermSession` class in `xterm_session.py` based on example_htop.py pattern
- [ ] Implement virtual display creation using Xvfb with configurable resolution
- [ ] Add xterm process spawning with customizable commands and geometry
- [ ] Implement window ID detection using xdotool search methods
- [ ] Add session tracking with unique IDs and state management (active, closed, error)
- [ ] Implement proper cleanup with Xvfb and xterm process termination

### 4. Core MCP Tools Implementation
- [ ] Implement `terminal_launch` tool: create Xvfb display and spawn xterm with specified command
- [ ] Implement `terminal_input` tool: send keyboard input using xdotool key/type commands
- [ ] Implement `terminal_capture` tool: take PNG screenshots using ImageMagick import
- [ ] Implement `terminal_close` tool: cleanup Xvfb and xterm processes with proper termination

### 5. Screen Capture & Visual Output
- [ ] Implement PNG screenshot capture using ImageMagick import command
- [ ] Add screenshot file management (temporary files, cleanup)
- [ ] Create base64 encoding for returning images via MCP
- [ ] Add screenshot metadata (timestamp, dimensions, file size)
- [ ] Return structured screen data (image data, metadata, session info)

### 6. Input Handling
- [ ] Implement xdotool-based keyboard input for alphanumeric characters using `type` command
- [ ] Add support for special keys using xdotool `key` command (Return, Tab, Escape, arrows, function keys)
- [ ] Handle control sequences (Ctrl+C, Ctrl+D, etc.) using xdotool key combinations
- [ ] Add window focus management before sending input
- [ ] Add input validation and error handling for invalid key sequences

### 7. Error Handling & Recovery
- [ ] Implement comprehensive error handling for all MCP tools
- [ ] Add proper exception handling for subprocess failures (Xvfb, xterm, xdotool)
- [ ] Handle window ID detection failures with multiple search strategies
- [ ] Create error recovery mechanisms for display and session failures
- [ ] Return structured error responses with helpful debugging information

### 8. Basic Testing & Validation
- [ ] Create simple test script to validate MCP server functionality
- [ ] Test Xvfb display creation and xterm launching
- [ ] Validate PNG screenshot capture with simple commands (ls, echo)
- [ ] Test xdotool input simulation with various key types
- [ ] Test session cleanup and resource deallocation
- [ ] Validate error handling with invalid commands and display failures

## MVP Success Criteria

The MVP should demonstrate:
- [ ] Launch a virtual X11 display and xterm session with specified commands
- [ ] Send keyboard input using xdotool to interact with running programs
- [ ] Capture and return terminal screen content as PNG screenshots
- [ ] Handle multiple concurrent virtual display sessions
- [ ] Provide clear error messages for debugging display and input issues

## Notes for Implementation

- **Focus on PNG screenshot capture** - Visual screenshots are the primary output format
- **Use xterm + xdotool for terminal interaction** - Provides reliable X11-based terminal control
- **Follow example_htop.py pattern** - Use the proven XTermSession class structure
- **Handle virtual display lifecycle carefully** - Proper Xvfb startup/cleanup is critical
- **Window ID detection is crucial** - Implement multiple fallback strategies for finding xterm windows
- **Keep sessions simple** - No persistence or advanced state management in MVP
- **Prioritize reliability over features** - Basic functionality that works consistently

## Out of Scope for MVP

- Mouse event handling with xdotool
- Session persistence across server restarts
- OCR text extraction from screenshots
- Advanced xterm configuration and theming
- Performance optimization for many concurrent displays
- Security sandboxing of executed commands
- Multiple shell type support beyond bash
- Display sharing or remote access features