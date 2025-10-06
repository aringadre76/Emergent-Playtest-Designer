import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
import cv2

from .input_injector import InputInjector, ActionType
from .logger import SessionLogger


class ReplayEngine:
    
    def __init__(self, session_path: str, playback_speed: float = 1.0):
        self.session_path = Path(session_path)
        self.playback_speed = playback_speed
        
        self.session_data = SessionLogger.load_session(str(session_path))
        self.metadata = self.session_data.get("metadata", {})
        self.actions = self.session_data.get("actions", [])
        self.anomalies = self.session_data.get("anomalies", [])
        
        self.input_injector = InputInjector(use_pydirectinput=True)
        self.current_action_index = 0
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"Session Replay: {self.metadata.get('session_name', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Start Time: {self.metadata.get('start_time', 'Unknown')}")
        print(f"Duration: {self.metadata.get('duration_seconds', 0):.2f}s")
        print(f"Total Actions: {self.metadata.get('total_actions', 0)}")
        print(f"Total Anomalies: {self.metadata.get('total_anomalies', 0)}")
        print(f"Crashed: {self.metadata.get('crashed', False)}")
        print(f"Playback Speed: {self.playback_speed}x")
        
        if self.anomalies:
            print(f"\nAnomalies detected:")
            for i, anomaly in enumerate(self.anomalies, 1):
                print(f"  {i}. [{anomaly.get('type', 'unknown')}] at {anomaly.get('timestamp', 0):.2f}s")
                print(f"     {anomaly.get('description', 'No description')}")
        
        print(f"{'='*60}\n")
    
    def replay(self, window_title: Optional[str] = None, delay_before_start: float = 3.0):
        self.print_summary()
        
        if window_title:
            print(f"Target window: {window_title}")
        
        print(f"Replay will start in {delay_before_start} seconds...")
        print("Press Ctrl+C to stop replay at any time.")
        time.sleep(delay_before_start)
        
        print("\nStarting replay...")
        start_time = time.time()
        
        try:
            for i, action in enumerate(self.actions):
                target_timestamp = action["timestamp"] / self.playback_speed
                
                elapsed = time.time() - start_time
                wait_time = target_timestamp - elapsed
                
                if wait_time > 0:
                    time.sleep(wait_time)
                
                action_type_str = action["action_type"]
                action_data = action["action_data"]
                
                if "ActionType." in action_type_str:
                    action_type_str = action_type_str.split(".")[-1]
                
                try:
                    action_type = ActionType[action_type_str.upper()]
                except KeyError:
                    print(f"Warning: Unknown action type: {action_type_str}")
                    continue
                
                self.input_injector.execute_action(action_type, **action_data)
                
                self.current_action_index = i
                
                if (i + 1) % 50 == 0:
                    print(f"Progress: {i + 1}/{len(self.actions)} actions replayed")
        
        except KeyboardInterrupt:
            print("\n\nReplay interrupted by user")
        
        except Exception as e:
            print(f"\n[ERROR] Replay error: {e}")
        
        finally:
            print(f"\nReplay finished. Executed {self.current_action_index + 1}/{len(self.actions)} actions.")
    
    def export_video(self, output_path: Optional[str] = None, fps: int = 10):
        if output_path is None:
            output_path = str(self.session_path / "replay_video.mp4")
        
        screenshot_dir = self.session_path / "screenshots"
        
        if not screenshot_dir.exists():
            print("No screenshots directory found. Cannot create video.")
            return
        
        screenshots = sorted(screenshot_dir.glob("frame_*.png"))
        
        if not screenshots:
            print("No screenshots found. Cannot create video.")
            return
        
        first_frame = cv2.imread(str(screenshots[0]))
        height, width, _ = first_frame.shape
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"Creating video from {len(screenshots)} screenshots...")
        
        for screenshot_path in screenshots:
            frame = cv2.imread(str(screenshot_path))
            if frame is not None:
                video_writer.write(frame)
        
        video_writer.release()
        print(f"Video saved: {output_path}")
    
    def get_action_at_time(self, timestamp: float) -> Optional[Dict[str, Any]]:
        for action in self.actions:
            if action["timestamp"] >= timestamp:
                return action
        return None
    
    def get_anomalies_in_range(self, start_time: float, end_time: float) -> list:
        return [
            anomaly for anomaly in self.anomalies
            if start_time <= anomaly["timestamp"] <= end_time
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "session_name": self.metadata.get("session_name"),
            "total_actions": len(self.actions),
            "total_anomalies": len(self.anomalies),
            "duration": self.metadata.get("duration_seconds", 0),
            "crashed": self.metadata.get("crashed", False),
            "current_progress": self.current_action_index,
            "playback_speed": self.playback_speed
        }

