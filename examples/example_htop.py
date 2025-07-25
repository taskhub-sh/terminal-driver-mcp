#!/usr/bin/env python3
"""
Example script demonstrating terminal control with htop using xterm approach
- Spawns htop in xterm with virtual display
- Presses F3 to search
- Takes actual PNG screenshots
- Uses xdotool for input simulation
"""

import subprocess
import time
import os
from pathlib import Path

class XTermSession:
    """Manage xterm session with virtual X display"""
    
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.display = ":99"
        self.xvfb_proc = None
        self.xterm_proc = None
        
    def start_virtual_display(self):
        """Start Xvfb virtual display"""
        print("Starting virtual X display...")
        self.xvfb_proc = subprocess.Popen([
            'Xvfb', self.display, 
            '-screen', '0', f'{self.width}x{self.height}x24',
            '-dpi', '150',
            '-ac', '+extension', 'GLX'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Wait for display to start
        
    def start_xterm(self, command="bash"):
        """Start xterm with specified command"""
        env = os.environ.copy()
        env['DISPLAY'] = self.display
        
        print(f"Starting xterm with command: {command}")
        self.xterm_proc = subprocess.Popen([
            'xterm',
            '-geometry', '120x40',
            '-fn', '-*-fixed-medium-r-*-*-18-*-*-*-*-*-*-*',
            '-bg', 'black',
            '-fg', 'white',
            '-e', command
        ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Wait for xterm to start
        
    def get_window_id(self):
        """Get the xterm window ID"""
        env = os.environ.copy()
        env['DISPLAY'] = self.display
        
        # Try multiple approaches to find the window
        for search_method in [
            ['xdotool', 'search', '--class', 'XTerm'],
            ['xdotool', 'search', '--name', 'xterm'],
            ['xdotool', 'search', '--class', 'xterm'],
            ['xdotool', 'getactivewindow']  # Get any active window
        ]:
            try:
                result = subprocess.run(search_method, 
                                      env=env, capture_output=True, text=True, check=True)
                window_id = result.stdout.strip().split('\n')[0]
                if window_id:
                    print(f"Found window ID: {window_id} using {' '.join(search_method)}")
                    return window_id
            except subprocess.CalledProcessError:
                continue
        
        # Debug: list all windows
        try:
            result = subprocess.run(['xdotool', 'search', '--onlyvisible', '.'], 
                                  env=env, capture_output=True, text=True)
            print(f"All visible windows: {result.stdout.strip()}")
        except:
            pass
            
        return None
        
    def send_key(self, key):
        """Send key to xterm window using xdotool"""
        env = os.environ.copy()
        env['DISPLAY'] = self.display
        
        window_id = self.get_window_id()
        if window_id:
            print(f"Sending key '{key}' to window {window_id}")
            # Focus the window first
            subprocess.run(['xdotool', 'windowfocus', window_id], env=env, stderr=subprocess.DEVNULL)
            time.sleep(0.2)
            subprocess.run(['xdotool', 'key', '--window', window_id, key], env=env, stderr=subprocess.DEVNULL)
        else:
            print(f"No window found to send key '{key}'")
        
    def send_text(self, text):
        """Send text to xterm window"""
        env = os.environ.copy()
        env['DISPLAY'] = self.display
        
        window_id = self.get_window_id()
        if window_id:
            print(f"Sending text '{text}' to window {window_id}")
            # Focus the window first
            subprocess.run(['xdotool', 'windowfocus', window_id], env=env, stderr=subprocess.DEVNULL)
            time.sleep(0.2)
            subprocess.run(['xdotool', 'type', '--window', window_id, text], env=env, stderr=subprocess.DEVNULL)
        else:
            print(f"No window found to send text '{text}'")
        
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot of the virtual display"""
        env = os.environ.copy()
        env['DISPLAY'] = self.display
        
        print(f"Taking screenshot: {filename}")
        try:
            subprocess.run(['import', '-window', 'root', filename], 
                         env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return Path(filename).exists()
        except subprocess.CalledProcessError:
            print(f"Failed to take screenshot: {filename}")
            return False
        
    def cleanup(self):
        """Clean up processes"""
        if self.xterm_proc:
            self.xterm_proc.terminate()
            try:
                self.xterm_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.xterm_proc.kill()
                
        if self.xvfb_proc:
            self.xvfb_proc.terminate()
            try:
                self.xvfb_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.xvfb_proc.kill()
        
        # Small delay to let X server cleanup
        time.sleep(0.5)

def main():
    print("Starting htop terminal control example with xterm...")
    
    session = XTermSession()
    
    try:
        # Start virtual display
        session.start_virtual_display()
        
        # Start xterm with htop
        session.start_xterm("htop")
        
        # Wait longer for htop to fully load
        print("Waiting for htop to fully load...")
        time.sleep(3)
        
        # Take initial screenshot
        if session.take_screenshot("htop_initial.png"):
            print("✓ Initial screenshot saved: htop_initial.png")
        else:
            print("✗ Failed to take initial screenshot")
        
        # Press F3 for search
        print("\nPressing F3 (search)...")
        session.send_key("F3")
        time.sleep(2)  # Give more time for search dialog to appear
        
        # Take screenshot after F3
        if session.take_screenshot("htop_search.png"):
            print("✓ Search dialog screenshot saved: htop_search.png")
        else:
            print("✗ Failed to take search screenshot")
        
        # Type search term
        print("\nTyping 'python'...")
        session.send_text("python")
        time.sleep(2)  # Give more time for text to appear
        
        # Take final screenshot
        if session.take_screenshot("htop_search_term.png"):
            print("✓ Final screenshot saved: htop_search_term.png")
        else:
            print("✗ Failed to take final screenshot")
        
        # Press Escape to close search
        print("\nClosing search dialog...")
        session.send_key("Escape")
        time.sleep(0.5)
        
        # Quit htop
        print("Quitting htop...")
        session.send_key("q")
        time.sleep(0.5)
        
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
        session.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    main()