"""Simple platformer game simulation for testing."""

import time
import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from emergent_playtest_designer.core.types import GameState, Action, ExploitReport, ExploitType, Severity, ActionSequence


@dataclass
class PlatformerGame:
    """Simple platformer game simulation."""
    player_position: Tuple[float, float, float]
    player_health: float
    player_resources: Dict[str, float]
    game_objects: Dict[str, Any]
    physics_state: Dict[str, Any]
    ui_state: Dict[str, Any]
    custom_metrics: Dict[str, float]
    timestamp: float
    
    def __init__(self):
        """Initialize game state."""
        self.player_position = (0.0, 0.0, 0.0)
        self.player_health = 100.0
        self.player_resources = {"coins": 0, "lives": 3}
        self.game_objects = {"platforms": [], "enemies": [], "collectibles": []}
        self.physics_state = {"velocity": [0.0, 0.0, 0.0], "gravity": -9.8}
        self.ui_state = {"score": 0, "level": 1}
        self.custom_metrics = {"jump_count": 0, "damage_taken": 0}
        self.timestamp = time.time()
    
    def get_game_state(self) -> GameState:
        """Get current game state."""
        return GameState(
            timestamp=self.timestamp,
            player_position=self.player_position,
            player_health=self.player_health,
            player_resources=self.player_resources,
            game_objects=self.game_objects,
            physics_state=self.physics_state,
            ui_state=self.ui_state,
            custom_metrics=self.custom_metrics
        )
    
    def apply_action(self, action: Action) -> GameState:
        """Apply action and return new game state."""
        self.timestamp = action.timestamp
        
        if action.action_type == "key_press":
            self._handle_key_press(action.parameters)
        elif action.action_type == "key_release":
            self._handle_key_release(action.parameters)
        elif action.action_type == "mouse_click":
            self._handle_mouse_click(action.parameters)
        elif action.action_type == "mouse_move":
            self._handle_mouse_move(action.parameters)
        
        self._update_physics()
        self._check_boundaries()
        
        return self.get_game_state()
    
    def _handle_key_press(self, parameters: Dict[str, Any]) -> None:
        """Handle key press."""
        key = parameters.get("key", "")
        
        if key == "w" or key == "space":
            self._jump()
        elif key == "a":
            self.physics_state["velocity"][0] = -5.0
        elif key == "d":
            self.physics_state["velocity"][0] = 5.0
        elif key == "s":
            self.physics_state["velocity"][1] = -5.0
    
    def _handle_key_release(self, parameters: Dict[str, Any]) -> None:
        """Handle key release."""
        key = parameters.get("key", "")
        
        if key in ["a", "d"]:
            self.physics_state["velocity"][0] = 0.0
        elif key == "s":
            self.physics_state["velocity"][1] = 0.0
    
    def _handle_mouse_click(self, parameters: Dict[str, Any]) -> None:
        """Handle mouse click."""
        button = parameters.get("button", "left")
        x = parameters.get("x", 0)
        y = parameters.get("y", 0)
        
        if button == "left":
            self._collect_item(x, y)
        elif button == "right":
            self._attack()
    
    def _handle_mouse_move(self, parameters: Dict[str, Any]) -> None:
        """Handle mouse move."""
        delta_x = parameters.get("delta_x", 0)
        delta_y = parameters.get("delta_y", 0)
        
        self.player_position = (
            self.player_position[0] + delta_x * 0.01,
            self.player_position[1] + delta_y * 0.01,
            self.player_position[2]
        )
    
    def _jump(self) -> None:
        """Handle jump action."""
        if self.player_position[1] <= 0.1:
            self.physics_state["velocity"][1] = 10.0
            self.custom_metrics["jump_count"] += 1
    
    def _collect_item(self, x: int, y: int) -> None:
        """Collect item at position."""
        if random.random() < 0.1:
            self.player_resources["coins"] += 1
            self.ui_state["score"] += 10
    
    def _attack(self) -> None:
        """Handle attack action."""
        if random.random() < 0.05:
            self.player_resources["coins"] += 5
            self.ui_state["score"] += 50
    
    def _update_physics(self) -> None:
        """Update physics simulation."""
        dt = 0.016
        
        self.player_position = (
            self.player_position[0] + self.physics_state["velocity"][0] * dt,
            self.player_position[1] + self.physics_state["velocity"][1] * dt,
            self.player_position[2] + self.physics_state["velocity"][2] * dt
        )
        
        self.physics_state["velocity"][1] += self.physics_state["gravity"] * dt
        
        if self.player_position[1] <= 0:
            self.player_position = (self.player_position[0], 0, self.player_position[2])
            self.physics_state["velocity"][1] = 0
    
    def _check_boundaries(self) -> None:
        """Check and enforce boundaries."""
        if abs(self.player_position[0]) > 1000:
            self.player_position = (1000 if self.player_position[0] > 0 else -1000, self.player_position[1], self.player_position[2])
        
        if self.player_position[1] < -100:
            self.player_health = 0
            self.custom_metrics["damage_taken"] += 100


class SimplePlatformer:
    """Simple platformer game for testing."""
    
    def __init__(self):
        """Initialize platformer."""
        self.game = PlatformerGame()
        self.exploit_scenarios = self._create_exploit_scenarios()
    
    def simulate_exploit_scenarios(self) -> List[Dict[str, Any]]:
        """Simulate various exploit scenarios."""
        return self.exploit_scenarios
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific scenario."""
        scenario_name = scenario["name"]
        actions = scenario["actions"]
        
        states = []
        game_states = []
        
        for action_data in actions:
            action = Action(
                action_type=action_data["action_type"],
                parameters=action_data["parameters"],
                timestamp=time.time(),
                duration=action_data.get("duration", 0.1)
            )
            
            state = self.game.apply_action(action)
            game_states.append(state)
            states.append(state.to_dict())
        
        exploits = self._detect_exploits(game_states, actions)
        
        return {
            "scenario_name": scenario_name,
            "states": states,
            "exploits": exploits,
            "final_state": game_states[-1].to_dict() if game_states else {}
        }
    
    def _create_exploit_scenarios(self) -> List[Dict[str, Any]]:
        """Create exploit scenarios."""
        scenarios = []
        
        scenarios.append({
            "name": "Out of Bounds Teleportation",
            "description": "Player teleports outside game boundaries",
            "actions": [
                {"action_type": "key_press", "parameters": {"key": "d"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "d"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "d"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "d"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "d"}, "duration": 0.1},
            ]
        })
        
        scenarios.append({
            "name": "Infinite Resource Gain",
            "description": "Player gains unlimited resources",
            "actions": [
                {"action_type": "mouse_click", "parameters": {"button": "left", "x": 100, "y": 100}, "duration": 0.1},
                {"action_type": "mouse_click", "parameters": {"button": "left", "x": 100, "y": 100}, "duration": 0.1},
                {"action_type": "mouse_click", "parameters": {"button": "left", "x": 100, "y": 100}, "duration": 0.1},
                {"action_type": "mouse_click", "parameters": {"button": "left", "x": 100, "y": 100}, "duration": 0.1},
                {"action_type": "mouse_click", "parameters": {"button": "left", "x": 100, "y": 100}, "duration": 0.1},
            ]
        })
        
        scenarios.append({
            "name": "Stuck State",
            "description": "Player gets stuck in same position",
            "actions": [
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
            ]
        })
        
        scenarios.append({
            "name": "Infinite Loop",
            "description": "Game enters infinite loop",
            "actions": [
                {"action_type": "key_press", "parameters": {"key": "w"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "w"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "w"}, "duration": 0.1},
                {"action_type": "key_press", "parameters": {"key": "s"}, "duration": 0.1},
            ]
        })
        
        return scenarios
    
    def _detect_exploits(self, states: List[GameState], actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect exploits in the scenario."""
        exploits = []
        
        if len(states) < 2:
            return exploits
        
        for i in range(1, len(states)):
            prev_state = states[i-1]
            curr_state = states[i]
            
            position_change = self._calculate_position_change(prev_state.player_position, curr_state.player_position)
            
            if position_change > 100:
                exploits.append({
                    "type": "out_of_bounds",
                    "description": f"Player teleported {position_change:.2f} units",
                    "confidence": min(1.0, position_change / 200),
                    "timestamp": curr_state.timestamp
                })
            
            resource_change = sum(curr_state.player_resources.values()) - sum(prev_state.player_resources.values())
            
            if resource_change > 10:
                exploits.append({
                    "type": "infinite_resources",
                    "description": f"Player gained {resource_change:.0f} resources instantly",
                    "confidence": min(1.0, resource_change / 50),
                    "timestamp": curr_state.timestamp
                })
            
            if curr_state.player_health <= 0:
                exploits.append({
                    "type": "stuck_state",
                    "description": "Player died/stuck",
                    "confidence": 1.0,
                    "timestamp": curr_state.timestamp
                })
        
        return exploits
    
    def _calculate_position_change(self, pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
        """Calculate position change."""
        return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 + (pos2[2] - pos1[2])**2)**0.5


def main():
    """Main function for testing."""
    platformer = SimplePlatformer()
    scenarios = platformer.simulate_exploit_scenarios()
    
    print("Running exploit scenarios...")
    
    for scenario in scenarios:
        print(f"\nRunning scenario: {scenario['name']}")
        result = platformer.run_scenario(scenario)
        
        print(f"Exploits found: {len(result['exploits'])}")
        for exploit in result['exploits']:
            print(f"  - {exploit['type']}: {exploit['description']} (confidence: {exploit['confidence']:.2f})")


if __name__ == "__main__":
    main()