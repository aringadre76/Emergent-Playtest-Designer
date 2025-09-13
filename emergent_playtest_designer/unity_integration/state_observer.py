"""Game state observation and monitoring."""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState


@dataclass
class StateChange:
    """Represents a change in game state."""
    timestamp: float
    field: str
    old_value: Any
    new_value: Any
    change_type: str


class StateObserver:
    """Observes and tracks changes in game state."""
    
    def __init__(self, update_frequency: float = 0.1):
        """Initialize state observer."""
        self.update_frequency = update_frequency
        self.current_state: Optional[GameState] = None
        self.previous_state: Optional[GameState] = None
        self.state_history: List[GameState] = []
        self.state_changes: List[StateChange] = []
        self.callbacks: List[Callable[[GameState], None]] = []
        self.is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
    def start_monitoring(self) -> None:
        """Start monitoring game state."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("State monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring game state."""
        self.is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        logger.info("State monitoring stopped")
    
    def update_state(self, new_state: GameState) -> None:
        """Update current state and detect changes."""
        with self._lock:
            self.previous_state = self.current_state
            self.current_state = new_state
            
            if self.previous_state:
                changes = self._detect_changes(self.previous_state, new_state)
                self.state_changes.extend(changes)
            
            self.state_history.append(new_state)
            
            for callback in self.callbacks:
                try:
                    callback(new_state)
                except Exception as e:
                    logger.error(f"State callback error: {e}")
    
    def register_callback(self, callback: Callable[[GameState], None]) -> None:
        """Register callback for state updates."""
        self.callbacks.append(callback)
    
    def get_current_state(self) -> Optional[GameState]:
        """Get current game state."""
        with self._lock:
            return self.current_state
    
    def get_state_history(self, limit: Optional[int] = None) -> List[GameState]:
        """Get state history."""
        with self._lock:
            if limit:
                return self.state_history[-limit:]
            return self.state_history.copy()
    
    def get_recent_changes(self, limit: int = 100) -> List[StateChange]:
        """Get recent state changes."""
        with self._lock:
            return self.state_changes[-limit:]
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous state patterns."""
        anomalies = []
        
        if len(self.state_history) < 10:
            return anomalies
        
        recent_states = self.state_history[-10:]
        
        anomalies.extend(self._detect_position_anomalies(recent_states))
        anomalies.extend(self._detect_health_anomalies(recent_states))
        anomalies.extend(self._detect_resource_anomalies(recent_states))
        anomalies.extend(self._detect_physics_anomalies(recent_states))
        
        return anomalies
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_monitoring:
            time.sleep(self.update_frequency)
    
    def _detect_changes(self, old_state: GameState, new_state: GameState) -> List[StateChange]:
        """Detect changes between two states."""
        changes = []
        
        if old_state.player_position != new_state.player_position:
            changes.append(StateChange(
                timestamp=new_state.timestamp,
                field="player_position",
                old_value=old_state.player_position,
                new_value=new_state.player_position,
                change_type="position"
            ))
        
        if old_state.player_health != new_state.player_health:
            changes.append(StateChange(
                timestamp=new_state.timestamp,
                field="player_health",
                old_value=old_state.player_health,
                new_value=new_state.player_health,
                change_type="health"
            ))
        
        for key, new_value in new_state.player_resources.items():
            old_value = old_state.player_resources.get(key, 0)
            if old_value != new_value:
                changes.append(StateChange(
                    timestamp=new_state.timestamp,
                    field=f"resource_{key}",
                    old_value=old_value,
                    new_value=new_value,
                    change_type="resource"
                ))
        
        return changes
    
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
                        "description": f"Player moved {distance:.2f} units in {time_diff:.3f}s"
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
                    "description": "Player died"
                })
            elif curr_health > prev_health and prev_health > 0:
                heal_amount = curr_health - prev_health
                if heal_amount > 50:
                    anomalies.append({
                        "type": "rapid_healing",
                        "timestamp": states[i].timestamp,
                        "heal_amount": heal_amount,
                        "description": f"Player healed {heal_amount:.1f} health instantly"
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
                            "description": f"Gained {gain:.0f} {resource} instantly"
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
                        "description": f"Player moving at {speed:.1f} units/s"
                    })
        
        return anomalies
    
    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate distance between two positions."""
        return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 + (pos2[2] - pos1[2])**2)**0.5
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get state observation statistics."""
        with self._lock:
            return {
                "total_states": len(self.state_history),
                "total_changes": len(self.state_changes),
                "monitoring_active": self.is_monitoring,
                "current_timestamp": time.time(),
            }
