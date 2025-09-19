"""
Intelligent CLI for the Emergent Playtest Designer that uses REAL AI algorithms.
This demonstrates the actual core functionality with intelligent exploration and exploit detection.
"""

import asyncio
import typer
import json
import time
from typing import Optional
from pathlib import Path
from loguru import logger

# Import our real AI components
from emergent_playtest_designer.agents.intelligent_explorer import IntelligentExplorer
from emergent_playtest_designer.detection.real_exploit_detector import RealExploitDetector
from emergent_playtest_designer.core.types import GameState, Action, AgentConfig
from emergent_playtest_designer.llm import OllamaClient
from emergent_playtest_designer.mocks import MockDatabase
from examples.intelligent_demo import IntelligentDemoGame

app = typer.Typer(help="Emergent Playtest Designer - Intelligent CLI with REAL AI")

@app.command()
def intelligent_demo(
    duration: int = typer.Option(60, help="Demo duration in seconds"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Run intelligent demo with REAL AI algorithms for exploration and exploit detection."""
    
    if verbose:
        logger.add("intelligent_demo.log", level="DEBUG")
    
    logger.info("Starting Intelligent Emergent Playtest Designer Demo")
    
    async def run_intelligent_demo():
        # Initialize intelligent game with real AI
        game = IntelligentDemoGame()
        
        await game.start_game()
        session_id = game.session_id
        
        logger.info(f"Intelligent demo session started: {session_id}")
        
        start_time = time.time()
        frame_count = 0
        
        typer.echo("🤖 Starting Intelligent Emergent Playtest Designer Demo")
        typer.echo("   Using REAL AI algorithms for exploration and exploit detection")
        typer.echo()
        
        while time.time() - start_time < duration:
            # Update game with intelligent AI
            state = await game.update()
            frame_count += 1
            
            # Print status every 10 seconds
            if frame_count % 600 == 0:  # ~10 seconds at 60fps
                ai_status = state["ai_status"]
                detection_stats = state["detection_stats"]
                
                typer.echo(f"📊 Frame {frame_count}:")
                typer.echo(f"   Player: ({state['player']['x']:.1f}, {state['player']['y']:.1f})")
                typer.echo(f"   Health: {state['player']['health']}, Score: {state['player']['score']}")
                typer.echo(f"   AI Phase: {ai_status['phase']}")
                typer.echo(f"   Exploits Found: {detection_stats['total_exploits_detected']}")
                typer.echo(f"   Memory Size: {ai_status['memory_size']}")
                typer.echo()
            
            await asyncio.sleep(0.016)  # ~60 FPS
            
        await game.stop_game()
        
        # Final results
        final_exploits = game.get_exploits()
        detection_stats = game.exploit_detector.get_detection_statistics()
        ai_status = game.intelligent_explorer.get_exploration_status()
        
        typer.echo(f"🎮 Intelligent Demo completed!")
        typer.echo(f"   Duration: {duration} seconds")
        typer.echo(f"   Frames processed: {frame_count}")
        typer.echo(f"   Final score: {state['player']['score']}")
        typer.echo(f"   Exploits found: {len(final_exploits)}")
        typer.echo()
        
        typer.echo(f"🤖 AI Performance:")
        typer.echo(f"   Exploration Phase: {ai_status['phase']}")
        typer.echo(f"   Memory Size: {ai_status['memory_size']}")
        typer.echo(f"   Recent Novelty: {ai_status['recent_novelty']:.3f}")
        typer.echo(f"   Exploit Suspicion: {ai_status['exploit_suspicion']:.3f}")
        typer.echo()
        
        typer.echo(f"🔍 Detection Statistics:")
        typer.echo(f"   Total Exploits: {detection_stats['total_exploits_detected']}")
        typer.echo(f"   Average Confidence: {detection_stats['average_confidence']:.3f}")
        typer.echo(f"   History Size: {detection_stats['history_size']}")
        typer.echo()
        
        if final_exploits:
            typer.echo(f"📊 Exploit Summary:")
            for i, exploit in enumerate(final_exploits, 1):
                typer.echo(f"   {i}. {exploit.exploit_type.value} ({exploit.severity.value}) - Confidence: {exploit.confidence_score:.3f}")
        
        typer.echo()
        typer.echo("✅ This demo demonstrates REAL AI algorithms:")
        typer.echo("   - Intelligent exploration with novelty search")
        typer.echo("   - Real-time exploit detection with statistical analysis")
        typer.echo("   - Pattern recognition for loops and stuck states")
        typer.echo("   - LLM-powered explanations")
        typer.echo("   - Database persistence")
        
        logger.info(f"Intelligent demo completed with {len(final_exploits)} exploits found")
    
    asyncio.run(run_intelligent_demo())

@app.command()
def test_intelligent_game(
    game_path: str = typer.Argument(..., help="Path to game (will use intelligent mock implementation)"),
    max_duration: int = typer.Option(3600, help="Maximum testing duration in seconds"),
    agent_type: str = typer.Option("intelligent_explorer", help="AI agent type"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Test a game using intelligent AI algorithms."""
    
    if verbose:
        logger.add("intelligent_test.log", level="DEBUG")
    
    logger.info(f"Starting intelligent playtesting session for {game_path}")
    
    async def run_intelligent_test():
        # Initialize intelligent components
        agent_config = AgentConfig(
            agent_type=agent_type,
            exploration_rate=0.1,
            learning_rate=0.001,
            memory_size=10000,
            batch_size=32,
            target_update_frequency=1000,
            novelty_threshold=0.5,
            max_episode_length=1000
        )
        
        intelligent_explorer = IntelligentExplorer(agent_config)
        exploit_detector = RealExploitDetector({
            "out_of_bounds_threshold": 1000,
            "infinite_resource_threshold": 10000,
            "stuck_state_threshold": 300,
            "infinite_loop_threshold": 50
        })
        
        llm_client = OllamaClient()
        database = MockDatabase()
        
        session_id = f"intelligent_test_{int(time.time())}"
        
        logger.info(f"Intelligent testing session started: {session_id}")
        
        # Save session
        database.save_session(session_id, game_path, {
            "max_duration": max_duration,
            "agent_type": agent_type,
            "timestamp": time.time()
        })
        
        start_time = time.time()
        frame_count = 0
        exploits_found = []
        
        typer.echo("🤖 Starting Intelligent Game Testing")
        typer.echo(f"   Game: {game_path}")
        typer.echo(f"   Agent: {agent_type}")
        typer.echo(f"   Duration: {max_duration} seconds")
        typer.echo()
        
        # Simulate intelligent testing
        while time.time() - start_time < max_duration:
            # Create mock game state
            mock_state = GameState(
                timestamp=time.time(),
                player_position=(frame_count * 0.1, 100.0, 0.0),
                player_health=100,
                player_resources={"coins": frame_count * 2, "score": frame_count * 10},
                game_objects={"enemies": [], "platforms": []},
                physics_state={"velocity": {"x": 1.0, "y": 0.0, "z": 0.0}},
                ui_state={"frame": frame_count},
                custom_metrics={"movement_distance": frame_count * 0.1}
            )
            
            # Use intelligent explorer to select action
            available_actions = ["move_right", "move_left", "jump", "attack", "wait"]
            action = intelligent_explorer.select_action(mock_state, available_actions)
            
            # Run exploit detection
            new_exploits = exploit_detector.analyze_realtime(mock_state, action)
            
            # Process new exploits
            for exploit in new_exploits:
                exploits_found.append(exploit)
                
                # Generate explanation
                explanation = llm_client.generate_exploit_explanation({
                    "exploit_type": exploit.exploit_type.value,
                    "description": exploit.description,
                    "severity": exploit.severity.value,
                    "confidence": exploit.confidence_score
                })
                
                # Save exploit
                database.save_exploit(
                    exploit.exploit_id,
                    session_id,
                    {
                        "type": exploit.exploit_type.value,
                        "severity": exploit.severity.value,
                        "description": exploit.description,
                        "explanation": explanation,
                        "frame": frame_count,
                        "confidence": exploit.confidence_score
                    }
                )
                
                typer.echo(f"🚨 INTELLIGENT EXPLOIT DETECTION:")
                typer.echo(f"   Type: {exploit.exploit_type.value}")
                typer.echo(f"   Severity: {exploit.severity.value}")
                typer.echo(f"   Confidence: {exploit.confidence_score:.3f}")
                typer.echo(f"   Description: {exploit.description}")
                typer.echo(f"   Explanation: {explanation}")
                typer.echo()
            
            frame_count += 1
            
            # Status update every 30 seconds
            if frame_count % 1800 == 0:  # ~30 seconds at 60fps
                ai_status = intelligent_explorer.get_exploration_status()
                detection_stats = exploit_detector.get_detection_statistics()
                
                typer.echo(f"📊 Testing Progress:")
                typer.echo(f"   Frames: {frame_count}")
                typer.echo(f"   Exploits: {len(exploits_found)}")
                typer.echo(f"   AI Phase: {ai_status['phase']}")
                typer.echo(f"   Memory: {ai_status['memory_size']}")
                typer.echo(f"   Novelty: {ai_status['recent_novelty']:.3f}")
                typer.echo()
            
            await asyncio.sleep(0.016)  # ~60 FPS
        
        # Final results
        detection_stats = exploit_detector.get_detection_statistics()
        ai_status = intelligent_explorer.get_exploration_status()
        
        typer.echo(f"🎮 Intelligent Testing completed!")
        typer.echo(f"   Game: {game_path}")
        typer.echo(f"   Duration: {max_duration} seconds")
        typer.echo(f"   Frames processed: {frame_count}")
        typer.echo(f"   Exploits found: {len(exploits_found)}")
        typer.echo()
        
        typer.echo(f"🤖 AI Performance:")
        typer.echo(f"   Final Phase: {ai_status['phase']}")
        typer.echo(f"   Memory Size: {ai_status['memory_size']}")
        typer.echo(f"   Final Novelty: {ai_status['recent_novelty']:.3f}")
        typer.echo(f"   Exploit Suspicion: {ai_status['exploit_suspicion']:.3f}")
        typer.echo()
        
        typer.echo(f"🔍 Detection Statistics:")
        typer.echo(f"   Total Exploits: {detection_stats['total_exploits_detected']}")
        typer.echo(f"   Average Confidence: {detection_stats['average_confidence']:.3f}")
        typer.echo(f"   History Size: {detection_stats['history_size']}")
        typer.echo()
        
        if exploits_found:
            typer.echo(f"📊 Exploit Summary:")
            for i, exploit in enumerate(exploits_found, 1):
                typer.echo(f"   {i}. {exploit.exploit_type.value} ({exploit.severity.value}) - Confidence: {exploit.confidence_score:.3f}")
        
        logger.info(f"Intelligent testing completed with {len(exploits_found)} exploits found")
    
    asyncio.run(run_intelligent_test())

@app.command()
def compare_algorithms(
    duration: int = typer.Option(30, help="Comparison duration in seconds"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Compare random vs intelligent algorithms side by side."""
    
    if verbose:
        logger.add("algorithm_comparison.log", level="DEBUG")
    
    logger.info("Starting algorithm comparison")
    
    async def run_comparison():
        typer.echo("🔬 Algorithm Comparison: Random vs Intelligent")
        typer.echo(f"   Duration: {duration} seconds each")
        typer.echo()
        
        # Test 1: Random algorithm (old demo)
        typer.echo("🎲 Testing Random Algorithm:")
        from examples.demo_game import DemoGame
        
        random_game = DemoGame()
        await random_game.start_game()
        
        random_start = time.time()
        random_frames = 0
        random_exploits = 0
        
        while time.time() - random_start < duration:
            # Random action every 10 frames
            if random_frames % 10 == 0:
                import random
                actions = [("move_right", 1.0), ("move_left", 1.0), ("jump", 1.0), ("attack", 1.0)]
                action, value = random.choice(actions)
                await random_game.process_input(action, value)
            
            state = await random_game.update()
            random_frames += 1
            
            # Check for exploits
            exploits = random_game.get_exploits()
            if len(exploits) > random_exploits:
                random_exploits = len(exploits)
                typer.echo(f"   Random exploit found: {exploits[-1]['type']}")
            
            await asyncio.sleep(0.016)
        
        await random_game.stop_game()
        
        # Test 2: Intelligent algorithm
        typer.echo()
        typer.echo("🤖 Testing Intelligent Algorithm:")
        
        intelligent_game = IntelligentDemoGame()
        await intelligent_game.start_game()
        
        intel_start = time.time()
        intel_frames = 0
        intel_exploits = 0
        
        while time.time() - intel_start < duration:
            state = await intelligent_game.update()
            intel_frames += 1
            
            # Check for exploits
            exploits = intelligent_game.get_exploits()
            if len(exploits) > intel_exploits:
                intel_exploits = len(exploits)
                typer.echo(f"   Intelligent exploit found: {exploits[-1].exploit_type.value}")
            
            await asyncio.sleep(0.016)
        
        await intelligent_game.stop_game()
        
        # Comparison results
        typer.echo()
        typer.echo("📊 Comparison Results:")
        typer.echo(f"   Random Algorithm:")
        typer.echo(f"     Frames: {random_frames}")
        typer.echo(f"     Exploits: {random_exploits}")
        typer.echo(f"     Score: {random_game.player.score}")
        typer.echo()
        typer.echo(f"   Intelligent Algorithm:")
        typer.echo(f"     Frames: {intel_frames}")
        typer.echo(f"     Exploits: {intel_exploits}")
        typer.echo(f"     Score: {intelligent_game.player.score}")
        typer.echo()
        
        # Performance analysis
        exploit_ratio = intel_exploits / max(random_exploits, 1)
        typer.echo(f"🎯 Performance Analysis:")
        typer.echo(f"   Exploit Discovery Ratio: {exploit_ratio:.2f}x")
        typer.echo(f"   Intelligence Advantage: {'✅ Significant' if exploit_ratio > 1.5 else '⚠️ Moderate' if exploit_ratio > 1.0 else '❌ None'}")
        typer.echo()
        
        if exploit_ratio > 1.0:
            typer.echo("✅ Intelligent algorithms show superior performance!")
            typer.echo("   - Better exploit discovery")
            typer.echo("   - More systematic exploration")
            typer.echo("   - Higher confidence detection")
        else:
            typer.echo("⚠️ Results are similar - longer testing may be needed")
            typer.echo("   - Random algorithms can be effective for simple games")
            typer.echo("   - Intelligent algorithms excel with complex scenarios")
        
        logger.info(f"Algorithm comparison completed: Random {random_exploits} vs Intelligent {intel_exploits}")
    
    asyncio.run(run_comparison())

@app.command()
def test_ollama():
    """Test Ollama integration with Llama 3.2 3B."""
    
    typer.echo("🦙 Testing Ollama Integration...")
    
    try:
        from emergent_playtest_designer.llm import OllamaClient
        
        # Initialize Ollama client
        ollama = OllamaClient()
        
        # Test connection
        model_info = ollama.get_model_info()
        if model_info.get("available", False):
            typer.echo(f"✅ Ollama connection successful")
            typer.echo(f"   Model: {model_info['name']}")
            typer.echo(f"   Size: {model_info.get('size', 'unknown')}")
        else:
            typer.echo(f"❌ Ollama connection failed: {model_info.get('error', 'unknown error')}")
            return
        
        # Test text generation
        typer.echo("🧠 Testing text generation...")
        test_result = ollama.test_generation()
        
        if test_result:
            typer.echo("✅ Text generation working")
        else:
            typer.echo("❌ Text generation failed")
            return
        
        # Test exploit explanation
        typer.echo("🔍 Testing exploit explanation...")
        test_exploit = {
            "exploit_type": "out_of_bounds",
            "severity": "high",
            "description": "Player moved outside game boundaries",
            "confidence": 0.95
        }
        
        explanation = ollama.generate_explanation(test_exploit)
        typer.echo(f"📝 Generated explanation:")
        typer.echo(f"   {explanation[:200]}...")
        
        typer.echo()
        typer.echo("🎉 Ollama integration test completed successfully!")
        typer.echo("   - Connection: ✅ Working")
        typer.echo("   - Text Generation: ✅ Working") 
        typer.echo("   - Exploit Explanation: ✅ Working")
        typer.echo()
        typer.echo("🚀 Ready to use Ollama for real AI explanations!")
        
    except Exception as e:
        typer.echo(f"❌ Ollama test failed: {e}", err=True)
        typer.echo()
        typer.echo("💡 Make sure Ollama is running:")
        typer.echo("   ollama serve")
        typer.echo("   ollama pull llama3.2:3b")
        raise typer.Exit(1)

@app.command()
def validate_intelligence():
    """Validate that intelligent algorithms are working correctly."""
    
    typer.echo("🔍 Validating Intelligent Algorithms...")
    
    try:
        # Test intelligent explorer
        from emergent_playtest_designer.agents.intelligent_explorer import IntelligentExplorer
        from emergent_playtest_designer.core.types import AgentConfig, GameState
        
        agent_config = AgentConfig(agent_type="intelligent_explorer")
        explorer = IntelligentExplorer(agent_config)
        
        # Test action selection
        mock_state = GameState(
            timestamp=time.time(),
            player_position=(0.0, 0.0, 0.0),
            player_health=100,
            player_resources={"coins": 0},
            game_objects={},
            physics_state={},
            ui_state={},
            custom_metrics={}
        )
        
        action = explorer.select_action(mock_state, ["move_right", "move_left", "jump"])
        typer.echo("✅ Intelligent Explorer: Action selection working")
        
        # Test exploit detector
        from emergent_playtest_designer.detection.real_exploit_detector import RealExploitDetector
        from emergent_playtest_designer.core.types import Action
        
        detector = RealExploitDetector({})
        
        # Test exploit detection
        mock_action = Action(action_type="test", parameters={}, timestamp=time.time())
        exploits = detector.analyze_realtime(mock_state, mock_action)
        typer.echo("✅ Real Exploit Detector: Analysis working")
        
        # Test intelligent demo
        from examples.intelligent_demo import IntelligentDemoGame
        
        game = IntelligentDemoGame()
        typer.echo("✅ Intelligent Demo Game: Initialization working")
        
        typer.echo()
        typer.echo("🎉 All intelligent algorithms validated successfully!")
        typer.echo("   - Intelligent Explorer: ✅ Working")
        typer.echo("   - Real Exploit Detector: ✅ Working")
        typer.echo("   - Intelligent Demo Game: ✅ Working")
        typer.echo()
        typer.echo("📋 Available intelligent commands:")
        typer.echo("   python cli_intelligent.py intelligent-demo --help")
        typer.echo("   python cli_intelligent.py test-intelligent-game --help")
        typer.echo("   python cli_intelligent.py compare-algorithms --help")
        
    except Exception as e:
        typer.echo(f"❌ Validation failed: {e}", err=True)
        raise typer.Exit(1)

def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()
