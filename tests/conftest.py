"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
from emergent_playtest_designer.core.config import Config
from emergent_playtest_designer.core.types import GameState, Action, ActionSequence


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config(
        database=Config.DatabaseConfig(url="sqlite:///:memory:"),
        redis=Config.RedisConfig(url="redis://localhost:6379/1"),
        unity=Config.UnityConfig(
            executable_path="/fake/unity/path",
            project_path="/fake/project/path"
        ),
        llm=Config.LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test_key"
        ),
        testing=Config.TestingConfig(
            test_game_path="/fake/game/path",
            max_testing_time=60,
            max_episodes=10
        )
    )


@pytest.fixture
def sample_game_state():
    """Create sample game state."""
    return GameState(
        timestamp=0.0,
        player_position=(0.0, 0.0, 0.0),
        player_health=100.0,
        player_resources={"health": 100.0, "mana": 50.0},
        game_objects={"enemy_1": {"position": [10, 0, 0], "health": 50}},
        physics_state={"velocity": [0, 0, 0], "acceleration": [0, 0, 0]},
        ui_state={"score": 0, "level": 1},
        custom_metrics={"distance_traveled": 0.0}
    )


@pytest.fixture
def sample_action():
    """Create sample action."""
    return Action(
        action_type="key_press",
        parameters={"key": "w"},
        timestamp=0.0,
        duration=0.1
    )


@pytest.fixture
def sample_action_sequence():
    """Create sample action sequence."""
    actions = [
        Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1),
        Action(action_type="key_release", parameters={"key": "w"}, timestamp=0.1, duration=0.0),
        Action(action_type="mouse_click", parameters={"button": "left", "x": 100, "y": 100}, timestamp=0.2, duration=0.05)
    ]
    
    return ActionSequence(
        actions=actions,
        start_time=0.0,
        end_time=0.25,
        total_duration=0.25
    )


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_unity_controller():
    """Create mock Unity controller."""
    class MockUnityController:
        def __init__(self, config):
            self.config = config
            self.is_running = False
        
        def start_game(self, game_path):
            self.is_running = True
            return True
        
        def stop_game(self):
            self.is_running = False
            return True
        
        def is_game_running(self):
            return self.is_running
        
        def get_game_state(self):
            if self.is_running:
                return GameState(
                    timestamp=0.0,
                    player_position=(0.0, 0.0, 0.0),
                    player_health=100.0,
                    player_resources={},
                    game_objects={},
                    physics_state={},
                    ui_state={},
                    custom_metrics={}
                )
            return None
    
    return MockUnityController
