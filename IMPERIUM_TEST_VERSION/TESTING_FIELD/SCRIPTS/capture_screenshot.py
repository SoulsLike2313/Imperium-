#!/usr/bin/env python3
"""
capture_screenshot.py - Capture screenshot of active window or full screen.

Usage:
    python capture_screenshot.py [output_path] [--fullscreen]

Requirements:
    pip install pillow pyautogui

Output:
    Screenshot saved to TESTING_FIELD/SCREENSHOTS/ with timestamp.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

def get_output_path(custom_path: str = None) -> Path:
    """Determine output path for screenshot."""
    if custom_path:
        return Path(custom_path)
    
    # Default: TESTING_FIELD/SCREENSHOTS/
    script_dir = Path(__file__).parent.parent
    screenshots_dir = script_dir / "SCREENSHOTS"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return screenshots_dir / f"screenshot_{timestamp}.png"

def capture_screenshot(output_path: Path, fullscreen: bool = False) -> dict:
    """Capture screenshot and return result."""
    result = {
        "success": False,
        "output_path": str(output_path),
        "error": None,
        "method": None
    }
    
    try:
        # Try pyautogui first (cross-platform)
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(str(output_path))
        result["success"] = True
        result["method"] = "pyautogui"
        return result
    except ImportError:
        pass
    except Exception as e:
        result["error"] = f"pyautogui failed: {e}"
    
    try:
        # Fallback: PIL ImageGrab (Windows)
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        screenshot.save(str(output_path))
        result["success"] = True
        result["method"] = "PIL.ImageGrab"
        return result
    except ImportError:
        pass
    except Exception as e:
        result["error"] = f"PIL.ImageGrab failed: {e}"
    
    # No method available
    if not result["error"]:
        result["error"] = "No screenshot library available. Install: pip install pillow pyautogui"
    
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Capture screenshot")
    parser.add_argument("output", nargs="?", help="Output path")
    parser.add_argument("--fullscreen", action="store_true", help="Capture full screen")
    args = parser.parse_args()
    
    output_path = get_output_path(args.output)
    result = capture_screenshot(output_path, args.fullscreen)
    
    if result["success"]:
        print(f"PASS: Screenshot saved to {result['output_path']}")
        print(f"Method: {result['method']}")
        sys.exit(0)
    else:
        print(f"FAIL: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
