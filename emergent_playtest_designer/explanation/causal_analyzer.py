"""Causal analysis for exploit understanding."""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import ExploitReport, GameState, Action


@dataclass
class CausalEvent:
    """Represents a causal event in the exploit chain."""
    timestamp: float
    event_type: str
    description: str
    confidence: float
    parameters: Dict[str, Any]


@dataclass
class CausalChain:
    """Represents the causal chain of an exploit."""
    root_cause: str
    exploit_mechanism: str
    events: List[CausalEvent]
    confidence: float
    total_duration: float


class CausalAnalyzer:
    """Analyzes causal relationships in exploits."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize causal analyzer."""
        self.config = config
        self.min_correlation = config.get("min_correlation", 0.7)
        self.max_causal_distance = config.get("max_causal_distance", 5.0)
        self.confidence_threshold = config.get("confidence_threshold", 0.5)
        
    def analyze_causal_chain(self, exploit_report: ExploitReport) -> CausalChain:
        """Analyze causal chain of exploit."""
        logger.info(f"Analyzing causal chain for exploit {exploit_report.exploit_id}")
        
        events = self._identify_causal_events(exploit_report)
        root_cause = self._identify_root_cause(exploit_report, events)
        mechanism = self._identify_exploit_mechanism(exploit_report, events)
        confidence = self._calculate_chain_confidence(events)
        
        causal_chain = CausalChain(
            root_cause=root_cause,
            exploit_mechanism=mechanism,
            events=events,
            confidence=confidence,
            total_duration=exploit_report.action_sequence.total_duration
        )
        
        logger.info(f"Causal chain analysis complete: {len(events)} events, confidence: {confidence:.2f}")
        return causal_chain
    
    def _identify_causal_events(self, exploit_report: ExploitReport) -> List[CausalEvent]:
        """Identify causal events in the exploit."""
        events = []
        
        states = exploit_report.game_states
        actions = exploit_report.action_sequence.actions
        
        for i, action in enumerate(actions):
            event = self._analyze_action_impact(action, states, i)
            if event:
                events.append(event)
        
        for i in range(1, len(states)):
            event = self._analyze_state_transition(states[i-1], states[i], i)
            if event:
                events.append(event)
        
        return sorted(events, key=lambda e: e.timestamp)
    
    def _analyze_action_impact(self, action: Action, states: List[GameState], action_index: int) -> Optional[CausalEvent]:
        """Analyze the impact of a specific action."""
        if action_index >= len(states) - 1:
            return None
        
        current_state = states[action_index]
        next_state = states[action_index + 1]
        
        impact_score = self._calculate_action_impact(action, current_state, next_state)
        
        if impact_score > self.confidence_threshold:
            return CausalEvent(
                timestamp=action.timestamp,
                event_type="action_impact",
                description=f"Action '{action.action_type}' caused significant state change",
                confidence=impact_score,
                parameters={
                    "action_type": action.action_type,
                    "action_parameters": action.parameters,
                    "impact_score": impact_score,
                    "state_change": self._calculate_state_change(current_state, next_state)
                }
            )
        
        return None
    
    def _analyze_state_transition(self, prev_state: GameState, curr_state: GameState, state_index: int) -> Optional[CausalEvent]:
        """Analyze state transition for causal events."""
        anomaly_score = self._calculate_state_anomaly(prev_state, curr_state)
        
        if anomaly_score > self.confidence_threshold:
            event_type = self._classify_state_change(prev_state, curr_state)
            
            return CausalEvent(
                timestamp=curr_state.timestamp,
                event_type=event_type,
                description=f"Anomalous state transition: {event_type}",
                confidence=anomaly_score,
                parameters={
                    "anomaly_score": anomaly_score,
                    "prev_state": prev_state.to_dict(),
                    "curr_state": curr_state.to_dict(),
                    "change_magnitude": self._calculate_change_magnitude(prev_state, curr_state)
                }
            )
        
        return None
    
    def _calculate_action_impact(self, action: Action, current_state: GameState, next_state: GameState) -> float:
        """Calculate impact score of an action."""
        position_change = self._calculate_position_change(current_state.player_position, next_state.player_position)
        health_change = abs(next_state.player_health - current_state.player_health)
        resource_change = self._calculate_resource_change(current_state.player_resources, next_state.player_resources)
        
        impact_score = 0.0
        
        if position_change > 50:
            impact_score += min(1.0, position_change / 200)
        
        if health_change > 10:
            impact_score += min(1.0, health_change / 100)
        
        if resource_change > 100:
            impact_score += min(1.0, resource_change / 1000)
        
        return min(1.0, impact_score)
    
    def _calculate_state_change(self, prev_state: GameState, curr_state: GameState) -> Dict[str, float]:
        """Calculate state change metrics."""
        return {
            "position_change": self._calculate_position_change(prev_state.player_position, curr_state.player_position),
            "health_change": curr_state.player_health - prev_state.player_health,
            "resource_change": self._calculate_resource_change(prev_state.player_resources, curr_state.player_resources),
            "time_change": curr_state.timestamp - prev_state.timestamp
        }
    
    def _calculate_state_anomaly(self, prev_state: GameState, curr_state: GameState) -> float:
        """Calculate anomaly score for state transition."""
        position_change = self._calculate_position_change(prev_state.player_position, curr_state.player_position)
        health_change = abs(curr_state.player_health - prev_state.player_health)
        resource_change = self._calculate_resource_change(prev_state.player_resources, curr_state.player_resources)
        
        anomaly_score = 0.0
        
        if position_change > 100:
            anomaly_score += min(1.0, position_change / 500)
        
        if health_change > 50:
            anomaly_score += min(1.0, health_change / 200)
        
        if resource_change > 1000:
            anomaly_score += min(1.0, resource_change / 5000)
        
        return min(1.0, anomaly_score)
    
    def _classify_state_change(self, prev_state: GameState, curr_state: GameState) -> str:
        """Classify type of state change."""
        position_change = self._calculate_position_change(prev_state.player_position, curr_state.player_position)
        health_change = curr_state.player_health - prev_state.player_health
        resource_change = self._calculate_resource_change(prev_state.player_resources, curr_state.player_resources)
        
        if position_change > 100:
            return "teleportation"
        elif health_change > 50:
            return "rapid_healing"
        elif resource_change > 1000:
            return "resource_exploit"
        elif curr_state.player_health <= 0:
            return "death"
        else:
            return "state_anomaly"
    
    def _calculate_change_magnitude(self, prev_state: GameState, curr_state: GameState) -> float:
        """Calculate magnitude of state change."""
        position_change = self._calculate_position_change(prev_state.player_position, curr_state.player_position)
        health_change = abs(curr_state.player_health - prev_state.player_health)
        resource_change = self._calculate_resource_change(prev_state.player_resources, curr_state.player_resources)
        
        return (position_change + health_change + resource_change) / 3.0
    
    def _identify_root_cause(self, exploit_report: ExploitReport, events: List[CausalEvent]) -> str:
        """Identify root cause of exploit."""
        if not events:
            return "Unknown root cause"
        
        exploit_type = exploit_report.exploit_type.value
        
        if exploit_type == "out_of_bounds":
            return "Insufficient boundary validation in movement system"
        elif exploit_type == "infinite_resources":
            return "Missing resource validation or rate limiting"
        elif exploit_type == "stuck_state":
            return "Inadequate state transition validation"
        elif exploit_type == "infinite_loop":
            return "Missing loop detection or termination conditions"
        elif exploit_type == "clipping":
            return "Insufficient collision detection"
        else:
            return "Game mechanic validation failure"
    
    def _identify_exploit_mechanism(self, exploit_report: ExploitReport, events: List[CausalEvent]) -> str:
        """Identify exploit mechanism."""
        if not events:
            return "Unknown mechanism"
        
        exploit_type = exploit_report.exploit_type.value
        
        if exploit_type == "out_of_bounds":
            return "Player position validation bypass"
        elif exploit_type == "infinite_resources":
            return "Resource generation rate exploit"
        elif exploit_type == "stuck_state":
            return "State machine deadlock"
        elif exploit_type == "infinite_loop":
            return "Conditional loop termination failure"
        elif exploit_type == "clipping":
            return "Collision detection bypass"
        else:
            return "Unexpected game state transition"
    
    def _calculate_chain_confidence(self, events: List[CausalEvent]) -> float:
        """Calculate confidence in causal chain."""
        if not events:
            return 0.0
        
        confidences = [event.confidence for event in events]
        return np.mean(confidences)
    
    def _calculate_position_change(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate position change."""
        return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 + (pos2[2] - pos1[2])**2)**0.5
    
    def _calculate_resource_change(self, resources1: Dict[str, float], resources2: Dict[str, float]) -> float:
        """Calculate total resource change."""
        total1 = sum(resources1.values())
        total2 = sum(resources2.values())
        return abs(total2 - total1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get causal analyzer statistics."""
        return {
            "min_correlation": self.min_correlation,
            "max_causal_distance": self.max_causal_distance,
            "confidence_threshold": self.confidence_threshold
        }