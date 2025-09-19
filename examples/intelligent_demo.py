"""
Intelligent demo game that uses real AI algorithms for exploit discovery.
This demonstrates the actual core functionality of the Emergent Playtest Designer.
"""

import asyncio
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# Import our real AI components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from emergent_playtest_designer.agents.intelligent_explorer import IntelligentExplorer
from emergent_playtest_designer.detection.real_exploit_detector import RealExploitDetector
from emergent_playtest_designer.core.types import GameState as CoreGameState, Action, AgentConfig, ExploitReport
from emergent_playtest_designer.llm import OllamaClient
from emergent_playtest_designer.mocks import MockDatabase


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

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
    platforms: List[Tuple[int, int, int, int]] = None
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

class IntelligentDemoGame:
    """
    Intelligent demo game that uses real AI algorithms for exploit discovery.
    This demonstrates the actual core functionality of the system.
    """
    
    def __init__(self):
        self.state = GameState.MENU
        self.player = Player()
        self.world = GameWorld()
        self.frame_count = 0
        
        # Initialize real AI components
        agent_config = AgentConfig(
            agent_type="intelligent_explorer",
            exploration_rate=0.1,
            learning_rate=0.001,
            memory_size=10000,
            batch_size=32,
            target_update_frequency=1000,
            novelty_threshold=0.5,
            max_episode_length=1000
        )
        
        self.intelligent_explorer = IntelligentExplorer(agent_config)
        self.exploit_detector = RealExploitDetector({
            "out_of_bounds_threshold": 1000,
            "infinite_resource_threshold": 10000,
            "stuck_state_threshold": 300,
            "infinite_loop_threshold": 50
        })
        
        # Real LLM client with Ollama + Llama 3.2 3B
        self.llm_client = OllamaClient()
        self.database = MockDatabase()
        
        # Game physics constants
        self.GRAVITY = 0.5
        self.JUMP_FORCE = -12
        self.MOVE_SPEED = 5
        self.FRICTION = 0.8
        
        # Exploit tracking
        self.exploits_detected = []
        self.session_id = f"intelligent_session_{int(time.time())}"
        
    async def start_game(self) -> bool:
        """Start the intelligent game."""
        self.state = GameState.PLAYING
        self.player = Player()
        self.frame_count = 0
        self.exploits_detected = []
        
        # Save session to database
        self.database.save_session(self.session_id, "intelligent_demo", {
            "duration": 0,
            "agent_type": "intelligent_explorer",
            "timestamp": time.time()
        })
        
        return True
        
    async def stop_game(self) -> bool:
        """Stop the game."""
        self.state = GameState.GAME_OVER
        return True
        
    async def process_intelligent_input(self, current_state: CoreGameState) -> bool:
        """
        Process intelligent input using real AI algorithms.
        This is the core intelligence that replaces random action selection.
        """
        if self.state != GameState.PLAYING:
            return False
            
        # Get available actions
        available_actions = ["move_right", "move_left", "jump", "attack", "wait"]
        
        # Use intelligent explorer to select action
        action = self.intelligent_explorer.select_action(current_state, available_actions)
        
        # Process the selected action
        await self._process_action(action)
        
        return True
        
    async def _process_action(self, action: Action):
        """Process the selected action."""
        # Apply movement
        if action.action_type == "move_right":
            intensity = action.parameters.get("intensity", 1.0)
            self.player.velocity_x = self.MOVE_SPEED * intensity
        elif action.action_type == "move_left":
            intensity = action.parameters.get("intensity", 1.0)
            self.player.velocity_x = -self.MOVE_SPEED * intensity
        elif action.action_type == "jump" and self.player.on_ground:
            strength = action.parameters.get("strength", 1.0)
            self.player.velocity_y = self.JUMP_FORCE * strength
            self.player.on_ground = False
        elif action.action_type == "attack":
            await self._process_attack()
        elif action.action_type == "wait":
            # Do nothing for wait duration
            await asyncio.sleep(action.duration)
            
    async def update(self) -> Dict[str, Any]:
        """Update game state with intelligent analysis."""
        if self.state != GameState.PLAYING:
            return self._get_game_state()
            
        self.frame_count += 1
        
        # Apply physics
        await self._apply_physics()
        
        # Check collisions
        await self._check_collisions()
        
        # Update enemies
        await self._update_enemies()
        
        # Create current game state for AI analysis
        current_state = self._create_game_state()
        
        # Use intelligent explorer to select next action
        await self.process_intelligent_input(current_state)
        
        # Run real exploit detection
        current_action = Action(
            action_type="update",
            parameters={},
            timestamp=time.time(),
            duration=0.016
        )
        
        new_exploits = self.exploit_detector.analyze_realtime(current_state, current_action)
        
        # Process any new exploits
        for exploit in new_exploits:
            await self._process_exploit(exploit)
        
        return self._get_game_state()
        
    async def _process_exploit(self, exploit: ExploitReport):
        """Process a detected exploit."""
        self.exploits_detected.append(exploit)
        
        # Generate LLM explanation
        explanation = self.llm_client.generate_explanation({
            "exploit_type": exploit.exploit_type.value,
            "description": exploit.description,
            "severity": exploit.severity.value,
            "confidence": exploit.confidence_score
        })
        
        # Save exploit to database
        self.database.save_exploit(
            exploit.exploit_id,
            self.session_id,
            {
                "type": exploit.exploit_type.value,
                "severity": exploit.severity.value,
                "description": exploit.description,
                "explanation": explanation,
                "frame": self.frame_count,
                "confidence": exploit.confidence_score
            }
        )
        
        print(f"🚨 INTELLIGENT EXPLOIT DETECTION:")
        print(f"   Type: {exploit.exploit_type.value}")
        print(f"   Severity: {exploit.severity.value}")
        print(f"   Confidence: {exploit.confidence_score:.3f}")
        print(f"   Description: {exploit.description}")
        print(f"   Explanation: {explanation}")
        print()
        
    def _create_game_state(self) -> CoreGameState:
        """Create GameState object for AI analysis."""
        return CoreGameState(
            timestamp=time.time(),
            player_position=(self.player.x, self.player.y, 0.0),
            player_health=self.player.health,
            player_resources={"coins": self.player.coins, "score": self.player.score},
            game_objects={
                "platforms": self.world.platforms,
                "enemies": self.world.enemies,
                "collectibles": self.world.collectibles
            },
            physics_state={
                "velocity": {"x": self.player.velocity_x, "y": self.player.velocity_y, "z": 0.0},
                "on_ground": self.player.on_ground,
                "gravity": self.GRAVITY
            },
            ui_state={"frame": self.frame_count},
            custom_metrics={
                "movement_distance": abs(self.player.velocity_x) + abs(self.player.velocity_y),
                "resource_rate": self.player.coins / max(self.frame_count, 1),
                "health_rate": self.player.health / 100.0
            }
        )
        
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
        for enemy in self.world.enemies[:]:
            if (self.player.x < enemy["x"] + 20 and
                self.player.x + 20 > enemy["x"] and
                self.player.y < enemy["y"] + 20 and
                self.player.y + 20 > enemy["y"]):
                
                if not self.player.invulnerable:
                    self.player.health -= 10
                    self.player.invulnerable = True
                    self.player.invulnerability_timer = 60
                    
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
            if distance < 50:
                enemy["health"] -= 1
                if enemy["health"] <= 0:
                    self.world.enemies.remove(enemy)
                    self.player.score += 100
                    
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
            "ai_status": self.intelligent_explorer.get_exploration_status(),
            "detection_stats": self.exploit_detector.get_detection_statistics()
        }
        
    def get_exploits(self) -> List[ExploitReport]:
        """Get all detected exploits."""
        return self.exploits_detected.copy()


# Example usage and testing
async def run_intelligent_demo():
    """Run the intelligent demo with real AI algorithms."""
    game = IntelligentDemoGame()
    
    print("🤖 Starting Intelligent Emergent Playtest Designer Demo")
    print("   Using REAL AI algorithms for exploration and exploit detection")
    print()
    
    await game.start_game()
    
    start_time = time.time()
    frame_count = 0
    
    # Run for 60 seconds
    while time.time() - start_time < 60:
        # Update game with intelligent AI
        state = await game.update()
        frame_count += 1
        
        # Print status every 10 seconds
        if frame_count % 600 == 0:  # ~10 seconds at 60fps
            ai_status = state["ai_status"]
            detection_stats = state["detection_stats"]
            
            print(f"📊 Frame {frame_count}:")
            print(f"   Player: ({state['player']['x']:.1f}, {state['player']['y']:.1f})")
            print(f"   Health: {state['player']['health']}, Score: {state['player']['score']}")
            print(f"   AI Phase: {ai_status['phase']}")
            print(f"   Exploits Found: {detection_stats['total_exploits_detected']}")
            print(f"   Memory Size: {ai_status['memory_size']}")
            print()
        
        await asyncio.sleep(0.016)  # ~60 FPS
        
    await game.stop_game()
    
    # Final results
    final_exploits = game.get_exploits()
    detection_stats = game.exploit_detector.get_detection_statistics()
    ai_status = game.intelligent_explorer.get_exploration_status()
    
    print(f"🎮 Intelligent Demo completed!")
    print(f"   Duration: 60 seconds")
    print(f"   Frames processed: {frame_count}")
    print(f"   Final score: {state['player']['score']}")
    print(f"   Exploits found: {len(final_exploits)}")
    print()
    
    print(f"🤖 AI Performance:")
    print(f"   Exploration Phase: {ai_status['phase']}")
    print(f"   Memory Size: {ai_status['memory_size']}")
    print(f"   Recent Novelty: {ai_status['recent_novelty']:.3f}")
    print(f"   Exploit Suspicion: {ai_status['exploit_suspicion']:.3f}")
    print()
    
    print(f"🔍 Detection Statistics:")
    print(f"   Total Exploits: {detection_stats['total_exploits_detected']}")
    print(f"   Average Confidence: {detection_stats['average_confidence']:.3f}")
    print(f"   History Size: {detection_stats['history_size']}")
    print()
    
    if final_exploits:
        print(f"📊 Exploit Summary:")
        for i, exploit in enumerate(final_exploits, 1):
            print(f"   {i}. {exploit.exploit_type.value} ({exploit.severity.value}) - Confidence: {exploit.confidence_score:.3f}")
    
    print()
    print("✅ This demo demonstrates REAL AI algorithms:")
    print("   - Intelligent exploration with novelty search")
    print("   - Real-time exploit detection with statistical analysis")
    print("   - Pattern recognition for loops and stuck states")
    print("   - LLM-powered explanations")
    print("   - Database persistence")

if __name__ == "__main__":
    asyncio.run(run_intelligent_demo())
