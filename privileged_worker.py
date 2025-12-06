#!/usr/bin/env python3
"""
Privileged worker subprocess that handles screenshots and input simulation.
This script should be run with elevated privileges (sudo) to access input devices.
"""

import sys
import json
import base64
import io
import time
from typing import Dict, Any, Optional
import mss
from PIL import Image
import pynput
from pynput import mouse, keyboard


class PrivilegedWorker:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.screenshot_tool = mss.mss()
        self.listener = None
        self.safety_mode_active = False  # When True, reject all requests
        self.f9_press_start = None
        self.long_press_duration = 2.0  # 2 seconds for long press
        
    def setup_key_listener(self):
        """Setup keyboard listener to detect F9 key events."""
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    if self.f9_press_start is None:
                        self.f9_press_start = time.time()
            except AttributeError:
                pass
                
        def on_release(key):
            try:
                if key == keyboard.Key.f9:
                    if self.f9_press_start is not None:
                        press_duration = time.time() - self.f9_press_start
                        if press_duration >= self.long_press_duration:
                            # Long press detected - toggle safety mode OFF
                            self.safety_mode_active = False
                        else:
                            # Short press - activate safety mode
                            self.safety_mode_active = True
                        self.f9_press_start = None
            except AttributeError:
                pass
                
        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
    
    def is_safe_mode_active(self) -> bool:
        """Check if safety mode is active (F9 was pressed but not long-pressed again)."""
        return self.safety_mode_active
    
    def screenshot(self) -> Dict[str, Any]:
        """Take a screenshot and return it as base64 encoded PNG."""
        try:
            # Capture entire screen
            monitor = self.screenshot_tool.monitors[1]  # Primary monitor
            screenshot = self.screenshot_tool.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return {
                "success": True,
                "image": img_base64,
                "width": screenshot.width,
                "height": screenshot.height
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        """Move mouse to coordinates (x, y)."""
        try:
            self.mouse_controller.position = (x, y)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_button_down(self, button: str) -> Dict[str, Any]:
        """Press mouse button down."""
        try:
            btn_map = {
                "left": mouse.Button.left,
                "right": mouse.Button.right,
                "middle": mouse.Button.middle
            }
            if button not in btn_map:
                return {"success": False, "error": f"Invalid button: {button}"}
            self.mouse_controller.press(btn_map[button])
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_button_up(self, button: str) -> Dict[str, Any]:
        """Release mouse button."""
        try:
            btn_map = {
                "left": mouse.Button.left,
                "right": mouse.Button.right,
                "middle": mouse.Button.middle
            }
            if button not in btn_map:
                return {"success": False, "error": f"Invalid button: {button}"}
            self.mouse_controller.release(btn_map[button])
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """Click at coordinates (x, y)."""
        try:
            # Move to position
            self.mouse_controller.position = (x, y)
            # Click
            btn_map = {
                "left": mouse.Button.left,
                "right": mouse.Button.right,
                "middle": mouse.Button.middle
            }
            if button not in btn_map:
                return {"success": False, "error": f"Invalid button: {button}"}
            self.mouse_controller.click(btn_map[button], 1)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_drag_drop(self, x: int, y: int, x_drop: int, y_drop: int, 
                       button: str = "left") -> Dict[str, Any]:
        """Drag from (x, y) to (x_drop, y_drop)."""
        try:
            btn_map = {
                "left": mouse.Button.left,
                "right": mouse.Button.right,
                "middle": mouse.Button.middle
            }
            if button not in btn_map:
                return {"success": False, "error": f"Invalid button: {button}"}
            
            # Move to start position
            self.mouse_controller.position = (x, y)
            # Press button
            self.mouse_controller.press(btn_map[button])
            # Move to drop position
            self.mouse_controller.position = (x_drop, y_drop)
            # Release button
            self.mouse_controller.release(btn_map[button])
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def key_press(self, key: str) -> Dict[str, Any]:
        """Press a key."""
        try:
            # Handle special keys
            key_map = {
                "page_up": keyboard.Key.page_up,
                "page_down": keyboard.Key.page_down,
                "home": keyboard.Key.home,
                "end": keyboard.Key.end,
                "up": keyboard.Key.up,
                "down": keyboard.Key.down,
                "left": keyboard.Key.left,
                "right": keyboard.Key.right,
                "enter": keyboard.Key.enter,
                "tab": keyboard.Key.tab,
                "escape": keyboard.Key.esc,
                "backspace": keyboard.Key.backspace,
                "delete": keyboard.Key.delete,
                "space": keyboard.Key.space,
            }
            
            if key.lower() in key_map:
                self.keyboard_controller.press(key_map[key.lower()])
                self.keyboard_controller.release(key_map[key.lower()])
            elif len(key) == 1:
                # Single character
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            else:
                return {"success": False, "error": f"Invalid key: {key}"}
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def key_type(self, text: str) -> Dict[str, Any]:
        """Type a string."""
        try:
            self.keyboard_controller.type(text)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status including safety mode."""
        return {
            "success": True,
            "safe_mode_active": self.is_safe_mode_active(),
            "mouse_position": self.mouse_controller.position
        }
    
    def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process a command from the FastAPI server."""
        # Check safety mode first (except for status check)
        if command.get("action") != "status" and self.is_safe_mode_active():
            return {
                "success": False,
                "error": "Safety mode active: F9 was pressed. Long-press F9 again to disable."
            }
        
        action = command.get("action")
        
        if action == "screenshot":
            return self.screenshot()
        elif action == "mouse_move":
            return self.mouse_move(command["x"], command["y"])
        elif action == "mouse_button_down":
            return self.mouse_button_down(command["button"])
        elif action == "mouse_button_up":
            return self.mouse_button_up(command["button"])
        elif action == "mouse_click":
            return self.mouse_click(command["x"], command["y"], command.get("button", "left"))
        elif action == "mouse_drag_drop":
            return self.mouse_drag_drop(
                command["x"], command["y"],
                command["x_drop"], command["y_drop"],
                command.get("button", "left")
            )
        elif action == "key_press":
            return self.key_press(command["key"])
        elif action == "key_type":
            return self.key_type(command["text"])
        elif action == "status":
            return self.get_status()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


def main():
    """Main loop: read commands from stdin, execute, write results to stdout."""
    worker = PrivilegedWorker()
    worker.setup_key_listener()
    
    try:
        for line in sys.stdin:
            try:
                command = json.loads(line.strip())
                result = worker.process_command(command)
                print(json.dumps(result), flush=True)
            except json.JSONDecodeError as e:
                error_result = {"success": False, "error": f"Invalid JSON: {str(e)}"}
                print(json.dumps(error_result), flush=True)
            except Exception as e:
                error_result = {"success": False, "error": f"Error processing command: {str(e)}"}
                print(json.dumps(error_result), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        if worker.listener:
            worker.listener.stop()


if __name__ == "__main__":
    main()

