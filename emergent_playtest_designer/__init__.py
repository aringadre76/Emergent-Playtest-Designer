"""
Emergent Playtest Designer

An AI-powered automated testing system for discovering game exploits
through unsupervised exploration of Unity games.
"""

__version__ = "1.0.0"
__author__ = "Development Team"
__email__ = "dev@example.com"

from .core.config import Config
from .core.types import GameState, ExploitReport, ActionSequence

# Import PlaytestOrchestrator lazily to avoid heavy dependency loading
def get_orchestrator():
    """Get PlaytestOrchestrator with lazy import to avoid heavy dependencies on package import."""
    try:
        from .core.orchestrator import PlaytestOrchestrator
        return PlaytestOrchestrator
    except ImportError as e:
        raise ImportError(
            f"PlaytestOrchestrator requires additional dependencies: {e}. "
            "Install with: pip install -r requirements.txt"
        )

__all__ = [
    "get_orchestrator",
    "Config", 
    "GameState",
    "ExploitReport",
    "ActionSequence",
]

# For backward compatibility
PlaytestOrchestrator = None

def __getattr__(name):
    """Lazy import for backward compatibility."""
    if name == "PlaytestOrchestrator":
        global PlaytestOrchestrator
        if PlaytestOrchestrator is None:
            PlaytestOrchestrator = get_orchestrator()
        return PlaytestOrchestrator
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
