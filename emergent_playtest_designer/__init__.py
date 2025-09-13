"""
Emergent Playtest Designer

An AI-powered automated testing system for discovering game exploits
through unsupervised exploration of Unity games.
"""

__version__ = "1.0.0"
__author__ = "Development Team"
__email__ = "dev@example.com"

from .core.orchestrator import PlaytestOrchestrator
from .core.config import Config
from .core.types import GameState, ExploitReport, ActionSequence

__all__ = [
    "PlaytestOrchestrator",
    "Config", 
    "GameState",
    "ExploitReport",
    "ActionSequence",
]
