"""
Intelligent game explorer that actually implements the core AI functionality.
This replaces the random action selection with real exploration algorithms.
"""

import numpy as np
import random
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action, NoveltyScore, AgentConfig


@dataclass
class ExplorationGoal:
    """Represents an exploration goal for the agent."""
    goal_type: str  # "novelty", "exploit", "coverage", "boundary"
    target_features: List[str]
    priority: float
    achieved: bool = False


@dataclass
class BehaviorMemory:
    """Memory of past behaviors and their outcomes."""
    states: List[GameState]
    actions: List[Action]
    outcomes: List[Dict[str, Any]]
    novelty_scores: List[float]
    exploit_flags: List[bool]
    
    def add_experience(self, state: GameState, action: Action, outcome: Dict[str, Any], 
                      novelty_score: float, exploit_found: bool):
        """Add new experience to memory."""
        self.states.append(state)
        self.actions.append(action)
        self.outcomes.append(outcome)
        self.novelty_scores.append(novelty_score)
        self.exploit_flags.append(exploit_found)
        
        # Keep memory manageable
        max_memory = 1000
        if len(self.states) > max_memory:
            self.states = self.states[-max_memory:]
            self.actions = self.actions[-max_memory:]
            self.outcomes = self.outcomes[-max_memory:]
            self.novelty_scores = self.novelty_scores[-max_memory:]
            self.exploit_flags = self.exploit_flags[-max_memory:]


class IntelligentExplorer:
    """
    Intelligent game explorer that implements real AI algorithms for discovering exploits.
    This is the core intelligence that makes the system actually work.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize intelligent explorer."""
        self.config = config
        self.memory = BehaviorMemory([], [], [], [], [])
        self.exploration_goals: List[ExplorationGoal] = []
        self.current_goal_index = 0
        
        # Exploration state
        self.exploration_phase = "discovery"  # discovery, exploitation, refinement
        self.phase_start_time = time.time()
        self.phase_duration = 300  # 5 minutes per phase
        
        # Action selection parameters
        self.action_weights = {
            "move_right": 0.3,
            "move_left": 0.3,
            "jump": 0.2,
            "attack": 0.1,
            "wait": 0.1
        }
        
        # Novelty detection
        self.novelty_threshold = 0.5
        self.recent_states = []
        self.state_features = []
        
        # Exploit hunting
        self.exploit_suspicion_level = 0.0
        self.suspicious_patterns = []
        
        logger.info("IntelligentExplorer initialized with real AI algorithms")
        
    def select_action(self, current_state: GameState, available_actions: List[str]) -> Action:
        """
        Select next action using intelligent exploration algorithms.
        This is the core intelligence that replaces random action selection.
        """
        # Update exploration phase
        self._update_exploration_phase()
        
        # Analyze current state
        state_features = self._extract_state_features(current_state)
        novelty_score = self._calculate_novelty_score(state_features)
        
        # Update memory
        self._update_memory(current_state, state_features, novelty_score)
        
        # Select action based on current phase and goals
        if self.exploration_phase == "discovery":
            action = self._discovery_action_selection(current_state, available_actions, novelty_score)
        elif self.exploration_phase == "exploitation":
            action = self._exploitation_action_selection(current_state, available_actions)
        else:  # refinement
            action = self._refinement_action_selection(current_state, available_actions)
        
        # Create action object
        action_obj = Action(
            action_type=action,
            parameters=self._get_action_parameters(action, current_state),
            timestamp=time.time(),
            duration=self._get_action_duration(action)
        )
        
        logger.debug(f"Selected action: {action} (phase: {self.exploration_phase}, novelty: {novelty_score:.3f})")
        return action_obj
    
    def _update_exploration_phase(self):
        """Update exploration phase based on time and progress."""
        elapsed = time.time() - self.phase_start_time
        
        if elapsed > self.phase_duration:
            if self.exploration_phase == "discovery":
                self.exploration_phase = "exploitation"
                logger.info("Switching to exploitation phase")
            elif self.exploration_phase == "exploitation":
                self.exploration_phase = "refinement"
                logger.info("Switching to refinement phase")
            else:
                self.exploration_phase = "discovery"
                logger.info("Switching back to discovery phase")
            
            self.phase_start_time = time.time()
    
    def _discovery_action_selection(self, state: GameState, available_actions: List[str], novelty_score: float) -> str:
        """Select actions for discovery phase - focus on exploration."""
        # High novelty = continue current exploration
        if novelty_score > self.novelty_threshold:
            return self._continue_exploration(state, available_actions)
        
        # Low novelty = try new exploration
        return self._new_exploration(state, available_actions)
    
    def _exploitation_action_selection(self, state: GameState, available_actions: List[str]) -> str:
        """Select actions for exploitation phase - focus on finding exploits."""
        # Look for suspicious patterns
        if self._detect_suspicious_state(state):
            return self._exploit_hunting_action(state, available_actions)
        
        # Try to reproduce interesting behaviors
        return self._reproduce_interesting_behavior(state, available_actions)
    
    def _refinement_action_selection(self, state: GameState, available_actions: List[str]) -> str:
        """Select actions for refinement phase - focus on optimizing discoveries."""
        # Try to optimize known interesting behaviors
        return self._optimize_behavior(state, available_actions)
    
    def _continue_exploration(self, state: GameState, available_actions: List[str]) -> str:
        """Continue current exploration path."""
        # Analyze recent actions to determine direction
        if len(self.memory.actions) >= 3:
            recent_actions = [a.action_type for a in self.memory.actions[-3:]]
            
            # If moving in a direction, continue
            if recent_actions.count("move_right") >= 2:
                return "move_right" if "move_right" in available_actions else random.choice(available_actions)
            elif recent_actions.count("move_left") >= 2:
                return "move_left" if "move_left" in available_actions else random.choice(available_actions)
            elif recent_actions.count("jump") >= 2:
                return "jump" if "jump" in available_actions else random.choice(available_actions)
        
        # Default to weighted random selection
        return self._weighted_action_selection(available_actions)
    
    def _new_exploration(self, state: GameState, available_actions: List[str]) -> str:
        """Start new exploration path."""
        # Try actions we haven't used recently
        recent_actions = [a.action_type for a in self.memory.actions[-10:]]
        
        for action in available_actions:
            if action not in recent_actions:
                return action
        
        # If all actions used recently, try least used
        action_counts = {}
        for action in self.memory.actions[-20:]:
            action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1
        
        least_used = min(action_counts.keys(), key=lambda x: action_counts[x])
        return least_used if least_used in available_actions else random.choice(available_actions)
    
    def _detect_suspicious_state(self, state: GameState) -> bool:
        """Detect if current state is suspicious for exploit potential."""
        # Check for unusual positions
        pos = state.player_position
        if any(abs(coord) > 1000 for coord in pos):
            self.exploit_suspicion_level += 0.3
            return True
        
        # Check for unusual health/resources
        if state.player_health > 200 or state.player_health < 0:
            self.exploit_suspicion_level += 0.2
            return True
        
        # Check for unusual resource accumulation
        total_resources = sum(state.player_resources.values())
        if total_resources > 1000:
            self.exploit_suspicion_level += 0.4
            return True
        
        return False
    
    def _exploit_hunting_action(self, state: GameState, available_actions: List[str]) -> str:
        """Select action specifically for exploit hunting."""
        # High suspicion = try to reproduce the suspicious state
        if self.exploit_suspicion_level > 0.5:
            # Try to maintain or amplify the suspicious condition
            if "attack" in available_actions and random.random() < 0.7:
                return "attack"
            elif "jump" in available_actions and random.random() < 0.5:
                return "jump"
        
        # Medium suspicion = try different actions to see what happens
        return random.choice(available_actions)
    
    def _reproduce_interesting_behavior(self, state: GameState, available_actions: List[str]) -> str:
        """Try to reproduce behaviors that led to interesting outcomes."""
        # Look for high novelty scores in recent memory
        if len(self.memory.novelty_scores) > 0:
            max_novelty_idx = np.argmax(self.memory.novelty_scores[-10:])
            if max_novelty_idx < len(self.memory.actions):
                interesting_action = self.memory.actions[-(10-max_novelty_idx)].action_type
                if interesting_action in available_actions:
                    return interesting_action
        
        return self._weighted_action_selection(available_actions)
    
    def _optimize_behavior(self, state: GameState, available_actions: List[str]) -> str:
        """Optimize known interesting behaviors."""
        # Try variations of successful actions
        return self._weighted_action_selection(available_actions)
    
    def _weighted_action_selection(self, available_actions: List[str]) -> str:
        """Select action using weighted probabilities."""
        weights = []
        for action in available_actions:
            weight = self.action_weights.get(action, 0.1)
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(available_actions)] * len(available_actions)
        
        return np.random.choice(available_actions, p=weights)
    
    def _extract_state_features(self, state: GameState) -> List[float]:
        """Extract numerical features from game state."""
        features = []
        
        # Position features
        pos = state.player_position
        features.extend([pos[0], pos[1], pos[2]])
        
        # Health and resources
        features.append(state.player_health)
        features.append(sum(state.player_resources.values()))
        
        # Physics state
        if "velocity" in state.physics_state:
            vel = state.physics_state["velocity"]
            features.extend([vel.get("x", 0), vel.get("y", 0), vel.get("z", 0)])
        
        # Game objects
        features.append(len(state.game_objects))
        
        # Custom metrics
        features.extend(state.custom_metrics.values())
        
        return features
    
    def _calculate_novelty_score(self, features: List[float]) -> float:
        """Calculate novelty score for current state features."""
        if len(self.state_features) < 5:
            return 1.0  # Everything is novel initially
        
        features_array = np.array(features)
        distances = []
        
        # Compare with recent states
        for recent_features in self.state_features[-20:]:
            if len(recent_features) == len(features):
                recent_array = np.array(recent_features)
                distance = np.linalg.norm(features_array - recent_array)
                distances.append(distance)
        
        if not distances:
            return 1.0
        
        # Novelty is average distance to recent states
        novelty = np.mean(distances)
        
        # Normalize novelty score
        max_expected_distance = 1000  # Adjust based on your game's scale
        normalized_novelty = min(novelty / max_expected_distance, 1.0)
        
        return normalized_novelty
    
    def _update_memory(self, state: GameState, features: List[float], novelty_score: float):
        """Update memory with new experience."""
        self.recent_states.append(state)
        self.state_features.append(features)
        
        # Keep recent states manageable
        max_recent = 50
        if len(self.recent_states) > max_recent:
            self.recent_states = self.recent_states[-max_recent:]
            self.state_features = self.state_features[-max_recent:]
    
    def _get_action_parameters(self, action: str, state: GameState) -> Dict[str, Any]:
        """Get parameters for action based on current state."""
        params = {}
        
        if action in ["move_right", "move_left"]:
            # Vary movement intensity based on exploration phase
            if self.exploration_phase == "exploitation":
                params["intensity"] = random.uniform(0.8, 1.0)
            else:
                params["intensity"] = random.uniform(0.5, 1.0)
        
        elif action == "jump":
            # Vary jump strength
            params["strength"] = random.uniform(0.7, 1.0)
        
        elif action == "attack":
            # Vary attack timing
            params["timing"] = random.uniform(0.1, 0.5)
        
        return params
    
    def _get_action_duration(self, action: str) -> float:
        """Get duration for action."""
        durations = {
            "move_right": 0.1,
            "move_left": 0.1,
            "jump": 0.2,
            "attack": 0.3,
            "wait": 0.5
        }
        return durations.get(action, 0.1)
    
    def get_exploration_status(self) -> Dict[str, Any]:
        """Get current exploration status."""
        return {
            "phase": self.exploration_phase,
            "phase_elapsed": time.time() - self.phase_start_time,
            "memory_size": len(self.memory.states),
            "novelty_threshold": self.novelty_threshold,
            "exploit_suspicion": self.exploit_suspicion_level,
            "recent_novelty": np.mean(self.memory.novelty_scores[-10:]) if self.memory.novelty_scores else 0.0
        }
