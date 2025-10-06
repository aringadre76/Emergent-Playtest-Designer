import time
import numpy as np
import mss
import mss.tools
from PIL import Image
from typing import Optional, Tuple, Dict, Any


class FrameGrabber:
    
    def __init__(self, window_title: Optional[str] = None, region: Optional[Dict[str, int]] = None):
        self.window_title = window_title
        self.region = region
        self.sct = mss.mss()
        self.last_capture_time = 0
        self.fps_cap = 30
        
        if window_title:
            self._find_window_region()
    
    def _find_window_region(self) -> bool:
        try:
            import win32gui
            import win32con
            
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if self.window_title.lower() in title.lower():
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                hwnd = windows[0]
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                
                rect = win32gui.GetWindowRect(hwnd)
                x, y, x2, y2 = rect
                
                self.region = {
                    "top": y,
                    "left": x,
                    "width": x2 - x,
                    "height": y2 - y
                }
                return True
        except ImportError:
            pass
        
        return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        current_time = time.time()
        min_interval = 1.0 / self.fps_cap
        
        if current_time - self.last_capture_time < min_interval:
            time.sleep(min_interval - (current_time - self.last_capture_time))
        
        try:
            if self.region:
                monitor = self.region
            else:
                monitor = self.sct.monitors[1]
            
            screenshot = self.sct.grab(monitor)
            
            frame = np.array(screenshot)
            frame = frame[:, :, :3]
            
            self.last_capture_time = time.time()
            return frame
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def get_frame_as_pil(self) -> Optional[Image.Image]:
        frame = self.capture_frame()
        if frame is not None:
            return Image.fromarray(frame)
        return None
    
    def set_fps_cap(self, fps: int):
        self.fps_cap = max(1, min(fps, 60))
    
    def get_region_info(self) -> Dict[str, Any]:
        return {
            "window_title": self.window_title,
            "region": self.region,
            "fps_cap": self.fps_cap
        }
    
    def close(self):
        self.sct.close()

