"""Anomaly detection for game states and behaviors."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


@dataclass
class AnomalyScore:
    """Represents an anomaly score."""
    score: float
    anomaly_type: str
    confidence: float
    features: List[float]
    description: str


class AnomalyDetector:
    """Detects anomalies in game states and behaviors."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize anomaly detector."""
        self.config = config
        self.isolation_forest = IsolationForest(
            contamination=config.get("contamination", 0.1),
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.normal_states: List[np.ndarray] = []
        self.anomaly_threshold = config.get("anomaly_threshold", 0.5)
        
    def detect_anomalies(self, states: List[GameState], actions: List[Action]) -> List[Dict[str, Any]]:
        """Detect anomalies in game session."""
        logger.info(f"Detecting anomalies in {len(states)} states")
        
        anomalies = []
        
        anomalies.extend(self._detect_position_anomalies(states))
        anomalies.extend(self._detect_health_anomalies(states))
        anomalies.extend(self._detect_resource_anomalies(states))
        anomalies.extend(self._detect_physics_anomalies(states))
        anomalies.extend(self._detect_action_anomalies(actions))
        anomalies.extend(self._detect_temporal_anomalies(states, actions))
        
        if len(self.normal_states) > 100:
            anomalies.extend(self._detect_statistical_anomalies(states))
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def score_state(self, state: GameState, action: Action) -> float:
        """Score single state-action pair for anomaly."""
        features = self._extract_features(state, action)
        
        if not self.is_fitted:
            return 0.0
        
        try:
            features_scaled = self.scaler.transform([features])
            anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
            return max(0.0, min(1.0, (anomaly_score + 1) / 2))
        except Exception as e:
            logger.error(f"Error scoring state: {e}")
            return 0.0
    
    def fit_normal_behavior(self, states: List[GameState], actions: List[Action]) -> None:
        """Fit detector to normal behavior patterns."""
        logger.info(f"Fitting anomaly detector to {len(states)} normal states")
        
        features_list = []
        
        for state, action in zip(states, actions):
            features = self._extract_features(state, action)
            features_list.append(features)
        
        if features_list:
            self.normal_states = np.array(features_list)
            self.scaler.fit(self.normal_states)
            self.isolation_forest.fit(self.normal_states)
            self.is_fitted = True
            
            logger.info("Anomaly detector fitted successfully")
    
    def _detect_position_anomalies(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect position-related anomalies."""
        anomalies = []
        
        for i in range(1, len(states)):
            prev_pos = states[i-1].player_position
            curr_pos = states[i].player_position
            
            distance = self._calculate_distance(prev_pos, curr_pos)
            time_diff = states[i].timestamp - states[i-1].timestamp
            
            if time_diff > 0:
                speed = distance / time_diff
                
                if speed > 100:
                    anomalies.append({
                        "type": "teleportation",
                        "timestamp": states[i].timestamp,
                        "speed": speed,
                        "distance": distance,
                        "confidence": min(1.0, speed / 200),
                        "description": f"Player moved {distance:.2f} units in {time_diff:.3f}s"
                    })
                
                if distance > 1000:
                    anomalies.append({
                        "type": "out_of_bounds",
                        "timestamp": states[i].timestamp,
                        "distance": distance,
                        "confidence": min(1.0, distance / 2000),
                        "description": f"Player moved {distance:.2f} units (possible out of bounds)"
                    })
        
        return anomalies
    
    def _detect_health_anomalies(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect health-related anomalies."""
        anomalies = []
        
        for i in range(1, len(states)):
            prev_health = states[i-1].player_health
            curr_health = states[i].player_health
            
            if prev_health > 0 and curr_health <= 0:
                anomalies.append({
                    "type": "death",
                    "timestamp": states[i].timestamp,
                    "confidence": 1.0,
                    "description": "Player died"
                })
            
            elif curr_health > prev_health and prev_health > 0:
                heal_amount = curr_health - prev_health
                if heal_amount > 50:
                    anomalies.append({
                        "type": "rapid_healing",
                        "timestamp": states[i].timestamp,
                        "heal_amount": heal_amount,
                        "confidence": min(1.0, heal_amount / 200),
                        "description": f"Player healed {heal_amount:.1f} health instantly"
                    })
            
            elif curr_health < 0:
                anomalies.append({
                    "type": "negative_health",
                    "timestamp": states[i].timestamp,
                    "health": curr_health,
                    "confidence": 1.0,
                    "description": f"Player has negative health: {curr_health:.1f}"
                })
        
        return anomalies
    
    def _detect_resource_anomalies(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect resource-related anomalies."""
        anomalies = []
        
        for i in range(1, len(states)):
            prev_resources = states[i-1].player_resources
            curr_resources = states[i].player_resources
            
            for resource, curr_value in curr_resources.items():
                prev_value = prev_resources.get(resource, 0)
                
                if curr_value > prev_value:
                    gain = curr_value - prev_value
                    if gain > 1000:
                        anomalies.append({
                            "type": "resource_exploit",
                            "timestamp": states[i].timestamp,
                            "resource": resource,
                            "gain": gain,
                            "confidence": min(1.0, gain / 5000),
                            "description": f"Gained {gain:.0f} {resource} instantly"
                        })
                
                if curr_value < 0:
                    anomalies.append({
                        "type": "negative_resource",
                        "timestamp": states[i].timestamp,
                        "resource": resource,
                        "value": curr_value,
                        "confidence": 1.0,
                        "description": f"Negative {resource}: {curr_value:.0f}"
                    })
        
        return anomalies
    
    def _detect_physics_anomalies(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect physics-related anomalies."""
        anomalies = []
        
        for state in states:
            physics_state = state.physics_state
            
            if "velocity" in physics_state:
                velocity = physics_state["velocity"]
                speed = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)**0.5
                
                if speed > 50:
                    anomalies.append({
                        "type": "high_velocity",
                        "timestamp": state.timestamp,
                        "speed": speed,
                        "confidence": min(1.0, speed / 100),
                        "description": f"Player moving at {speed:.1f} units/s"
                    })
            
            if "acceleration" in physics_state:
                acceleration = physics_state["acceleration"]
                accel_magnitude = (acceleration[0]**2 + acceleration[1]**2 + acceleration[2]**2)**0.5
                
                if accel_magnitude > 100:
                    anomalies.append({
                        "type": "high_acceleration",
                        "timestamp": state.timestamp,
                        "acceleration": accel_magnitude,
                        "confidence": min(1.0, accel_magnitude / 200),
                        "description": f"Player accelerating at {accel_magnitude:.1f} units/s²"
                    })
        
        return anomalies
    
    def _detect_action_anomalies(self, actions: List[Action]) -> List[Dict[str, Any]]:
        """Detect action-related anomalies."""
        anomalies = []
        
        if len(actions) < 10:
            return anomalies
        
        action_counts = {}
        for action in actions:
            action_type = action.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        total_actions = len(actions)
        
        for action_type, count in action_counts.items():
            frequency = count / total_actions
            
            if frequency > 0.8:
                anomalies.append({
                    "type": "action_spam",
                    "timestamp": actions[-1].timestamp,
                    "action_type": action_type,
                    "frequency": frequency,
                    "confidence": min(1.0, frequency),
                    "description": f"Action {action_type} used {frequency:.1%} of the time"
                })
        
        return anomalies
    
    def _detect_temporal_anomalies(self, states: List[GameState], actions: List[Action]) -> List[Dict[str, Any]]:
        """Detect temporal anomalies."""
        anomalies = []
        
        if len(states) < 2:
            return anomalies
        
        time_diffs = []
        for i in range(1, len(states)):
            time_diff = states[i].timestamp - states[i-1].timestamp
            time_diffs.append(time_diff)
        
        if time_diffs:
            avg_time_diff = np.mean(time_diffs)
            std_time_diff = np.std(time_diffs)
            
            for i, time_diff in enumerate(time_diffs):
                if abs(time_diff - avg_time_diff) > 3 * std_time_diff:
                    anomalies.append({
                        "type": "temporal_anomaly",
                        "timestamp": states[i+1].timestamp,
                        "time_diff": time_diff,
                        "expected_diff": avg_time_diff,
                        "confidence": min(1.0, abs(time_diff - avg_time_diff) / (3 * std_time_diff)),
                        "description": f"Unexpected time difference: {time_diff:.3f}s (expected {avg_time_diff:.3f}s)"
                    })
        
        return anomalies
    
    def _detect_statistical_anomalies(self, states: List[GameState]) -> List[Dict[str, Any]]:
        """Detect statistical anomalies using machine learning."""
        anomalies = []
        
        if not self.is_fitted:
            return anomalies
        
        try:
            features_list = []
            for state in states:
                features = self._extract_features(state, None)
                features_list.append(features)
            
            features_array = np.array(features_list)
            features_scaled = self.scaler.transform(features_array)
            
            anomaly_predictions = self.isolation_forest.predict(features_scaled)
            anomaly_scores = self.isolation_forest.decision_function(features_scaled)
            
            for i, (prediction, score) in enumerate(zip(anomaly_predictions, anomaly_scores)):
                if prediction == -1:
                    confidence = max(0.0, min(1.0, (score + 1) / 2))
                    
                    anomalies.append({
                        "type": "statistical_anomaly",
                        "timestamp": states[i].timestamp,
                        "confidence": confidence,
                        "description": f"Statistical anomaly detected (score: {score:.3f})"
                    })
        
        except Exception as e:
            logger.error(f"Error in statistical anomaly detection: {e}")
        
        return anomalies
    
    def _extract_features(self, state: GameState, action: Optional[Action]) -> List[float]:
        """Extract features from state and action."""
        features = []
        
        features.extend(state.player_position)
        features.append(state.player_health)
        features.append(sum(state.player_resources.values()))
        
        if "velocity" in state.physics_state:
            features.extend(state.physics_state["velocity"])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        if "acceleration" in state.physics_state:
            features.extend(state.physics_state["acceleration"])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        features.extend(list(state.player_resources.values())[:5])
        
        if action:
            features.append(1.0 if action.action_type == "key_press" else 0.0)
            features.append(1.0 if action.action_type == "mouse_click" else 0.0)
            features.append(action.duration)
        else:
            features.extend([0.0, 0.0, 0.0])
        
        return features
    
    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate distance between two positions."""
        return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 + (pos2[2] - pos1[2])**2)**0.5
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            "is_fitted": self.is_fitted,
            "normal_states_count": len(self.normal_states),
            "anomaly_threshold": self.anomaly_threshold,
            "contamination": self.isolation_forest.contamination
        }
