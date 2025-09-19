"""Core type definitions for the Emergent Playtest Designer."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
import numpy as np


class ExploitType(Enum):
    """Types of exploits that can be detected."""
    OUT_OF_BOUNDS = "out_of_bounds"
    INFINITE_RESOURCES = "infinite_resources"
    STUCK_STATE = "stuck_state"
    INFINITE_LOOP = "infinite_loop"
    ABNORMAL_REWARD = "abnormal_reward"
    CLIPPING = "clipping"
    SEQUENCE_BREAK = "sequence_break"
    UNKNOWN = "unknown"


class Severity(Enum):
    """Severity levels for exploits."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GameState:
    """Represents the current state of the game."""
    timestamp: float
    player_position: Tuple[float, float, float]
    player_health: float
    player_resources: Dict[str, float]
    game_objects: Dict[str, Any]
    physics_state: Dict[str, Any]
    ui_state: Dict[str, Any]
    custom_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "player_position": self.player_position,
            "player_health": self.player_health,
            "player_resources": self.player_resources,
            "game_objects": self.game_objects,
            "physics_state": self.physics_state,
            "ui_state": self.ui_state,
            "custom_metrics": self.custom_metrics,
        }


@dataclass
class Action:
    """Represents a single game action."""
    action_type: str
    parameters: Dict[str, Any]
    timestamp: float
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_type": self.action_type,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "duration": self.duration,
        }


@dataclass
class ActionSequence:
    """Represents a sequence of actions."""
    actions: List[Action]
    start_time: float
    end_time: float
    total_duration: float
    
    def __post_init__(self):
        """Calculate total duration if not provided."""
        if self.total_duration == 0:
            self.total_duration = self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "actions": [action.to_dict() for action in self.actions],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration": self.total_duration,
        }


@dataclass
class ExploitReport:
    """Comprehensive report of a discovered exploit."""
    exploit_id: str
    exploit_type: ExploitType
    severity: Severity
    description: str
    reproduction_steps: List[str]
    action_sequence: ActionSequence
    game_states: List[GameState]
    video_path: Optional[str] = None
    screenshots: List[str] = None
    explanation: Optional[str] = None
    confidence_score: float = 0.0
    discovery_time: float = 0.0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.screenshots is None:
            self.screenshots = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "exploit_id": self.exploit_id,
            "exploit_type": self.exploit_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "reproduction_steps": self.reproduction_steps,
            "action_sequence": self.action_sequence.to_dict(),
            "game_states": [state.to_dict() for state in self.game_states],
            "video_path": self.video_path,
            "screenshots": self.screenshots,
            "explanation": self.explanation,
            "confidence_score": self.confidence_score,
            "discovery_time": self.discovery_time,
        }


@dataclass
class NoveltyScore:
    """Represents a novelty score for a game state or action sequence."""
    score: float
    features: List[float]
    comparison_states: List[str]
    novelty_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "score": self.score,
            "features": self.features,
            "comparison_states": self.comparison_states,
            "novelty_type": self.novelty_type,
        }


@dataclass
class TestingSession:
    """Represents a complete testing session."""
    session_id: str
    game_path: str
    start_time: float
    end_time: Optional[float] = None
    exploits_found: List[ExploitReport] = None
    total_actions: int = 0
    total_states: int = 0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.exploits_found is None:
            self.exploits_found = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "game_path": self.game_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "exploits_found": [exploit.to_dict() for exploit in self.exploits_found],
            "total_actions": self.total_actions,
            "total_states": self.total_states,
        }


@dataclass
class ReproductionData:
    """Data needed to reproduce an exploit."""
    exploit_id: str
    action_sequence: ActionSequence
    reproduction_steps: List[str]
    metadata: Dict[str, Any]
    video_path: Optional[str] = None
    screenshots: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.screenshots is None:
            self.screenshots = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "exploit_id": self.exploit_id,
            "action_sequence": self.action_sequence.to_dict(),
            "reproduction_steps": self.reproduction_steps,
            "metadata": self.metadata,
            "video_path": self.video_path,
            "screenshots": self.screenshots,
        }


@dataclass
class AgentConfig:
    """Configuration for AI agents."""
    agent_type: str
    exploration_rate: float = 0.1
    learning_rate: float = 0.001
    memory_size: int = 10000
    batch_size: int = 32
    target_update_frequency: int = 1000
    novelty_threshold: float = 0.5
    max_episode_length: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_type": self.agent_type,
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate,
            "memory_size": self.memory_size,
            "batch_size": self.batch_size,
            "target_update_frequency": self.target_update_frequency,
            "novelty_threshold": self.novelty_threshold,
            "max_episode_length": self.max_episode_length,
        }
