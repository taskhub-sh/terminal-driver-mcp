# Terminal Control Examples

This directory contains examples demonstrating terminal control and screenshot capabilities using virtual X displays.

## Dependencies

To run these examples on Linux, you need to install the following packages:

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install xvfb xterm xdotool imagemagick
```

### CentOS/RHEL/Fedora:
```bash
# For CentOS/RHEL with yum:
sudo yum install xorg-x11-server-Xvfb xterm xdotool ImageMagick

# For Fedora with dnf:
sudo dnf install xorg-x11-server-Xvfb xterm xdotool ImageMagick
```

### Arch Linux:
```bash
sudo pacman -S xorg-server-xvfb xterm xdotool imagemagick
```

## Package Descriptions

- **xvfb** (X Virtual Framebuffer): Creates a virtual X display for headless operation
- **xterm**: Terminal emulator used to run applications
- **xdotool**: Command-line tool for simulating keyboard input and mouse activity
- **imagemagick**: Provides the `import` command for taking screenshots

## Examples

### example_htop.py

Demonstrates terminal control with htop:
- Spawns htop in a virtual X display
- Takes high-resolution screenshots (1920x1080 @ 150 DPI)
- Simulates keyboard input (F3 for search, typing "python")
- Saves PNG screenshots at different interaction stages

**Usage:**
```bash
python example_htop.py
```

**Output:**
- `htop_initial.png`: Initial htop view
- `htop_search.png`: Search dialog activated
- `htop_search_term.png`: Search results for "python"

## Features

- High-resolution screenshot capture
- Virtual X display for headless operation
- Keyboard and text input simulation
- Process cleanup and error handling
- Cross-platform Linux compatibility