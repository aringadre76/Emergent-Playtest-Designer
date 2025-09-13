"""Causal analysis for exploit understanding."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action, ExploitReport


@dataclass
class CausalEvent:
    """Represents a causal event in the exploit."""
    timestamp: float
    event_type: str
    description: str
    impact: float
    dependencies: List[str]
    metadata: Dict[str, Any]


@dataclass
class CausalChain:
    """Represents a causal chain of events."""
    events: List[CausalEvent]
    root_cause: str
    exploit_mechanism: str
    confidence: float


class CausalAnalyzer:
    """Analyzes causal relationships in exploits."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize causal analyzer."""
        self.config = config
        self.min_correlation = config.get("min_correlation", 0.7)
        self.max_causal_distance = config.get("max_causal_distance", 5.0)
        
    def analyze_causal_chain(self, exploit_report: ExploitReport) -> CausalChain:
        """Analyze causal chain of exploit."""
        logger.info(f"Analyzing causal chain for exploit {exploit_report.exploit_id}")
        
        events = self._extract_causal_events(exploit_report)
        correlations = self._calculate_correlations(events)
        causal_relationships = self._identify_causal_relationships(events, correlations)
        
        root_cause = self._identify_root_cause(events, causal_relationships)
        exploit_mechanism = self._identify_exploit_mechanism(events, causal_relationships)
        confidence = self._calculate_confidence(events, causal_relationships)
        
        causal_chain = CausalChain(
            events=events,
            root_cause=root_cause,
            exploit_mechanism=exploit_mechanism,
            confidence=confidence
        )
        
        logger.info(f"Causal analysis completed with confidence {confidence:.3f}")
        return causal_chain
    
    def _extract_causal_events(self, exploit_report: ExploitReport) -> List[CausalEvent]:
        """Extract causal events from exploit report."""
        events = []
        
        for i, state in enumerate(exploit_report.game_states):
            event = self._state_to_causal_event(state, i)
            if event:
                events.append(event)
        
        for i, action in enumerate(exploit_report.action_sequence.actions):
            event = self._action_to_causal_event(action, i)
            if event:
                events.append(event)
        
        return sorted(events, key=lambda e: e.timestamp)
    
    def _state_to_causal_event(self, state: GameState, index: int) -> Optional[CausalEvent]:
        """Convert game state to causal event."""
        event_type = "state_change"
        description = f"Game state {index}"
        impact = 0.0
        dependencies = []
        metadata = {}
        
        if state.player_health <= 0:
            event_type = "death"
            description = "Player died"
            impact = 1.0
            metadata["health"] = state.player_health
        
        elif state.player_position[0] > 1000 or state.player_position[0] < -1000:
            event_type = "out_of_bounds"
            description = "Player moved out of bounds"
            impact = 0.8
            metadata["position"] = state.player_position
        
        elif sum(state.player_resources.values()) > 10000:
            event_type = "resource_exploit"
            description = "Abnormal resource accumulation"
            impact = 0.9
            metadata["resources"] = state.player_resources
        
        if impact > 0:
            return CausalEvent(
                timestamp=state.timestamp,
                event_type=event_type,
                description=description,
                impact=impact,
                dependencies=dependencies,
                metadata=metadata
            )
        
        return None
    
    def _action_to_causal_event(self, action: Action, index: int) -> Optional[CausalEvent]:
        """Convert action to causal event."""
        event_type = "action"
        description = f"Action {index}: {action.action_type}"
        impact = 0.1
        dependencies = []
        metadata = {"action_type": action.action_type, "parameters": action.parameters}
        
        if action.action_type in ["key_press", "mouse_click"]:
            impact = 0.3
            description = f"Input: {action.action_type}"
        
        elif action.action_type == "joystick_input":
            impact = 0.2
            description = f"Joystick input: {action.parameters.get('axis', 'unknown')}"
        
        return CausalEvent(
            timestamp=action.timestamp,
            event_type=event_type,
            description=description,
            impact=impact,
            dependencies=dependencies,
            metadata=metadata
        )
    
    def _calculate_correlations(self, events: List[CausalEvent]) -> Dict[Tuple[int, int], float]:
        """Calculate correlations between events."""
        correlations = {}
        
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                correlation = self._calculate_event_correlation(events[i], events[j])
                correlations[(i, j)] = correlation
        
        return correlations
    
    def _calculate_event_correlation(self, event1: CausalEvent, event2: CausalEvent) -> float:
        """Calculate correlation between two events."""
        time_diff = abs(event2.timestamp - event1.timestamp)
        
        if time_diff > self.max_causal_distance:
            return 0.0
        
        type_similarity = self._calculate_type_similarity(event1.event_type, event2.event_type)
        impact_similarity = 1.0 - abs(event1.impact - event2.impact)
        temporal_proximity = 1.0 - (time_diff / self.max_causal_distance)
        
        correlation = (type_similarity + impact_similarity + temporal_proximity) / 3.0
        return correlation
    
    def _calculate_type_similarity(self, type1: str, type2: str) -> float:
        """Calculate similarity between event types."""
        if type1 == type2:
            return 1.0
        
        similar_types = {
            ("state_change", "action"): 0.3,
            ("death", "out_of_bounds"): 0.5,
            ("resource_exploit", "action"): 0.4,
        }
        
        return similar_types.get((type1, type2), similar_types.get((type2, type1), 0.0))
    
    def _identify_causal_relationships(self, events: List[CausalEvent], 
                                    correlations: Dict[Tuple[int, int], float]) -> Dict[int, List[int]]:
        """Identify causal relationships between events."""
        relationships = {i: [] for i in range(len(events))}
        
        for (i, j), correlation in correlations.items():
            if correlation > self.min_correlation:
                if events[i].timestamp < events[j].timestamp:
                    relationships[i].append(j)
                else:
                    relationships[j].append(i)
        
        return relationships
    
    def _identify_root_cause(self, events: List[CausalEvent], 
                           relationships: Dict[int, List[int]]) -> str:
        """Identify root cause of exploit."""
        if not events:
            return "No events detected"
        
        high_impact_events = [e for e in events if e.impact > 0.5]
        
        if not high_impact_events:
            return "No high-impact events detected"
        
        root_event = max(high_impact_events, key=lambda e: e.impact)
        
        if root_event.event_type == "out_of_bounds":
            return f"Player movement exploit at frame {root_event.timestamp:.2f}s"
        elif root_event.event_type == "resource_exploit":
            return f"Resource manipulation exploit at frame {root_event.timestamp:.2f}s"
        elif root_event.event_type == "death":
            return f"Death/stuck state exploit at frame {root_event.timestamp:.2f}s"
        else:
            return f"Unknown exploit mechanism at frame {root_event.timestamp:.2f}s"
    
    def _identify_exploit_mechanism(self, events: List[CausalEvent], 
                                  relationships: Dict[int, List[int]]) -> str:
        """Identify the exploit mechanism."""
        exploit_types = [e.event_type for e in events if e.impact > 0.5]
        
        if not exploit_types:
            return "Unknown mechanism"
        
        if "out_of_bounds" in exploit_types:
            return "Boundary violation through movement manipulation"
        elif "resource_exploit" in exploit_types:
            return "Resource duplication or infinite generation"
        elif "death" in exploit_types:
            return "State corruption leading to stuck/death state"
        else:
            return "Complex multi-step exploit sequence"
    
    def _calculate_confidence(self, events: List[CausalEvent], 
                            relationships: Dict[int, List[int]]) -> float:
        """Calculate confidence in causal analysis."""
        if not events:
            return 0.0
        
        high_impact_count = sum(1 for e in events if e.impact > 0.5)
        total_events = len(events)
        
        if total_events == 0:
            return 0.0
        
        impact_ratio = high_impact_count / total_events
        
        relationship_strength = sum(len(deps) for deps in relationships.values()) / total_events
        
        confidence = (impact_ratio + min(relationship_strength, 1.0)) / 2.0
        return min(1.0, confidence)
    
    def generate_explanation_text(self, causal_chain: CausalChain) -> str:
        """Generate human-readable explanation from causal chain."""
        explanation = f"""
EXPLOIT ANALYSIS REPORT
======================

Root Cause: {causal_chain.root_cause}
Mechanism: {causal_chain.exploit_mechanism}
Confidence: {causal_chain.confidence:.1%}

CAUSAL CHAIN OF EVENTS:
"""
        
        for i, event in enumerate(causal_chain.events):
            explanation += f"{i+1}. Frame {event.timestamp:.2f}s: {event.description} (Impact: {event.impact:.1%})\n"
            
            if event.metadata:
                for key, value in event.metadata.items():
                    explanation += f"   - {key}: {value}\n"
        
        explanation += f"""
ANALYSIS SUMMARY:
- Total events analyzed: {len(causal_chain.events)}
- High-impact events: {sum(1 for e in causal_chain.events if e.impact > 0.5)}
- Causal relationships: {sum(len(deps) for deps in self._identify_causal_relationships(causal_chain.events, {}).values())}
- Exploit complexity: {'High' if len(causal_chain.events) > 10 else 'Medium' if len(causal_chain.events) > 5 else 'Low'}
"""
        
        return explanation
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return {
            "min_correlation": self.min_correlation,
            "max_causal_distance": self.max_causal_distance
        }
