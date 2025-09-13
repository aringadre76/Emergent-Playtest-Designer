"""Unit tests for core types."""

import pytest
from emergent_playtest_designer.core.types import (
    GameState, Action, ActionSequence, ExploitReport, 
    ExploitType, Severity, NoveltyScore, TestingSession
)


def test_game_state_creation():
    """Test GameState creation and serialization."""
    state = GameState(
        timestamp=1.0,
        player_position=(10.0, 20.0, 30.0),
        player_health=75.0,
        player_resources={"health": 75.0, "mana": 25.0},
        game_objects={"enemy": {"position": [5, 0, 0]}},
        physics_state={"velocity": [1, 0, 0]},
        ui_state={"score": 100},
        custom_metrics={"distance": 50.0}
    )
    
    assert state.timestamp == 1.0
    assert state.player_position == (10.0, 20.0, 30.0)
    assert state.player_health == 75.0
    assert state.player_resources["health"] == 75.0
    
    state_dict = state.to_dict()
    assert state_dict["timestamp"] == 1.0
    assert state_dict["player_position"] == [10.0, 20.0, 30.0]


def test_action_creation():
    """Test Action creation and serialization."""
    action = Action(
        action_type="key_press",
        parameters={"key": "w", "duration": 0.5},
        timestamp=2.0,
        duration=0.1
    )
    
    assert action.action_type == "key_press"
    assert action.parameters["key"] == "w"
    assert action.timestamp == 2.0
    assert action.duration == 0.1
    
    action_dict = action.to_dict()
    assert action_dict["action_type"] == "key_press"
    assert action_dict["parameters"]["key"] == "w"


def test_action_sequence_creation():
    """Test ActionSequence creation and serialization."""
    actions = [
        Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1),
        Action(action_type="key_release", parameters={"key": "w"}, timestamp=0.1, duration=0.0)
    ]
    
    sequence = ActionSequence(
        actions=actions,
        start_time=0.0,
        end_time=0.1,
        total_duration=0.1
    )
    
    assert len(sequence.actions) == 2
    assert sequence.start_time == 0.0
    assert sequence.end_time == 0.1
    assert sequence.total_duration == 0.1
    
    sequence_dict = sequence.to_dict()
    assert len(sequence_dict["actions"]) == 2
    assert sequence_dict["start_time"] == 0.0


def test_exploit_report_creation():
    """Test ExploitReport creation and serialization."""
    actions = [Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1)]
    states = [GameState(timestamp=0.0, player_position=(0, 0, 0), player_health=100, 
                       player_resources={}, game_objects={}, physics_state={}, 
                       ui_state={}, custom_metrics={})]
    
    sequence = ActionSequence(actions=actions, start_time=0.0, end_time=0.1, total_duration=0.1)
    
    report = ExploitReport(
        exploit_id="test-123",
        exploit_type=ExploitType.OUT_OF_BOUNDS,
        severity=Severity.HIGH,
        description="Test exploit",
        reproduction_steps=["Step 1", "Step 2"],
        action_sequence=sequence,
        game_states=states,
        confidence_score=0.8
    )
    
    assert report.exploit_id == "test-123"
    assert report.exploit_type == ExploitType.OUT_OF_BOUNDS
    assert report.severity == Severity.HIGH
    assert report.confidence_score == 0.8
    
    report_dict = report.to_dict()
    assert report_dict["exploit_id"] == "test-123"
    assert report_dict["exploit_type"] == "out_of_bounds"
    assert report_dict["severity"] == "high"


def test_novelty_score_creation():
    """Test NoveltyScore creation and serialization."""
    score = NoveltyScore(
        score=0.75,
        features=[1.0, 2.0, 3.0],
        comparison_states=["state1", "state2"],
        novelty_type="behavioral"
    )
    
    assert score.score == 0.75
    assert len(score.features) == 3
    assert len(score.comparison_states) == 2
    assert score.novelty_type == "behavioral"
    
    score_dict = score.to_dict()
    assert score_dict["score"] == 0.75
    assert score_dict["features"] == [1.0, 2.0, 3.0]


def test_testing_session_creation():
    """Test TestingSession creation and serialization."""
    session = TestingSession(
        session_id="session-123",
        game_path="/path/to/game",
        start_time=100.0,
        end_time=200.0,
        exploits_found=[],
        total_actions=50,
        total_states=100
    )
    
    assert session.session_id == "session-123"
    assert session.game_path == "/path/to/game"
    assert session.start_time == 100.0
    assert session.end_time == 200.0
    assert session.total_actions == 50
    assert session.total_states == 100
    
    session_dict = session.to_dict()
    assert session_dict["session_id"] == "session-123"
    assert session_dict["total_actions"] == 50
