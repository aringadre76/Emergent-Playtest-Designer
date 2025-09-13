"""Unity game controller for headless execution and management."""

import subprocess
import time
import threading
import queue
from typing import Optional, Dict, Any, List, Callable
from loguru import logger
from ..core.types import GameState, Action
from ..core.config import UnityConfig


class UnityController:
    """Controls Unity game execution in headless mode."""
    
    def __init__(self, config: UnityConfig):
        """Initialize Unity controller."""
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.state_queue: queue.Queue = queue.Queue()
        self.action_queue: queue.Queue = queue.Queue()
        self.callbacks: List[Callable] = []
        self._monitor_thread: Optional[threading.Thread] = None
        
    def start_game(self, game_path: str) -> bool:
        """Start Unity game in headless mode."""
        try:
            cmd = [
                self.config.executable_path,
                "-batchmode",
                "-quit",
                "-projectPath", self.config.project_path,
                "-executeMethod", "PlaytestDesigner.StartHeadlessMode",
                "-logFile", "unity_log.txt",
            ]
            
            if self.config.headless_mode:
                cmd.extend(["-nographics"])
            
            logger.info(f"Starting Unity game: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            self._start_monitoring()
            
            logger.info("Unity game started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Unity game: {e}")
            return False
    
    def stop_game(self) -> bool:
        """Stop Unity game."""
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                self.is_running = False
                logger.info("Unity game stopped")
                return True
                
        except Exception as e:
            logger.error(f"Error stopping Unity game: {e}")
            return False
    
    def is_game_running(self) -> bool:
        """Check if game is currently running."""
        if self.process is None:
            return False
        
        return self.process.poll() is None and self.is_running
    
    def send_action(self, action: Action) -> bool:
        """Send action to Unity game."""
        try:
            if not self.is_game_running():
                logger.warning("Cannot send action: game is not running")
                return False
            
            action_data = {
                "type": action.action_type,
                "parameters": action.parameters,
                "timestamp": action.timestamp,
                "duration": action.duration,
            }
            
            self.action_queue.put(action_data)
            logger.debug(f"Action sent: {action.action_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send action: {e}")
            return False
    
    def get_game_state(self) -> Optional[GameState]:
        """Get current game state."""
        try:
            if not self.state_queue.empty():
                state_data = self.state_queue.get_nowait()
                return self._parse_game_state(state_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get game state: {e}")
            return None
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback for state updates."""
        self.callbacks.append(callback)
    
    def _start_monitoring(self) -> None:
        """Start monitoring Unity process."""
        self._monitor_thread = threading.Thread(
            target=self._monitor_process,
            daemon=True
        )
        self._monitor_thread.start()
    
    def _monitor_process(self) -> None:
        """Monitor Unity process output."""
        while self.is_running and self.process:
            try:
                if self.process.poll() is not None:
                    logger.warning("Unity process terminated unexpectedly")
                    self.is_running = False
                    break
                
                line = self.process.stdout.readline()
                if line:
                    self._process_output_line(line.strip())
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error monitoring Unity process: {e}")
                break
    
    def _process_output_line(self, line: str) -> None:
        """Process output line from Unity."""
        try:
            if line.startswith("STATE:"):
                state_data = self._parse_state_line(line[6:])
                self.state_queue.put(state_data)
                
                for callback in self.callbacks:
                    try:
                        callback(state_data)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                        
            elif line.startswith("ERROR:"):
                logger.error(f"Unity error: {line[6:]}")
                
            elif line.startswith("LOG:"):
                logger.info(f"Unity log: {line[4:]}")
                
        except Exception as e:
            logger.error(f"Error processing output line: {e}")
    
    def _parse_state_line(self, state_line: str) -> Dict[str, Any]:
        """Parse state line from Unity."""
        import json
        try:
            return json.loads(state_line)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse state line: {state_line}")
            return {}
    
    def _parse_game_state(self, state_data: Dict[str, Any]) -> GameState:
        """Parse state data into GameState object."""
        return GameState(
            timestamp=state_data.get("timestamp", time.time()),
            player_position=tuple(state_data.get("player_position", [0, 0, 0])),
            player_health=state_data.get("player_health", 100.0),
            player_resources=state_data.get("player_resources", {}),
            game_objects=state_data.get("game_objects", {}),
            physics_state=state_data.get("physics_state", {}),
            ui_state=state_data.get("ui_state", {}),
            custom_metrics=state_data.get("custom_metrics", {}),
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get Unity performance metrics."""
        if not self.process:
            return {}
        
        try:
            import psutil
            process = psutil.Process(self.process.pid)
            
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "threads": process.num_threads(),
                "status": process.status(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def __del__(self):
        """Cleanup on destruction."""
        if self.is_running:
            self.stop_game()
