"""Pattern analysis for detecting exploit behaviors."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action


@dataclass
class Pattern:
    """Represents a detected pattern."""
    pattern_type: str
    start_time: float
    end_time: float
    confidence: float
    description: str
    metadata: Dict[str, Any]


class PatternAnalyzer:
    """Analyzes patterns in game behavior to detect exploits."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize pattern analyzer."""
        self.config = config
        self.min_pattern_length = config.get("min_pattern_length", 5)
        self.max_pattern_length = config.get("max_pattern_length", 50)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        
    def analyze_patterns(self, states: List[GameState], actions: List[Action]) -> List[Dict[str, Any]]:
        """Analyze patterns in game session."""
        logger.info(f"Analyzing patterns in {len(states)} states and {len(actions)} actions")
        
        patterns = []
        
        patterns.extend(self._detect_loops(states, actions))
        patterns.extend(self._detect_stuck_states(states))
        patterns.extend(self._detect_repetitive_actions(actions))
        patterns.extend(self._detect_state_transitions(states))
        patterns.extend(self._detect_resource_patterns(states))
        
        logger.info(f"Detected {len(patterns)} patterns")
        return patterns
    
    def _detect_loops(self, states: List[GameState], actions: List[Action]) -> List[Dict[str, Any]]:
        """Detect infinite loops or repetitive cycles."""
        patterns = []
        
        if len(states) < self.min_pattern_length * 2:
            return patterns
        
        for pattern_length in range(self.min_pattern_length, min(self.max_pattern_length, len(states) // 2)):
            for start_idx in range(len(states) - pattern_length * 2):
                pattern_states = states[start_idx:start_idx + pattern_length]
                next_pattern_states = states[start_idx + pattern_length:start_idx + pattern_length * 2]
                
                similarity = self._calculate_state_similarity(pattern_states, next_pattern_states)
                
                if similarity > self.similarity_threshold:
                    patterns.append({
                        "type": "infinite_loop",
                        "start_time": pattern_states[0].timestamp,
                        "end_time": next_pattern_states[-1].timestamp,
                        "confidence": similarity,
                        "pattern_length": pattern_length,
                        "description": f"Infinite loop detected with {pattern_length} states"
                    })
        
        return patterns
    
    def _detect_stuck_states(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect when player is stuck in same state."""
        patterns = []
        
        if len(states) < self.min_pattern_length:
            return patterns
        
        stuck_threshold = self.config.get("stuck_threshold", 0.95)
        stuck_duration = self.config.get("stuck_duration", 5.0)
        
        current_stuck_start = None
        stuck_count = 0
        
        for i in range(1, len(states)):
            similarity = self._calculate_state_similarity([states[i-1]], [states[i]])
            
            if similarity > stuck_threshold:
                if current_stuck_start is None:
                    current_stuck_start = i - 1
                stuck_count += 1
            else:
                if current_stuck_start is not None and stuck_count >= self.min_pattern_length:
                    stuck_duration_time = states[i-1].timestamp - states[current_stuck_start].timestamp
                    
                    if stuck_duration_time >= stuck_duration:
                        patterns.append({
                            "type": "stuck_state",
                            "timestamp": states[current_stuck_start].timestamp,
                            "duration": stuck_duration_time,
                            "confidence": min(1.0, stuck_count / 20),
                            "stuck_count": stuck_count,
                            "description": f"Player stuck for {stuck_duration_time:.1f}s"
                        })
                
                current_stuck_start = None
                stuck_count = 0
        
        return patterns
    
    def _detect_repetitive_actions(self, actions: List[Action]) -> List[Dict[str, Any]]:
        """Detect repetitive action patterns."""
        patterns = []
        
        if len(actions) < self.min_pattern_length * 2:
            return patterns
        
        action_sequences = self._extract_action_sequences(actions)
        
        for pattern_length in range(self.min_pattern_length, min(self.max_pattern_length, len(actions) // 2)):
            for start_idx in range(len(action_sequences) - pattern_length * 2):
                pattern_actions = action_sequences[start_idx:start_idx + pattern_length]
                next_pattern_actions = action_sequences[start_idx + pattern_length:start_idx + pattern_length * 2]
                
                similarity = self._calculate_action_similarity(pattern_actions, next_pattern_actions)
                
                if similarity > self.similarity_threshold:
                    patterns.append({
                        "type": "repetitive_actions",
                        "start_time": actions[start_idx].timestamp,
                        "end_time": actions[start_idx + pattern_length * 2 - 1].timestamp,
                        "confidence": similarity,
                        "pattern_length": pattern_length,
                        "description": f"Repetitive action pattern with {pattern_length} actions"
                    })
        
        return patterns
    
    def _detect_state_transitions(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect unusual state transitions."""
        patterns = []
        
        if len(states) < 3:
            return patterns
        
        transition_threshold = self.config.get("transition_threshold", 0.1)
        
        for i in range(2, len(states)):
            prev_state = states[i-2]
            curr_state = states[i-1]
            next_state = states[i]
            
            prev_to_curr_similarity = self._calculate_state_similarity([prev_state], [curr_state])
            curr_to_next_similarity = self._calculate_state_similarity([curr_state], [next_state])
            
            if prev_to_curr_similarity > 0.8 and curr_to_next_similarity < transition_threshold:
                patterns.append({
                    "type": "sudden_transition",
                    "timestamp": next_state.timestamp,
                    "confidence": 1.0 - curr_to_next_similarity,
                    "description": "Sudden state transition detected"
                })
        
        return patterns
    
    def _detect_resource_patterns(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect unusual resource patterns."""
        patterns = []
        
        if len(states) < self.min_pattern_length:
            return patterns
        
        resource_gain_threshold = self.config.get("resource_gain_threshold", 100)
        
        for resource_name in ["health", "mana", "gold", "experience"]:
            resource_values = []
            timestamps = []
            
            for state in states:
                if resource_name in state.player_resources:
                    resource_values.append(state.player_resources[resource_name])
                    timestamps.append(state.timestamp)
            
            if len(resource_values) < 2:
                continue
            
            for i in range(1, len(resource_values)):
                gain = resource_values[i] - resource_values[i-1]
                
                if gain > resource_gain_threshold:
                    patterns.append({
                        "type": "resource_gain_pattern",
                        "timestamp": timestamps[i],
                        "resource": resource_name,
                        "gain": gain,
                        "confidence": min(1.0, gain / (resource_gain_threshold * 2)),
                        "description": f"Large {resource_name} gain: {gain:.0f}"
                    })
        
        return patterns
    
    def _extract_action_sequences(self, actions: List[Action]) -> List[str]:
        """Extract action sequences for pattern matching."""
        sequences = []
        
        for action in actions:
            sequence_item = f"{action.action_type}_{action.parameters.get('key', '')}"
            sequences.append(sequence_item)
        
        return sequences
    
    def _calculate_state_similarity(self, states1: List[GameState], states2: List[GameState]) -> float:
        """Calculate similarity between two state sequences."""
        if len(states1) != len(states2):
            return 0.0
        
        similarities = []
        
        for state1, state2 in zip(states1, states2):
            similarity = self._calculate_single_state_similarity(state1, state2)
            similarities.append(similarity)
        
        return np.mean(similarities)
    
    def _calculate_single_state_similarity(self, state1: GameState, state2: GameState) -> float:
        """Calculate similarity between two single states."""
        position_sim = self._calculate_position_similarity(state1.player_position, state2.player_position)
        health_sim = self._calculate_value_similarity(state1.player_health, state2.player_health)
        resource_sim = self._calculate_resource_similarity(state1.player_resources, state2.player_resources)
        
        return (position_sim + health_sim + resource_sim) / 3.0
    
    def _calculate_position_similarity(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate position similarity."""
        distance = ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 + (pos2[2] - pos1[2])**2)**0.5
        max_distance = 1000.0
        return max(0.0, 1.0 - distance / max_distance)
    
    def _calculate_value_similarity(self, val1: float, val2: float) -> float:
        """Calculate value similarity."""
        if val1 == 0 and val2 == 0:
            return 1.0
        
        diff = abs(val1 - val2)
        max_val = max(abs(val1), abs(val2))
        
        if max_val == 0:
            return 1.0
        
        return max(0.0, 1.0 - diff / max_val)
    
    def _calculate_resource_similarity(self, resources1: Dict[str, float], resources2: Dict[str, float]) -> float:
        """Calculate resource similarity."""
        all_keys = set(resources1.keys()) | set(resources2.keys())
        
        if not all_keys:
            return 1.0
        
        similarities = []
        for key in all_keys:
            val1 = resources1.get(key, 0)
            val2 = resources2.get(key, 0)
            similarities.append(self._calculate_value_similarity(val1, val2))
        
        return np.mean(similarities)
    
    def _calculate_action_similarity(self, actions1: List[str], actions2: List[str]) -> float:
        """Calculate action sequence similarity."""
        if len(actions1) != len(actions2):
            return 0.0
        
        matches = sum(1 for a1, a2 in zip(actions1, actions2) if a1 == a2)
        return matches / len(actions1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return {
            "min_pattern_length": self.min_pattern_length,
            "max_pattern_length": self.max_pattern_length,
            "similarity_threshold": self.similarity_threshold
        }
