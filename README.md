# Terminal Control MCP

A Model Context Protocol (MCP) server that enables AI agents to interact with terminal-based TUI applications through a virtual X11 display approach.

<a href="https://glama.ai/mcp/servers/@taskhub-sh/terminal-driver-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@taskhub-sh/terminal-driver-mcp/badge" alt="Terminal Control MCP server" />
</a>

## Overview

This project provides a comprehensive solution for controlling terminal applications programmatically using:
- **Xvfb** for headless virtual X11 display
- **xterm** for terminal emulation
- **xdotool** for input simulation and window management
- **ImageMagick** for PNG screenshot capture

The system captures actual visual terminal output as PNG screenshots, making it ideal for AI agents that need to see and interact with terminal applications.

## Features

- **Virtual Display Management**: Headless X11 display using Xvfb
- **Input Simulation**: Send keyboard input and text to terminal applications
- **Screenshot Capture**: Take PNG screenshots of terminal output
- **Window Management**: Reliable window detection and focus handling
- **Resource Cleanup**: Proper process management with timeout handling

## System Requirements

The following system packages must be installed:

```bash
# Ubuntu/Debian
sudo apt-get install xvfb xterm xdotool imagemagick

# CentOS/RHEL/Fedora
sudo yum install xorg-x11-server-Xvfb xterm xdotool ImageMagick
```

## Installation

This project uses the `uv` package manager:

```bash
# Clone the repository
git clone <repository-url>
cd terminal-control-mcp

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

## Quick Start

### Running the Example

Try the included htop example to see the system in action:

```bash
python examples/example_htop.py
```

This will:
1. Launch htop in a virtual xterm session
2. Press F3 to open the search dialog
3. Type "python" as a search term
4. Capture PNG screenshots at each step
5. Clean up all processes

### Basic Usage

```python
from examples.example_htop import XTermSession

# Create a session
session = XTermSession(width=1920, height=1080)

try:
    # Start virtual display and terminal
    session.start_virtual_display()
    session.start_xterm("your-command-here")
    
    # Take a screenshot
    session.take_screenshot("output.png")
    
    # Send input
    session.send_key("F1")
    session.send_text("hello world")
    
finally:
    session.cleanup()
```

## Architecture

### Core Components

1. **XTermSession Class**: The main interface for terminal control
   - Manages Xvfb virtual display lifecycle
   - Spawns and controls xterm processes
   - Handles input simulation via xdotool
   - Captures screenshots using ImageMagick

2. **Virtual Display Approach**: Unlike direct TTY manipulation, this system:
   - Creates a real X11 environment with Xvfb
   - Launches actual xterm instances
   - Captures genuine visual output as PNG files
   - Provides reliable input simulation

### Key Methods

- `start_virtual_display()`: Initialize Xvfb virtual display
- `start_xterm(command)`: Launch xterm with specified command
- `send_key(key)`: Send special keys (F1, Escape, etc.)
- `send_text(text)`: Send alphanumeric text input
- `take_screenshot(filename)`: Capture PNG screenshot
- `cleanup()`: Properly terminate all processes

## Development

### Project Structure

```
terminal-control-mcp/
├── src/terminal_control_mcp/    # Main MCP server implementation (planned)
├── examples/
│   ├── example_htop.py         # Reference implementation
│   └── README.md
├── tests/                      # Test suite
├── pyproject.toml             # Project configuration
└── CLAUDE.md                  # Development guidelines
```

### Development Commands

```bash
# Run the main application
python main.py

# Run the htop example
python examples/example_htop.py

# Activate virtual environment
source .venv/bin/activate
```

### MCP Server Implementation (Planned)

The full MCP server will provide these tools:
- `terminal_launch`: Start a new terminal session
- `terminal_input`: Send keyboard/text input
- `terminal_capture`: Take PNG screenshot
- `terminal_close`: Clean up terminal session

## Technical Details

### Window Detection

The system uses multiple fallback strategies for reliable window ID detection:

```python
search_methods = [
    ['xdotool', 'search', '--class', 'XTerm'],
    ['xdotool', 'search', '--name', 'xterm'],
    ['xdotool', 'search', '--class', 'xterm'],
    ['xdotool', 'getactivewindow']
]
```

### Screenshot Capture

Uses ImageMagick's `import` command for reliable PNG capture:

```python
subprocess.run(['import', '-window', 'root', filename], env=env)
```

### Resource Management

Implements proper cleanup with timeout handling:

```python
def cleanup(self):
    if self.xterm_proc:
        self.xterm_proc.terminate()
        try:
            self.xterm_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.xterm_proc.kill()
```

## Contributing

[TBD]