"""Input injection system for Unity games."""

import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import Action


@dataclass
class InputEvent:
    """Represents an input event."""
    event_type: str
    key: str
    value: float
    timestamp: float
    duration: float = 0.0


class InputInjector:
    """Injects inputs into Unity games."""
    
    def __init__(self):
        """Initialize input injector."""
        self.active_inputs: Dict[str, InputEvent] = {}
        self.input_history: List[InputEvent] = []
        self.is_recording = False
        self._lock = threading.Lock()
        
    def inject_action(self, action: Action) -> bool:
        """Inject action into the game."""
        try:
            with self._lock:
                if action.action_type == "key_press":
                    return self._inject_key_press(action)
                elif action.action_type == "key_release":
                    return self._inject_key_release(action)
                elif action.action_type == "mouse_click":
                    return self._inject_mouse_click(action)
                elif action.action_type == "mouse_move":
                    return self._inject_mouse_move(action)
                elif action.action_type == "joystick_input":
                    return self._inject_joystick_input(action)
                else:
                    logger.warning(f"Unknown action type: {action.action_type}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to inject action: {e}")
            return False
    
    def start_recording(self) -> None:
        """Start recording input events."""
        with self._lock:
            self.is_recording = True
            self.input_history.clear()
        logger.info("Input recording started")
    
    def stop_recording(self) -> List[InputEvent]:
        """Stop recording and return input history."""
        with self._lock:
            self.is_recording = False
            return self.input_history.copy()
    
    def get_active_inputs(self) -> Dict[str, InputEvent]:
        """Get currently active inputs."""
        with self._lock:
            return self.active_inputs.copy()
    
    def clear_active_inputs(self) -> None:
        """Clear all active inputs."""
        with self._lock:
            self.active_inputs.clear()
    
    def _inject_key_press(self, action: Action) -> bool:
        """Inject key press event."""
        key = action.parameters.get("key", "")
        if not key:
            return False
        
        event = InputEvent(
            event_type="key_press",
            key=key,
            value=1.0,
            timestamp=action.timestamp,
            duration=action.duration
        )
        
        self._record_event(event)
        self.active_inputs[key] = event
        
        logger.debug(f"Key press injected: {key}")
        return True
    
    def _inject_key_release(self, action: Action) -> bool:
        """Inject key release event."""
        key = action.parameters.get("key", "")
        if not key:
            return False
        
        event = InputEvent(
            event_type="key_release",
            key=key,
            value=0.0,
            timestamp=action.timestamp,
            duration=action.duration
        )
        
        self._record_event(event)
        if key in self.active_inputs:
            del self.active_inputs[key]
        
        logger.debug(f"Key release injected: {key}")
        return True
    
    def _inject_mouse_click(self, action: Action) -> bool:
        """Inject mouse click event."""
        button = action.parameters.get("button", "left")
        x = action.parameters.get("x", 0)
        y = action.parameters.get("y", 0)
        
        event = InputEvent(
            event_type="mouse_click",
            key=f"mouse_{button}",
            value=1.0,
            timestamp=action.timestamp,
            duration=action.duration
        )
        
        self._record_event(event)
        
        logger.debug(f"Mouse click injected: {button} at ({x}, {y})")
        return True
    
    def _inject_mouse_move(self, action: Action) -> bool:
        """Inject mouse move event."""
        x = action.parameters.get("x", 0)
        y = action.parameters.get("y", 0)
        delta_x = action.parameters.get("delta_x", 0)
        delta_y = action.parameters.get("delta_y", 0)
        
        event = InputEvent(
            event_type="mouse_move",
            key="mouse_move",
            value=1.0,
            timestamp=action.timestamp,
            duration=action.duration
        )
        
        self._record_event(event)
        
        logger.debug(f"Mouse move injected: ({x}, {y}) delta: ({delta_x}, {delta_y})")
        return True
    
    def _inject_joystick_input(self, action: Action) -> bool:
        """Inject joystick input event."""
        axis = action.parameters.get("axis", "")
        value = action.parameters.get("value", 0.0)
        
        if not axis:
            return False
        
        event = InputEvent(
            event_type="joystick_input",
            key=f"joystick_{axis}",
            value=value,
            timestamp=action.timestamp,
            duration=action.duration
        )
        
        self._record_event(event)
        
        logger.debug(f"Joystick input injected: {axis} = {value}")
        return True
    
    def _record_event(self, event: InputEvent) -> None:
        """Record input event if recording is active."""
        if self.is_recording:
            self.input_history.append(event)
    
    def generate_action_sequence(self, start_time: float, end_time: float) -> List[Action]:
        """Generate action sequence from recorded events."""
        actions = []
        
        with self._lock:
            for event in self.input_history:
                if start_time <= event.timestamp <= end_time:
                    action = Action(
                        action_type=event.event_type,
                        parameters={
                            "key": event.key,
                            "value": event.value,
                        },
                        timestamp=event.timestamp,
                        duration=event.duration
                    )
                    actions.append(action)
        
        return sorted(actions, key=lambda a: a.timestamp)
    
    def simulate_input_sequence(self, actions: List[Action], delay: float = 0.0) -> bool:
        """Simulate a sequence of inputs with optional delay."""
        try:
            for action in actions:
                if not self.inject_action(action):
                    logger.warning(f"Failed to inject action: {action.action_type}")
                    return False
                
                if delay > 0:
                    time.sleep(delay)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate input sequence: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get input injection statistics."""
        with self._lock:
            return {
                "total_events": len(self.input_history),
                "active_inputs": len(self.active_inputs),
                "recording_active": self.is_recording,
                "current_timestamp": time.time(),
            }
