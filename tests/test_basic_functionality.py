"""Basic functionality tests for the Emergent Playtest Designer."""

import pytest
import time
from emergent_playtest_designer.core.types import GameState, Action, ExploitReport, ExploitType, Severity, ActionSequence
from emergent_playtest_designer.core.config import Config
from emergent_playtest_designer.detection import ExploitDetector
from emergent_playtest_designer.agents import NoveltySearchAgent
from emergent_playtest_designer.core.database import DatabaseManager


class TestGameState:
    """Test GameState functionality."""
    
    def test_game_state_creation(self):
        """Test GameState creation."""
        state = GameState(
            timestamp=time.time(),
            player_position=(0.0, 0.0, 0.0),
            player_health=100.0,
            player_resources={"coins": 10, "lives": 3},
            game_objects={"platforms": []},
            physics_state={"velocity": [0.0, 0.0, 0.0]},
            ui_state={"score": 0},
            custom_metrics={"jump_count": 0}
        )
        
        assert state.player_position == (0.0, 0.0, 0.0)
        assert state.player_health == 100.0
        assert state.player_resources["coins"] == 10
        assert state.player_resources["lives"] == 3
    
    def test_game_state_to_dict(self):
        """Test GameState to_dict conversion."""
        state = GameState(
            timestamp=1234567890.0,
            player_position=(1.0, 2.0, 3.0),
            player_health=50.0,
            player_resources={"coins": 5},
            game_objects={},
            physics_state={},
            ui_state={},
            custom_metrics={}
        )
        
        state_dict = state.to_dict()
        
        assert state_dict["timestamp"] == 1234567890.0
        assert state_dict["player_position"] == [1.0, 2.0, 3.0]
        assert state_dict["player_health"] == 50.0
        assert state_dict["player_resources"]["coins"] == 5


class TestAction:
    """Test Action functionality."""
    
    def test_action_creation(self):
        """Test Action creation."""
        action = Action(
            action_type="key_press",
            parameters={"key": "w"},
            timestamp=time.time(),
            duration=0.1
        )
        
        assert action.action_type == "key_press"
        assert action.parameters["key"] == "w"
        assert action.duration == 0.1
    
    def test_action_to_dict(self):
        """Test Action to_dict conversion."""
        action = Action(
            action_type="mouse_click",
            parameters={"button": "left", "x": 100, "y": 200},
            timestamp=1234567890.0,
            duration=0.5
        )
        
        action_dict = action.to_dict()
        
        assert action_dict["action_type"] == "mouse_click"
        assert action_dict["parameters"]["button"] == "left"
        assert action_dict["parameters"]["x"] == 100
        assert action_dict["parameters"]["y"] == 200
        assert action_dict["timestamp"] == 1234567890.0
        assert action_dict["duration"] == 0.5


class TestActionSequence:
    """Test ActionSequence functionality."""
    
    def test_action_sequence_creation(self):
        """Test ActionSequence creation."""
        actions = [
            Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1),
            Action(action_type="key_release", parameters={"key": "w"}, timestamp=0.1, duration=0.1)
        ]
        
        sequence = ActionSequence(
            actions=actions,
            start_time=0.0,
            end_time=0.2,
            total_duration=0.2
        )
        
        assert len(sequence.actions) == 2
        assert sequence.start_time == 0.0
        assert sequence.end_time == 0.2
        assert sequence.total_duration == 0.2
    
    def test_action_sequence_auto_duration(self):
        """Test ActionSequence automatic duration calculation."""
        actions = [
            Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1),
            Action(action_type="key_release", parameters={"key": "w"}, timestamp=0.1, duration=0.1)
        ]
        
        sequence = ActionSequence(
            actions=actions,
            start_time=0.0,
            end_time=0.2,
            total_duration=0.0
        )
        
        assert sequence.total_duration == 0.2


class TestExploitReport:
    """Test ExploitReport functionality."""
    
    def test_exploit_report_creation(self):
        """Test ExploitReport creation."""
        actions = [
            Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1)
        ]
        
        sequence = ActionSequence(
            actions=actions,
            start_time=0.0,
            end_time=0.1,
            total_duration=0.1
        )
        
        states = [
            GameState(
                timestamp=0.0,
                player_position=(0.0, 0.0, 0.0),
                player_health=100.0,
                player_resources={},
                game_objects={},
                physics_state={},
                ui_state={},
                custom_metrics={}
            )
        ]
        
        report = ExploitReport(
            exploit_id="test-exploit-1",
            exploit_type=ExploitType.OUT_OF_BOUNDS,
            severity=Severity.HIGH,
            description="Test exploit",
            reproduction_steps=["1. Press W key", "2. Observe teleportation"],
            action_sequence=sequence,
            game_states=states,
            confidence_score=0.9,
            discovery_time=time.time()
        )
        
        assert report.exploit_id == "test-exploit-1"
        assert report.exploit_type == ExploitType.OUT_OF_BOUNDS
        assert report.severity == Severity.HIGH
        assert report.confidence_score == 0.9
        assert len(report.reproduction_steps) == 2
        assert len(report.game_states) == 1


class TestConfig:
    """Test Config functionality."""
    
    def test_config_creation(self):
        """Test Config creation."""
        config = Config()
        
        assert config.unity.executable_path == ""
        assert config.unity.project_path == ""
        assert config.unity.headless_mode is True
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"
    
    def test_config_validation(self):
        """Test Config validation."""
        config = Config()
        
        with pytest.raises(ValueError):
            config.validate()
        
        config.unity.executable_path = "/path/to/unity"
        config.unity.project_path = "/path/to/project"
        config.llm.api_key = "test-key"
        
        assert config.validate() is True


class TestExploitDetector:
    """Test ExploitDetector functionality."""
    
    def test_exploit_detector_creation(self):
        """Test ExploitDetector creation."""
        config = {
            "confidence_threshold": 0.8,
            "realtime_threshold": 0.7,
            "anomaly_config": {"contamination": 0.1},
            "pattern_config": {"min_pattern_length": 5}
        }
        
        detector = ExploitDetector(config)
        
        assert detector.config["confidence_threshold"] == 0.8
        assert detector.config["realtime_threshold"] == 0.7
    
    def test_exploit_detector_statistics(self):
        """Test ExploitDetector statistics."""
        config = {"confidence_threshold": 0.8}
        detector = ExploitDetector(config)
        
        stats = detector.get_statistics()
        
        assert "total_exploits" in stats
        assert "exploit_types" in stats
        assert "candidates" in stats
        assert "avg_confidence" in stats


class TestNoveltySearchAgent:
    """Test NoveltySearchAgent functionality."""
    
    def test_agent_creation(self):
        """Test NoveltySearchAgent creation."""
        from emergent_playtest_designer.core.types import AgentConfig
        
        config = AgentConfig(
            agent_type="novelty_search",
            exploration_rate=0.1,
            learning_rate=0.001,
            memory_size=10000,
            batch_size=32,
            target_update_frequency=1000,
            novelty_threshold=0.5,
            max_episode_length=1000
        )
        
        agent = NoveltySearchAgent(config)
        
        assert agent.config.agent_type == "novelty_search"
        assert agent.exploration_rate == 0.1
        assert agent.novelty_threshold == 0.5
    
    def test_agent_action_selection(self):
        """Test agent action selection."""
        from emergent_playtest_designer.core.types import AgentConfig
        
        config = AgentConfig(agent_type="novelty_search")
        agent = NoveltySearchAgent(config)
        
        state = GameState(
            timestamp=time.time(),
            player_position=(0.0, 0.0, 0.0),
            player_health=100.0,
            player_resources={},
            game_objects={},
            physics_state={},
            ui_state={},
            custom_metrics={}
        )
        
        action = agent.select_action(state)
        
        assert action is not None
        assert action.action_type in ["key_press", "key_release", "mouse_click", "mouse_move", "joystick_input"]
        assert action.timestamp == state.timestamp
    
    def test_agent_statistics(self):
        """Test agent statistics."""
        from emergent_playtest_designer.core.types import AgentConfig
        
        config = AgentConfig(agent_type="novelty_search")
        agent = NoveltySearchAgent(config)
        
        stats = agent.get_statistics()
        
        assert "archive_size" in stats
        assert "episode_count" in stats
        assert "avg_novelty_score" in stats
        assert "exploration_rate" in stats


class TestDatabaseManager:
    """Test DatabaseManager functionality."""
    
    def test_database_creation(self):
        """Test DatabaseManager creation."""
        db = DatabaseManager(":memory:")
        
        assert db.db_path == ":memory:"
    
    def test_database_statistics(self):
        """Test DatabaseManager statistics."""
        db = DatabaseManager(":memory:")
        
        stats = db.get_statistics()
        
        assert "database_path" in stats
        assert "session_count" in stats
        assert "exploit_count" in stats
        assert "test_case_count" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
