import time
import random
from typing import Optional, Dict, Any
import psutil
import numpy as np

from .frame_grabber import FrameGrabber
from .input_injector import InputInjector, ActionType
from .analyzer import Analyzer
from .logger import SessionLogger


class Agent:
    
    def __init__(
        self,
        window_title: str,
        session_name: Optional[str] = None,
        fps: int = 10,
        max_steps: int = 1000
    ):
        self.window_title = window_title
        self.max_steps = max_steps
        self.current_step = 0
        
        self.frame_grabber = FrameGrabber(window_title=window_title)
        self.frame_grabber.set_fps_cap(fps)
        
        self.input_injector = InputInjector(use_pydirectinput=True)
        self.analyzer = Analyzer(ssim_threshold=0.95, softlock_threshold=30)
        self.logger = SessionLogger(session_name=session_name)
        
        self.game_process = None
        self.running = False
        
        self.logger.set_metadata("window_title", window_title)
        self.logger.set_metadata("max_steps", max_steps)
        self.logger.set_metadata("fps", fps)
    
    def _find_game_process(self) -> Optional[psutil.Process]:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if self.window_title.lower() in proc.info['name'].lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def _check_game_alive(self) -> bool:
        if self.game_process is None:
            return True
        
        try:
            return self.game_process.is_running()
        except:
            return False
    
    def decide_action(self, frame: np.ndarray, analysis: Dict[str, Any]) -> tuple:
        raise NotImplementedError("Subclasses must implement decide_action")
    
    def run(self):
        print(f"Starting agent for window: {self.window_title}")
        print(f"Session: {self.logger.session_name}")
        print(f"Max steps: {self.max_steps}")
        
        self.game_process = self._find_game_process()
        
        time.sleep(2)
        
        self.running = True
        
        try:
            while self.running and self.current_step < self.max_steps:
                if not self._check_game_alive():
                    print("\n[CRASH] Game process terminated!")
                    self.logger.log_crash({
                        "reason": "Process terminated",
                        "step": self.current_step
                    })
                    break
                
                frame = self.frame_grabber.capture_frame()
                
                if frame is None:
                    print("Warning: Failed to capture frame")
                    time.sleep(0.5)
                    continue
                
                analysis = self.analyzer.analyze_frame(frame)
                
                if analysis["anomalies"]:
                    for anomaly in analysis["anomalies"]:
                        self.logger.log_anomaly(anomaly, frame)
                
                action_type, action_data = self.decide_action(frame, analysis)
                
                self.input_injector.execute_action(action_type, **action_data)
                
                self.logger.log_action(
                    action_type=action_type,
                    action_data=action_data,
                    frame=frame
                )
                
                self.current_step += 1
                
                if self.current_step % 100 == 0:
                    print(f"Step {self.current_step}/{self.max_steps} - Anomalies: {len(self.logger.anomalies)}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.logger.log_crash({
                "reason": str(e),
                "step": self.current_step
            })
        
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        print("\nStopping agent...")
        
        replay_path = self.logger.save_session()
        
        self.frame_grabber.close()
        
        print(f"Replay saved: {replay_path}")
        print("Agent stopped.")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "session_path": self.logger.get_session_path(),
            "total_anomalies": len(self.logger.anomalies),
            "analyzer_stats": self.analyzer.get_stats()
        }


class RandomAgent(Agent):
    
    def __init__(
        self,
        window_title: str,
        session_name: Optional[str] = None,
        fps: int = 10,
        max_steps: int = 1000,
        action_keys: Optional[list] = None
    ):
        super().__init__(window_title, session_name, fps, max_steps)
        
        if action_keys is None:
            self.action_keys = ['w', 'a', 's', 'd', 'space', 'left', 'right', 'up', 'down']
        else:
            self.action_keys = action_keys
        
        self.logger.set_metadata("agent_type", "random")
        self.logger.set_metadata("action_keys", self.action_keys)
    
    def decide_action(self, frame: np.ndarray, analysis: Dict[str, Any]) -> tuple:
        action_choice = random.choice(['key_press', 'key_tap', 'wait'])
        
        if action_choice == 'key_press':
            key = random.choice(self.action_keys)
            duration = random.uniform(0.05, 0.3)
            return ActionType.KEY_PRESS, {'key': key, 'duration': duration}
        
        elif action_choice == 'key_tap':
            key = random.choice(self.action_keys)
            return ActionType.KEY_TAP, {'key': key}
        
        else:
            duration = random.uniform(0.1, 0.5)
            return ActionType.WAIT, {'duration': duration}

