import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import cv2
import numpy as np


class SessionLogger:
    
    def __init__(self, session_name: Optional[str] = None, output_dir: str = "repro"):
        if session_name is None:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
            session_name = f"session_{timestamp}"
        
        self.session_name = session_name
        self.output_dir = Path(output_dir)
        self.session_dir = self.output_dir / session_name
        self.screenshots_dir = self.session_dir / "screenshots"
        
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.start_time = time.time()
        self.actions: List[Dict[str, Any]] = []
        self.anomalies: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "session_name": session_name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_actions": 0,
            "total_anomalies": 0,
            "crashed": False
        }
        
        self.frame_count = 0
        self.screenshot_interval = 10
    
    def log_action(self, action_type: str, action_data: Dict[str, Any], frame: Optional[np.ndarray] = None):
        timestamp = time.time() - self.start_time
        
        action_entry = {
            "timestamp": timestamp,
            "frame_number": self.frame_count,
            "action_type": str(action_type),
            "action_data": action_data
        }
        
        if frame is not None and self.frame_count % self.screenshot_interval == 0:
            screenshot_path = self.screenshots_dir / f"frame_{self.frame_count:06d}.png"
            cv2.imwrite(str(screenshot_path), frame)
            action_entry["screenshot"] = f"screenshots/frame_{self.frame_count:06d}.png"
        
        self.actions.append(action_entry)
        self.frame_count += 1
    
    def log_anomaly(self, anomaly: Dict[str, Any], frame: Optional[np.ndarray] = None):
        timestamp = time.time() - self.start_time
        
        anomaly_entry = {
            "timestamp": timestamp,
            "frame_number": self.frame_count,
            **anomaly
        }
        
        if frame is not None:
            screenshot_path = self.screenshots_dir / f"anomaly_{len(self.anomalies):04d}_frame_{self.frame_count:06d}.png"
            cv2.imwrite(str(screenshot_path), frame)
            anomaly_entry["screenshot"] = f"screenshots/anomaly_{len(self.anomalies):04d}_frame_{self.frame_count:06d}.png"
        
        self.anomalies.append(anomaly_entry)
        print(f"[ANOMALY] {anomaly.get('type', 'unknown')}: {anomaly.get('description', 'No description')}")
    
    def log_crash(self, crash_info: Dict[str, Any]):
        self.metadata["crashed"] = True
        self.metadata["crash_info"] = crash_info
        print(f"[CRASH DETECTED] {crash_info}")
    
    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value
    
    def save_session(self):
        self.metadata["end_time"] = datetime.now().isoformat()
        self.metadata["total_actions"] = len(self.actions)
        self.metadata["total_anomalies"] = len(self.anomalies)
        self.metadata["duration_seconds"] = time.time() - self.start_time
        
        session_data = {
            "metadata": self.metadata,
            "actions": self.actions,
            "anomalies": self.anomalies
        }
        
        replay_path = self.session_dir / "replay.json"
        with open(replay_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        summary_path = self.session_dir / "summary.txt"
        with open(summary_path, 'w') as f:
            f.write(f"Session: {self.session_name}\n")
            f.write(f"Start: {self.metadata['start_time']}\n")
            f.write(f"End: {self.metadata['end_time']}\n")
            f.write(f"Duration: {self.metadata['duration_seconds']:.2f}s\n")
            f.write(f"Total Actions: {self.metadata['total_actions']}\n")
            f.write(f"Total Anomalies: {self.metadata['total_anomalies']}\n")
            f.write(f"Crashed: {self.metadata['crashed']}\n")
            
            if self.anomalies:
                f.write("\nAnomalies:\n")
                for i, anomaly in enumerate(self.anomalies, 1):
                    f.write(f"  {i}. [{anomaly.get('type', 'unknown')}] {anomaly.get('description', 'No description')} at {anomaly['timestamp']:.2f}s\n")
        
        print(f"\nSession saved to: {self.session_dir}")
        print(f"Total actions: {len(self.actions)}")
        print(f"Total anomalies: {len(self.anomalies)}")
        
        return str(replay_path)
    
    def get_session_path(self) -> str:
        return str(self.session_dir)
    
    @staticmethod
    def load_session(session_path: str) -> Dict[str, Any]:
        replay_path = Path(session_path) / "replay.json"
        
        if not replay_path.exists():
            replay_path = Path(session_path)
        
        with open(replay_path, 'r') as f:
            return json.load(f)

