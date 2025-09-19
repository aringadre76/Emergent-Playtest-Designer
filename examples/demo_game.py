"""
Demo game simulation for testing the Emergent Playtest Designer.
This simulates a simple platformer game without requiring Unity.
"""

import asyncio
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class ExploitType(Enum):
    OUT_OF_BOUNDS = "out_of_bounds"
    INFINITE_RESOURCES = "infinite_resources"
    STUCK_STATE = "stuck_state"
    INFINITE_LOOP = "infinite_loop"
    CLIPPING = "clipping"
    SEQUENCE_BREAK = "sequence_break"

@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    health: int = 100
    score: int = 0
    coins: int = 0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    on_ground: bool = False
    invulnerable: bool = False
    invulnerability_timer: float = 0.0

@dataclass
class GameWorld:
    width: int = 1000
    height: int = 600
    platforms: List[Tuple[int, int, int, int]] = None  # x, y, width, height
    enemies: List[Dict[str, Any]] = None
    collectibles: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = [
                (0, 500, 200, 20),      # Ground platform
                (300, 400, 150, 20),    # Mid platform
                (600, 300, 100, 20),    # High platform
                (800, 200, 120, 20),    # Top platform
            ]
        if self.enemies is None:
            self.enemies = [
                {"x": 250, "y": 480, "type": "goomba", "health": 1},
                {"x": 350, "y": 380, "type": "spike", "health": 1},
                {"x": 650, "y": 280, "type": "flying", "health": 2},
            ]
        if self.collectibles is None:
            self.collectibles = [
                {"x": 320, "y": 350, "type": "coin", "value": 10},
                {"x": 620, "y": 250, "type": "coin", "value": 10},
                {"x": 850, "y": 150, "type": "powerup", "value": 50},
            ]

class DemoGame:
    """Simple platformer game simulation for testing exploit detection."""
    
    def __init__(self):
        self.state = GameState.MENU
        self.player = Player()
        self.world = GameWorld()
        self.frame_count = 0
        self.exploits_detected = []
        self.action_history = []
        self.max_history = 1000
        
        # Game physics constants
        self.GRAVITY = 0.5
        self.JUMP_FORCE = -12
        self.MOVE_SPEED = 5
        self.FRICTION = 0.8
        
        # Exploit detection thresholds
        self.OUT_OF_BOUNDS_THRESHOLD = 50
        self.STUCK_THRESHOLD = 300  # frames
        self.INFINITE_LOOP_THRESHOLD = 100
        
    async def start_game(self) -> bool:
        """Start the game."""
        self.state = GameState.PLAYING
        self.player = Player()
        self.frame_count = 0
        self.exploits_detected = []
        self.action_history = []
        return True
        
    async def stop_game(self) -> bool:
        """Stop the game."""
        self.state = GameState.GAME_OVER
        return True
        
    async def process_input(self, action: str, value: float = 1.0) -> bool:
        """Process player input."""
        if self.state != GameState.PLAYING:
            return False
            
        # Record action for exploit detection
        self.action_history.append({
            "frame": self.frame_count,
            "action": action,
            "value": value,
            "player_state": {
                "x": self.player.x,
                "y": self.player.y,
                "health": self.player.health,
                "score": self.player.score,
                "coins": self.player.coins
            }
        })
        
        # Keep history manageable
        if len(self.action_history) > self.max_history:
            self.action_history = self.action_history[-self.max_history:]
            
        # Process movement
        if action == "move_right":
            self.player.velocity_x = self.MOVE_SPEED * value
        elif action == "move_left":
            self.player.velocity_x = -self.MOVE_SPEED * value
        elif action == "jump" and self.player.on_ground:
            self.player.velocity_y = self.JUMP_FORCE * value
            self.player.on_ground = False
        elif action == "attack":
            await self._process_attack()
            
        return True
        
    async def update(self) -> Dict[str, Any]:
        """Update game state."""
        if self.state != GameState.PLAYING:
            return self._get_game_state()
            
        self.frame_count += 1
        
        # Apply physics
        await self._apply_physics()
        
        # Check collisions
        await self._check_collisions()
        
        # Update enemies
        await self._update_enemies()
        
        # Check for exploits
        await self._check_exploits()
        
        return self._get_game_state()
        
    async def _apply_physics(self):
        """Apply physics to player."""
        # Apply gravity
        if not self.player.on_ground:
            self.player.velocity_y += self.GRAVITY
            
        # Apply friction
        self.player.velocity_x *= self.FRICTION
        
        # Update position
        self.player.x += self.player.velocity_x
        self.player.y += self.player.velocity_y
        
        # Update invulnerability timer
        if self.player.invulnerable:
            self.player.invulnerability_timer -= 1
            if self.player.invulnerability_timer <= 0:
                self.player.invulnerable = False
                
    async def _check_collisions(self):
        """Check collisions with platforms and objects."""
        # Check platform collisions
        self.player.on_ground = False
        for platform in self.world.platforms:
            px, py, pw, ph = platform
            if (self.player.x < px + pw and 
                self.player.x + 20 > px and
                self.player.y < py + ph and
                self.player.y + 20 > py):
                
                # Landing on top of platform
                if self.player.velocity_y > 0 and self.player.y < py:
                    self.player.y = py - 20
                    self.player.velocity_y = 0
                    self.player.on_ground = True
                    
        # Check enemy collisions
        for enemy in self.world.enemies[:]:  # Copy to avoid modification during iteration
            if (self.player.x < enemy["x"] + 20 and
                self.player.x + 20 > enemy["x"] and
                self.player.y < enemy["y"] + 20 and
                self.player.y + 20 > enemy["y"]):
                
                if not self.player.invulnerable:
                    self.player.health -= 10
                    self.player.invulnerable = True
                    self.player.invulnerability_timer = 60  # 1 second at 60fps
                    
        # Check collectible collisions
        for collectible in self.world.collectibles[:]:
            if (self.player.x < collectible["x"] + 10 and
                self.player.x + 20 > collectible["x"] and
                self.player.y < collectible["y"] + 10 and
                self.player.y + 20 > collectible["y"]):
                
                if collectible["type"] == "coin":
                    self.player.coins += collectible["value"]
                    self.player.score += collectible["value"]
                elif collectible["type"] == "powerup":
                    self.player.score += collectible["value"]
                    
                self.world.collectibles.remove(collectible)
                
    async def _update_enemies(self):
        """Update enemy AI."""
        for enemy in self.world.enemies:
            if enemy["type"] == "goomba":
                enemy["x"] += random.choice([-1, 1]) * 0.5
            elif enemy["type"] == "flying":
                enemy["x"] += random.choice([-2, 2]) * 0.3
                enemy["y"] += random.choice([-1, 1]) * 0.2
                
    async def _process_attack(self):
        """Process attack action."""
        # Simple attack - damage nearby enemies
        for enemy in self.world.enemies[:]:
            distance = ((self.player.x - enemy["x"])**2 + (self.player.y - enemy["y"])**2)**0.5
            if distance < 50:  # Attack range
                enemy["health"] -= 1
                if enemy["health"] <= 0:
                    self.world.enemies.remove(enemy)
                    self.player.score += 100
                    
    async def _check_exploits(self):
        """Check for various exploits."""
        # Out of bounds exploit
        if (self.player.x < -self.OUT_OF_BOUNDS_THRESHOLD or 
            self.player.x > self.world.width + self.OUT_OF_BOUNDS_THRESHOLD or
            self.player.y < -self.OUT_OF_BOUNDS_THRESHOLD or
            self.player.y > self.world.height + self.OUT_OF_BOUNDS_THRESHOLD):
            
            await self._detect_exploit(ExploitType.OUT_OF_BOUNDS, {
                "player_x": self.player.x,
                "player_y": self.player.y,
                "world_bounds": (self.world.width, self.world.height)
            })
            
        # Infinite resources exploit (coins growing too fast)
        if len(self.action_history) > 10:
            recent_coins = [h["player_state"]["coins"] for h in self.action_history[-10:]]
            if len(set(recent_coins)) == 1 and recent_coins[0] > 1000:
                await self._detect_exploit(ExploitType.INFINITE_RESOURCES, {
                    "coin_count": self.player.coins,
                    "coin_history": recent_coins
                })
                
        # Stuck state exploit
        if len(self.action_history) > self.STUCK_THRESHOLD:
            recent_positions = [(h["player_state"]["x"], h["player_state"]["y"]) 
                              for h in self.action_history[-self.STUCK_THRESHOLD:]]
            if len(set(recent_positions)) < 5:  # Player hasn't moved much
                await self._detect_exploit(ExploitType.STUCK_STATE, {
                    "position_history": recent_positions[-10:],
                    "frames_stuck": self.STUCK_THRESHOLD
                })
                
        # Infinite loop exploit (repeating action patterns)
        if len(self.action_history) > self.INFINITE_LOOP_THRESHOLD:
            recent_actions = [h["action"] for h in self.action_history[-self.INFINITE_LOOP_THRESHOLD:]]
            # Check for repetitive patterns
            for pattern_length in range(2, 10):
                if self._has_repeating_pattern(recent_actions, pattern_length):
                    await self._detect_exploit(ExploitType.INFINITE_LOOP, {
                        "pattern": recent_actions[-pattern_length:],
                        "pattern_length": pattern_length,
                        "repetitions": len(recent_actions) // pattern_length
                    })
                    break
                    
    def _has_repeating_pattern(self, actions: List[str], pattern_length: int) -> bool:
        """Check if actions contain a repeating pattern."""
        if len(actions) < pattern_length * 3:
            return False
            
        pattern = actions[-pattern_length:]
        for i in range(len(actions) - pattern_length * 2, len(actions) - pattern_length):
            if actions[i:i+pattern_length] == pattern:
                return True
        return False
        
    async def _detect_exploit(self, exploit_type: ExploitType, data: Dict[str, Any]):
        """Record detected exploit."""
        exploit = {
            "id": f"exploit_{len(self.exploits_detected)}_{self.frame_count}",
            "type": exploit_type.value,
            "frame": self.frame_count,
            "severity": self._calculate_severity(exploit_type, data),
            "description": self._generate_description(exploit_type, data),
            "data": data,
            "timestamp": time.time()
        }
        
        self.exploits_detected.append(exploit)
        
    def _calculate_severity(self, exploit_type: ExploitType, data: Dict[str, Any]) -> str:
        """Calculate exploit severity."""
        severity_map = {
            ExploitType.OUT_OF_BOUNDS: "high",
            ExploitType.INFINITE_RESOURCES: "critical",
            ExploitType.STUCK_STATE: "medium",
            ExploitType.INFINITE_LOOP: "high",
            ExploitType.CLIPPING: "medium",
            ExploitType.SEQUENCE_BREAK: "high"
        }
        return severity_map.get(exploit_type, "low")
        
    def _generate_description(self, exploit_type: ExploitType, data: Dict[str, Any]) -> str:
        """Generate exploit description."""
        descriptions = {
            ExploitType.OUT_OF_BOUNDS: f"Player moved outside game boundaries at position ({data.get('player_x', 0):.1f}, {data.get('player_y', 0):.1f})",
            ExploitType.INFINITE_RESOURCES: f"Player has accumulated {data.get('coin_count', 0)} coins, indicating possible infinite resource exploit",
            ExploitType.STUCK_STATE: f"Player has been stuck in same position for {data.get('frames_stuck', 0)} frames",
            ExploitType.INFINITE_LOOP: f"Detected repeating action pattern: {data.get('pattern', [])}",
            ExploitType.CLIPPING: "Player passed through solid objects",
            ExploitType.SEQUENCE_BREAK: "Game sequence was broken or skipped"
        }
        return descriptions.get(exploit_type, "Unknown exploit detected")
        
    def _get_game_state(self) -> Dict[str, Any]:
        """Get current game state."""
        return {
            "frame": self.frame_count,
            "state": self.state.value,
            "player": {
                "x": self.player.x,
                "y": self.player.y,
                "health": self.player.health,
                "score": self.player.score,
                "coins": self.player.coins,
                "velocity_x": self.player.velocity_x,
                "velocity_y": self.player.velocity_y,
                "on_ground": self.player.on_ground,
                "invulnerable": self.player.invulnerable
            },
            "world": {
                "width": self.world.width,
                "height": self.world.height,
                "platforms": self.world.platforms,
                "enemies": self.world.enemies,
                "collectibles": self.world.collectibles
            },
            "exploits": self.exploits_detected,
            "action_history_length": len(self.action_history)
        }
        
    def get_exploits(self) -> List[Dict[str, Any]]:
        """Get all detected exploits."""
        return self.exploits_detected.copy()
        
    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get action history."""
        return self.action_history.copy()

# Example usage and testing
async def run_demo():
    """Run a demo of the game with automated testing."""
    game = DemoGame()
    
    print("Starting demo game...")
    await game.start_game()
    
    # Simulate some gameplay
    actions = [
        ("move_right", 1.0),
        ("move_right", 1.0),
        ("jump", 1.0),
        ("move_left", 1.0),
        ("attack", 1.0),
        ("move_right", 1.0),
        ("jump", 1.0),
    ]
    
    for i in range(1000):  # Run for 1000 frames
        # Randomly select actions
        if i % 10 == 0:  # Every 10 frames
            action, value = random.choice(actions)
            await game.process_input(action, value)
            
        # Update game
        state = await game.update()
        
        # Print status every 100 frames
        if i % 100 == 0:
            print(f"Frame {i}: Player at ({state['player']['x']:.1f}, {state['player']['y']:.1f}), "
                  f"Health: {state['player']['health']}, Score: {state['player']['score']}, "
                  f"Coins: {state['player']['coins']}")
                  
        # Check for exploits
        exploits = game.get_exploits()
        if exploits and len(exploits) > len(game.exploits_detected) - 1:
            latest_exploit = exploits[-1]
            print(f"EXPLOIT DETECTED: {latest_exploit['type']} - {latest_exploit['description']}")
            
        await asyncio.sleep(0.016)  # ~60 FPS
        
    await game.stop_game()
    
    print(f"\nGame completed!")
    print(f"Final score: {game.player.score}")
    print(f"Final coins: {game.player.coins}")
    print(f"Exploits detected: {len(game.get_exploits())}")
    
    for exploit in game.get_exploits():
        print(f"- {exploit['type']}: {exploit['description']}")

if __name__ == "__main__":
    asyncio.run(run_demo())
