"""Novelty search agent for discovering unique game behaviors."""

import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action, NoveltyScore, AgentConfig


@dataclass
class BehaviorArchive:
    """Archive of discovered behaviors."""
    behaviors: List[Dict[str, Any]]
    feature_dimensions: List[str]
    max_size: int = 1000
    
    def add_behavior(self, behavior: Dict[str, Any]) -> None:
        """Add behavior to archive."""
        if len(self.behaviors) >= self.max_size:
            self.behaviors.pop(0)
        self.behaviors.append(behavior)
    
    def get_novelty_score(self, behavior: Dict[str, Any]) -> float:
        """Calculate novelty score for a behavior."""
        if not self.behaviors:
            return 1.0
        
        features = np.array([behavior.get(dim, 0) for dim in self.feature_dimensions])
        distances = []
        
        for existing_behavior in self.behaviors:
            existing_features = np.array([existing_behavior.get(dim, 0) for dim in self.feature_dimensions])
            distance = np.linalg.norm(features - existing_features)
            distances.append(distance)
        
        return np.mean(distances)


class NoveltySearchAgent:
    """Agent that explores game mechanics to discover novel behaviors."""
    
    def __init__(self, config: AgentConfig):
        """Initialize novelty search agent."""
        self.config = config
        self.behavior_archive = BehaviorArchive(
            feature_dimensions=[
                "position_x", "position_y", "position_z",
                "health", "resources", "velocity",
                "action_diversity", "state_transitions"
            ]
        )
        self.current_episode = []
        self.episode_rewards = []
        self.novelty_scores = []
        self.exploration_rate = config.exploration_rate
        self.novelty_threshold = config.novelty_threshold
        
    def select_action(self, state: GameState) -> Action:
        """Select action based on novelty search strategy."""
        if random.random() < self.exploration_rate:
            return self._explore_action(state)
        else:
            return self._exploit_novel_action(state)
    
    def update(self, state: GameState, action: Action, reward: float, next_state: GameState) -> None:
        """Update agent with new experience."""
        self.current_episode.append({
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state
        })
        
        if len(self.current_episode) >= self.config.max_episode_length:
            self._process_episode()
    
    def _explore_action(self, state: GameState) -> Action:
        """Generate random exploratory action."""
        action_types = [
            "key_press", "key_release", "mouse_click", 
            "mouse_move", "joystick_input"
        ]
        
        action_type = random.choice(action_types)
        parameters = self._generate_random_parameters(action_type)
        
        return Action(
            action_type=action_type,
            parameters=parameters,
            timestamp=state.timestamp,
            duration=random.uniform(0.1, 1.0)
        )
    
    def _exploit_novel_action(self, state: GameState) -> Action:
        """Select action that maximizes novelty."""
        candidate_actions = self._generate_candidate_actions(state)
        best_action = None
        best_novelty = -1
        
        for action in candidate_actions:
            predicted_behavior = self._predict_behavior(state, action)
            novelty_score = self.behavior_archive.get_novelty_score(predicted_behavior)
            
            if novelty_score > best_novelty:
                best_novelty = novelty_score
                best_action = action
        
        return best_action or self._explore_action(state)
    
    def _generate_candidate_actions(self, state: GameState) -> List[Action]:
        """Generate candidate actions for novelty evaluation."""
        candidates = []
        
        for _ in range(10):
            action_type = random.choice(["key_press", "key_release", "mouse_click"])
            parameters = self._generate_random_parameters(action_type)
            
            action = Action(
                action_type=action_type,
                parameters=parameters,
                timestamp=state.timestamp,
                duration=random.uniform(0.1, 0.5)
            )
            candidates.append(action)
        
        return candidates
    
    def _generate_random_parameters(self, action_type: str) -> Dict[str, Any]:
        """Generate random parameters for action type."""
        if action_type in ["key_press", "key_release"]:
            keys = ["w", "a", "s", "d", "space", "shift", "ctrl", "alt"]
            return {"key": random.choice(keys)}
        
        elif action_type == "mouse_click":
            return {
                "button": random.choice(["left", "right", "middle"]),
                "x": random.randint(0, 1920),
                "y": random.randint(0, 1080)
            }
        
        elif action_type == "mouse_move":
            return {
                "x": random.randint(0, 1920),
                "y": random.randint(0, 1080),
                "delta_x": random.randint(-100, 100),
                "delta_y": random.randint(-100, 100)
            }
        
        elif action_type == "joystick_input":
            return {
                "axis": random.choice(["horizontal", "vertical", "trigger"]),
                "value": random.uniform(-1.0, 1.0)
            }
        
        return {}
    
    def _predict_behavior(self, state: GameState, action: Action) -> Dict[str, Any]:
        """Predict behavior that would result from action."""
        behavior = {
            "position_x": state.player_position[0],
            "position_y": state.player_position[1],
            "position_z": state.player_position[2],
            "health": state.player_health,
            "resources": sum(state.player_resources.values()),
            "velocity": 0.0,
            "action_diversity": self._calculate_action_diversity(),
            "state_transitions": len(self.current_episode)
        }
        
        if "velocity" in state.physics_state:
            velocity = state.physics_state["velocity"]
            behavior["velocity"] = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)**0.5
        
        return behavior
    
    def _calculate_action_diversity(self) -> float:
        """Calculate diversity of actions in current episode."""
        if not self.current_episode:
            return 0.0
        
        action_types = set()
        for experience in self.current_episode:
            action_types.add(experience["action"].action_type)
        
        return len(action_types) / len(self.current_episode)
    
    def _process_episode(self) -> None:
        """Process completed episode and update archive."""
        if not self.current_episode:
            return
        
        episode_behavior = self._extract_episode_behavior()
        novelty_score = self.behavior_archive.get_novelty_score(episode_behavior)
        
        if novelty_score > self.novelty_threshold:
            self.behavior_archive.add_behavior(episode_behavior)
            logger.info(f"Novel behavior discovered! Novelty score: {novelty_score:.3f}")
        
        self.novelty_scores.append(novelty_score)
        self.current_episode.clear()
    
    def _extract_episode_behavior(self) -> Dict[str, Any]:
        """Extract behavior features from episode."""
        if not self.current_episode:
            return {}
        
        states = [exp["state"] for exp in self.current_episode]
        actions = [exp["action"] for exp in self.current_episode]
        
        final_state = states[-1]
        initial_state = states[0]
        
        behavior = {
            "position_x": final_state.player_position[0],
            "position_y": final_state.player_position[1],
            "position_z": final_state.player_position[2],
            "health": final_state.player_health,
            "resources": sum(final_state.player_resources.values()),
            "velocity": 0.0,
            "action_diversity": self._calculate_action_diversity(),
            "state_transitions": len(self.current_episode),
            "position_change": self._calculate_position_change(initial_state, final_state),
            "health_change": final_state.player_health - initial_state.player_health,
            "episode_length": len(self.current_episode)
        }
        
        if "velocity" in final_state.physics_state:
            velocity = final_state.physics_state["velocity"]
            behavior["velocity"] = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)**0.5
        
        return behavior
    
    def _calculate_position_change(self, initial_state: GameState, final_state: GameState) -> float:
        """Calculate total position change in episode."""
        initial_pos = initial_state.player_position
        final_pos = final_state.player_position
        
        return ((final_pos[0] - initial_pos[0])**2 + 
                (final_pos[1] - initial_pos[1])**2 + 
                (final_pos[2] - initial_pos[2])**2)**0.5
    
    def get_novelty_score(self, behavior: Dict[str, Any]) -> NoveltyScore:
        """Get novelty score for a behavior."""
        score = self.behavior_archive.get_novelty_score(behavior)
        
        return NoveltyScore(
            score=score,
            features=list(behavior.values()),
            comparison_states=[str(b) for b in self.behavior_archive.behaviors[-5:]],
            novelty_type="behavioral"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "archive_size": len(self.behavior_archive.behaviors),
            "episode_count": len(self.novelty_scores),
            "avg_novelty_score": np.mean(self.novelty_scores) if self.novelty_scores else 0.0,
            "exploration_rate": self.exploration_rate,
            "novelty_threshold": self.novelty_threshold,
            "current_episode_length": len(self.current_episode)
        }
    
    def reset(self) -> None:
        """Reset agent state."""
        self.current_episode.clear()
        self.episode_rewards.clear()
        self.novelty_scores.clear()
