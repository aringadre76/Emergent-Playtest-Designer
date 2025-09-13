"""
Simple platformer game example for testing the Emergent Playtest Designer.

This is a minimal Unity-style game simulation that can be used to test
the exploit detection system.
"""

import time
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from emergent_playtest_designer.core.types import GameState, Action


@dataclass
class Player:
    """Represents the player character."""
    position: Tuple[float, float, float]
    velocity: Tuple[float, float, float]
    health: float
    resources: Dict[str, float]
    is_grounded: bool
    is_dead: bool


@dataclass
class Platform:
    """Represents a platform in the game."""
    position: Tuple[float, float, float]
    size: Tuple[float, float, float]


class SimplePlatformer:
    """Simple platformer game simulation."""
    
    def __init__(self):
        """Initialize the game."""
        self.player = Player(
            position=(0.0, 0.0, 0.0),
            velocity=(0.0, 0.0, 0.0),
            health=100.0,
            resources={"coins": 0, "lives": 3},
            is_grounded=True,
            is_dead=False
        )
        
        self.platforms = [
            Platform(position=(0, -1, 0), size=(10, 1, 10)),
            Platform(position=(5, 0, 0), size=(3, 1, 3)),
            Platform(position=(-5, 2, 0), size=(2, 1, 2)),
        ]
        
        self.gravity = -9.8
        self.jump_force = 15.0
        self.move_speed = 5.0
        self.boundaries = (-50, 50, -50, 50, -50, 50)
        
        self.frame_count = 0
        self.last_time = time.time()
        
    def get_game_state(self) -> GameState:
        """Get current game state."""
        current_time = time.time()
        
        return GameState(
            timestamp=current_time,
            player_position=self.player.position,
            player_health=self.player.health,
            player_resources=self.player.resources,
            game_objects={
                "platforms": [{"position": p.position, "size": p.size} for p in self.platforms]
            },
            physics_state={
                "velocity": self.player.velocity,
                "acceleration": (0, self.gravity, 0),
                "is_grounded": self.player.is_grounded
            },
            ui_state={
                "score": self.player.resources["coins"],
                "lives": self.player.resources["lives"],
                "frame": self.frame_count
            },
            custom_metrics={
                "distance_traveled": abs(self.player.position[0]) + abs(self.player.position[1]) + abs(self.player.position[2]),
                "jump_count": 0
            }
        )
    
    def process_action(self, action: Action) -> bool:
        """Process an action and update game state."""
        if self.player.is_dead:
            return False
        
        dt = 0.016  # 60 FPS
        
        if action.action_type == "key_press":
            key = action.parameters.get("key", "")
            
            if key == "w" and self.player.is_grounded:
                self.player.velocity = (self.player.velocity[0], self.jump_force, self.player.velocity[2])
                self.player.is_grounded = False
            
            elif key == "a":
                self.player.velocity = (-self.move_speed, self.player.velocity[1], self.player.velocity[2])
            
            elif key == "d":
                self.player.velocity = (self.move_speed, self.player.velocity[1], self.player.velocity[2])
            
            elif key == "s":
                self.player.velocity = (self.player.velocity[0], self.player.velocity[1], -self.move_speed)
        
        elif action.action_type == "key_release":
            key = action.parameters.get("key", "")
            
            if key in ["a", "d"]:
                self.player.velocity = (0, self.player.velocity[1], self.player.velocity[2])
            
            elif key == "s":
                self.player.velocity = (self.player.velocity[0], self.player.velocity[1], 0)
        
        elif action.action_type == "mouse_click":
            button = action.parameters.get("button", "")
            x = action.parameters.get("x", 0)
            y = action.parameters.get("y", 0)
            
            if button == "left":
                self.player.resources["coins"] += 1
        
        self._update_physics(dt)
        self._check_collisions()
        self._check_boundaries()
        
        self.frame_count += 1
        return True
    
    def _update_physics(self, dt: float):
        """Update physics simulation."""
        # Apply gravity
        new_velocity_y = self.player.velocity[1] + self.gravity * dt
        self.player.velocity = (self.player.velocity[0], new_velocity_y, self.player.velocity[2])
        
        # Update position
        new_x = self.player.position[0] + self.player.velocity[0] * dt
        new_y = self.player.position[1] + self.player.velocity[1] * dt
        new_z = self.player.position[2] + self.player.velocity[2] * dt
        
        self.player.position = (new_x, new_y, new_z)
    
    def _check_collisions(self):
        """Check collisions with platforms."""
        player_x, player_y, player_z = self.player.position
        
        for platform in self.platforms:
            px, py, pz = platform.position
            sx, sy, sz = platform.size
            
            # Check if player is on top of platform
            if (px - sx/2 <= player_x <= px + sx/2 and
                py - sy/2 <= player_y <= py + sy/2 + 0.5 and
                pz - sz/2 <= player_z <= pz + sz/2):
                
                if self.player.velocity[1] <= 0:  # Falling down
                    self.player.position = (player_x, py + sy/2 + 0.5, player_z)
                    self.player.velocity = (self.player.velocity[0], 0, self.player.velocity[2])
                    self.player.is_grounded = True
    
    def _check_boundaries(self):
        """Check if player is out of bounds."""
        x, y, z = self.player.position
        min_x, max_x, min_y, max_y, min_z, max_z = self.boundaries
        
        if x < min_x or x > max_x or y < min_y or y > max_y or z < min_z or z > max_z:
            # Player is out of bounds - this is an exploit!
            self.player.health = 0
            self.player.is_dead = True
    
    def simulate_exploit_scenarios(self) -> List[Dict[str, Any]]:
        """Simulate various exploit scenarios for testing."""
        scenarios = []
        
        # Scenario 1: Out of bounds exploit
        scenarios.append({
            "name": "Out of Bounds",
            "description": "Player moves outside game boundaries",
            "actions": [
                Action(action_type="key_press", parameters={"key": "d"}, timestamp=0.0, duration=10.0),
            ],
            "expected_exploit": "out_of_bounds"
        })
        
        # Scenario 2: Infinite coins exploit
        scenarios.append({
            "name": "Infinite Coins",
            "description": "Player clicks rapidly to gain infinite coins",
            "actions": [
                Action(action_type="mouse_click", parameters={"button": "left", "x": 100, "y": 100}, timestamp=i*0.01, duration=0.01)
                for i in range(100)
            ],
            "expected_exploit": "infinite_resources"
        })
        
        # Scenario 3: Stuck state exploit
        scenarios.append({
            "name": "Stuck State",
            "description": "Player gets stuck in a wall",
            "actions": [
                Action(action_type="key_press", parameters={"key": "w"}, timestamp=0.0, duration=0.1),
                Action(action_type="key_press", parameters={"key": "a"}, timestamp=0.1, duration=10.0),
            ],
            "expected_exploit": "stuck_state"
        })
        
        return scenarios
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific scenario and return results."""
        self.__init__()  # Reset game state
        
        initial_state = self.get_game_state()
        states = [initial_state]
        
        for action in scenario["actions"]:
            success = self.process_action(action)
            if not success:
                break
            
            current_state = self.get_game_state()
            states.append(current_state)
        
        final_state = states[-1]
        
        # Detect exploits
        exploits = []
        
        # Check for out of bounds
        x, y, z = final_state.player_position
        min_x, max_x, min_y, max_y, min_z, max_z = self.boundaries
        if x < min_x or x > max_x or y < min_y or y > max_y or z < min_z or z > max_z:
            exploits.append({
                "type": "out_of_bounds",
                "description": f"Player at position {final_state.player_position} is out of bounds",
                "confidence": 1.0
            })
        
        # Check for infinite resources
        if final_state.player_resources.get("coins", 0) > 50:
            exploits.append({
                "type": "infinite_resources",
                "description": f"Player has {final_state.player_resources['coins']} coins (suspicious)",
                "confidence": 0.8
            })
        
        # Check for stuck state
        if final_state.player_health <= 0:
            exploits.append({
                "type": "stuck_state",
                "description": "Player is dead/stuck",
                "confidence": 0.9
            })
        
        return {
            "scenario": scenario["name"],
            "initial_state": initial_state.to_dict(),
            "final_state": final_state.to_dict(),
            "states": [state.to_dict() for state in states],
            "exploits": exploits,
            "success": len(exploits) > 0
        }


def main():
    """Run example scenarios."""
    game = SimplePlatformer()
    scenarios = game.simulate_exploit_scenarios()
    
    print("Running exploit scenarios...")
    
    for scenario in scenarios:
        print(f"\nRunning scenario: {scenario['name']}")
        result = game.run_scenario(scenario)
        
        print(f"Success: {result['success']}")
        print(f"Exploits found: {len(result['exploits'])}")
        
        for exploit in result['exploits']:
            print(f"  - {exploit['type']}: {exploit['description']} (confidence: {exploit['confidence']:.1%})")


if __name__ == "__main__":
    main()
