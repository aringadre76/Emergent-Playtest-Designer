"""Reproduction generation for exploits."""

import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import ExploitReport, ActionSequence, GameState, Action
from .video_capture import VideoCapture
from .test_case_generator import TestCaseGenerator


@dataclass
class ReproductionData:
    """Represents reproduction data for an exploit."""
    exploit_id: str
    reproduction_steps: List[str]
    action_sequence: ActionSequence
    game_states: List[GameState]
    video_path: Optional[str] = None
    screenshots: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.screenshots is None:
            self.screenshots = []
        if self.metadata is None:
            self.metadata = {}


class ReproductionGenerator:
    """Generates reproducible test cases for exploits."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize reproduction generator."""
        self.config = config
        self.output_dir = config.get("output_dir", "reproductions")
        self.video_capture = VideoCapture(config.get("video_config", {}))
        self.test_case_generator = TestCaseGenerator(config.get("test_case_config", {}))
        
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_reproduction(self, exploit_report: ExploitReport) -> ReproductionData:
        """Generate reproduction data for an exploit."""
        logger.info(f"Generating reproduction for exploit {exploit_report.exploit_id}")
        
        reproduction_data = ReproductionData(
            exploit_id=exploit_report.exploit_id,
            reproduction_steps=exploit_report.reproduction_steps,
            action_sequence=exploit_report.action_sequence,
            game_states=exploit_report.game_states,
            metadata={
                "exploit_type": exploit_report.exploit_type.value,
                "severity": exploit_report.severity.value,
                "confidence": exploit_report.confidence_score,
                "discovery_time": exploit_report.discovery_time
            }
        )
        
        self._generate_video(reproduction_data)
        self._generate_screenshots(reproduction_data)
        self._generate_test_case(reproduction_data)
        self._save_reproduction_data(reproduction_data)
        
        logger.info(f"Reproduction generated successfully for exploit {exploit_report.exploit_id}")
        return reproduction_data
    
    def _generate_video(self, reproduction_data: ReproductionData) -> None:
        """Generate video of the exploit."""
        if not self.config.get("generate_video", True):
            return
        
        try:
            video_path = os.path.join(
                self.output_dir,
                f"exploit_{reproduction_data.exploit_id}_video.mp4"
            )
            
            self.video_capture.capture_exploit_video(
                reproduction_data.action_sequence,
                reproduction_data.game_states,
                video_path
            )
            
            reproduction_data.video_path = video_path
            logger.info(f"Video generated: {video_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
    
    def _generate_screenshots(self, reproduction_data: ReproductionData) -> None:
        """Generate screenshots of key moments."""
        if not self.config.get("generate_screenshots", True):
            return
        
        try:
            screenshots = []
            
            for i, state in enumerate(reproduction_data.game_states):
                if i % 5 == 0:
                    screenshot_path = os.path.join(
                        self.output_dir,
                        f"exploit_{reproduction_data.exploit_id}_screenshot_{i}.png"
                    )
                    
                    self.video_capture.capture_screenshot(state, screenshot_path)
                    screenshots.append(screenshot_path)
            
            reproduction_data.screenshots = screenshots
            logger.info(f"Generated {len(screenshots)} screenshots")
            
        except Exception as e:
            logger.error(f"Failed to generate screenshots: {e}")
    
    def _generate_test_case(self, reproduction_data: ReproductionData) -> None:
        """Generate automated test case."""
        try:
            test_case_path = os.path.join(
                self.output_dir,
                f"exploit_{reproduction_data.exploit_id}_test_case.py"
            )
            
            test_case_content = self.test_case_generator.generate_test_case(reproduction_data)
            
            with open(test_case_path, 'w') as f:
                f.write(test_case_content)
            
            logger.info(f"Test case generated: {test_case_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate test case: {e}")
    
    def _save_reproduction_data(self, reproduction_data: ReproductionData) -> None:
        """Save reproduction data to JSON file."""
        try:
            data_path = os.path.join(
                self.output_dir,
                f"exploit_{reproduction_data.exploit_id}_data.json"
            )
            
            data = {
                "exploit_id": reproduction_data.exploit_id,
                "reproduction_steps": reproduction_data.reproduction_steps,
                "action_sequence": reproduction_data.action_sequence.to_dict(),
                "game_states": [state.to_dict() for state in reproduction_data.game_states],
                "video_path": reproduction_data.video_path,
                "screenshots": reproduction_data.screenshots,
                "metadata": reproduction_data.metadata
            }
            
            with open(data_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Reproduction data saved: {data_path}")
            
        except Exception as e:
            logger.error(f"Failed to save reproduction data: {e}")
    
    def validate_reproduction(self, reproduction_data: ReproductionData) -> bool:
        """Validate that reproduction data is complete and valid."""
        try:
            if not reproduction_data.reproduction_steps:
                logger.warning("No reproduction steps provided")
                return False
            
            if not reproduction_data.action_sequence.actions:
                logger.warning("No actions in sequence")
                return False
            
            if not reproduction_data.game_states:
                logger.warning("No game states provided")
                return False
            
            if reproduction_data.video_path and not os.path.exists(reproduction_data.video_path):
                logger.warning(f"Video file not found: {reproduction_data.video_path}")
                return False
            
            for screenshot in reproduction_data.screenshots:
                if not os.path.exists(screenshot):
                    logger.warning(f"Screenshot not found: {screenshot}")
                    return False
            
            logger.info("Reproduction data validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Reproduction validation failed: {e}")
            return False
    
    def get_reproduction_summary(self, reproduction_data: ReproductionData) -> Dict[str, Any]:
        """Get summary of reproduction data."""
        return {
            "exploit_id": reproduction_data.exploit_id,
            "steps_count": len(reproduction_data.reproduction_steps),
            "actions_count": len(reproduction_data.action_sequence.actions),
            "states_count": len(reproduction_data.game_states),
            "duration": reproduction_data.action_sequence.total_duration,
            "has_video": reproduction_data.video_path is not None,
            "screenshots_count": len(reproduction_data.screenshots),
            "metadata": reproduction_data.metadata
        }
    
    def cleanup_old_reproductions(self, max_age_hours: int = 24) -> int:
        """Clean up old reproduction files."""
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old file: {filename}")
            
            logger.info(f"Cleaned up {cleaned_count} old reproduction files")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old reproductions: {e}")
        
        return cleaned_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reproduction generator statistics."""
        try:
            files = os.listdir(self.output_dir)
            
            exploit_files = [f for f in files if f.startswith("exploit_") and f.endswith("_data.json")]
            video_files = [f for f in files if f.endswith("_video.mp4")]
            screenshot_files = [f for f in files if f.endswith(".png")]
            test_case_files = [f for f in files if f.endswith("_test_case.py")]
            
            return {
                "total_reproductions": len(exploit_files),
                "total_videos": len(video_files),
                "total_screenshots": len(screenshot_files),
                "total_test_cases": len(test_case_files),
                "output_directory": self.output_dir
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
