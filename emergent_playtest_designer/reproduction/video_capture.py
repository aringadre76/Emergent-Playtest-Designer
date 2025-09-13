"""Video capture for exploit reproduction."""

import os
import cv2
import numpy as np
from typing import List, Optional, Tuple
from loguru import logger
from ..core.types import GameState, ActionSequence


class VideoCapture:
    """Captures video and screenshots of exploits."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize video capture."""
        self.config = config
        self.fps = config.get("fps", 30)
        self.resolution = config.get("resolution", (1920, 1080))
        self.codec = config.get("codec", "mp4v")
        self.quality = config.get("quality", 90)
        
    def capture_exploit_video(self, action_sequence: ActionSequence, 
                            game_states: List[GameState], output_path: str) -> None:
        """Capture video of exploit reproduction."""
        logger.info(f"Capturing video: {output_path}")
        
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        video_writer = cv2.VideoWriter(
            output_path,
            fourcc,
            self.fps,
            self.resolution
        )
        
        try:
            for i, state in enumerate(game_states):
                frame = self._generate_frame(state, i)
                video_writer.write(frame)
            
            video_writer.release()
            logger.info(f"Video captured successfully: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to capture video: {e}")
            video_writer.release()
            if os.path.exists(output_path):
                os.remove(output_path)
            raise
    
    def capture_screenshot(self, state: GameState, output_path: str) -> None:
        """Capture screenshot of game state."""
        try:
            frame = self._generate_frame(state, 0)
            cv2.imwrite(output_path, frame)
            logger.debug(f"Screenshot captured: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    def _generate_frame(self, state: GameState, frame_index: int) -> np.ndarray:
        """Generate frame from game state."""
        frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        self._draw_background(frame)
        self._draw_player(frame, state)
        self._draw_ui(frame, state)
        self._draw_debug_info(frame, state, frame_index)
        
        return frame
    
    def _draw_background(self, frame: np.ndarray) -> None:
        """Draw background."""
        frame[:] = (50, 50, 50)
        
        for y in range(0, frame.shape[0], 50):
            cv2.line(frame, (0, y), (frame.shape[1], y), (70, 70, 70), 1)
        
        for x in range(0, frame.shape[1], 50):
            cv2.line(frame, (x, 0), (x, frame.shape[0]), (70, 70, 70), 1)
    
    def _draw_player(self, frame: np.ndarray, state: GameState) -> None:
        """Draw player representation."""
        center_x = frame.shape[1] // 2
        center_y = frame.shape[0] // 2
        
        player_x = int(center_x + state.player_position[0] * 10)
        player_y = int(center_y - state.player_position[1] * 10)
        
        player_color = (0, 255, 0) if state.player_health > 0 else (255, 0, 0)
        
        cv2.circle(frame, (player_x, player_y), 10, player_color, -1)
        cv2.circle(frame, (player_x, player_y), 10, (255, 255, 255), 2)
        
        health_text = f"HP: {state.player_health:.1f}"
        cv2.putText(frame, health_text, (player_x - 30, player_y - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _draw_ui(self, frame: np.ndarray, state: GameState) -> None:
        """Draw UI elements."""
        ui_y = 30
        
        for resource_name, value in state.player_resources.items():
            resource_text = f"{resource_name}: {value:.1f}"
            cv2.putText(frame, resource_text, (10, ui_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            ui_y += 25
        
        if state.ui_state:
            for ui_element, ui_value in state.ui_state.items():
                ui_text = f"{ui_element}: {ui_value}"
                cv2.putText(frame, ui_text, (frame.shape[1] - 200, ui_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                ui_y += 20
    
    def _draw_debug_info(self, frame: np.ndarray, state: GameState, frame_index: int) -> None:
        """Draw debug information."""
        debug_y = frame.shape[0] - 100
        
        timestamp_text = f"Time: {state.timestamp:.2f}s"
        cv2.putText(frame, timestamp_text, (10, debug_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        frame_text = f"Frame: {frame_index}"
        cv2.putText(frame, frame_text, (10, debug_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        position_text = f"Pos: ({state.player_position[0]:.1f}, {state.player_position[1]:.1f}, {state.player_position[2]:.1f})"
        cv2.putText(frame, position_text, (10, debug_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if state.physics_state:
            if "velocity" in state.physics_state:
                velocity = state.physics_state["velocity"]
                velocity_text = f"Vel: ({velocity[0]:.1f}, {velocity[1]:.1f}, {velocity[2]:.1f})"
                cv2.putText(frame, velocity_text, (10, debug_y + 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def create_gif(self, frames: List[np.ndarray], output_path: str, 
                   duration: float = 1.0) -> None:
        """Create GIF from frames."""
        try:
            import imageio
            
            gif_frames = []
            for frame in frames:
                gif_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            imageio.mimsave(output_path, gif_frames, duration=duration/len(frames))
            logger.info(f"GIF created: {output_path}")
            
        except ImportError:
            logger.warning("imageio not available, skipping GIF creation")
        except Exception as e:
            logger.error(f"Failed to create GIF: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get video capture statistics."""
        return {
            "fps": self.fps,
            "resolution": self.resolution,
            "codec": self.codec,
            "quality": self.quality
        }
