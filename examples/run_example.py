"""
Example script showing how to use the Emergent Playtest Designer.
"""

import asyncio
import time
from emergent_playtest_designer.core.config import Config
from emergent_playtest_designer.core.orchestrator import PlaytestOrchestrator, TestingConfig
from emergent_playtest_designer.core.types import ExploitReport


def exploit_callback(exploit: ExploitReport):
    """Callback function called when an exploit is discovered."""
    print(f"\n🚨 EXPLOIT DISCOVERED! 🚨")
    print(f"ID: {exploit.exploit_id}")
    print(f"Type: {exploit.exploit_type.value}")
    print(f"Severity: {exploit.severity.value}")
    print(f"Description: {exploit.description}")
    print(f"Confidence: {exploit.confidence_score:.1%}")
    print(f"Reproduction steps:")
    for i, step in enumerate(exploit.reproduction_steps, 1):
        print(f"  {i}. {step}")
    print("-" * 50)


async def main():
    """Main example function."""
    print("🎮 Emergent Playtest Designer Example")
    print("=" * 50)
    
    # Create configuration
    config = Config()
    
    # Override some settings for the example
    config.unity.executable_path = "/path/to/unity/executable"
    config.unity.project_path = "/path/to/unity/project"
    config.llm.api_key = "your_api_key_here"
    config.testing.test_game_path = "/path/to/test/game"
    config.testing.max_testing_time = 300  # 5 minutes
    config.testing.max_episodes = 50
    
    # Create orchestrator
    orchestrator = PlaytestOrchestrator(config)
    
    # Register exploit callback
    orchestrator.register_exploit_callback(exploit_callback)
    
    # Create testing configuration
    testing_config = TestingConfig(
        game_path="/path/to/your/game",
        max_duration=300,  # 5 minutes
        max_episodes=50,
        agent_type="novelty_search",
        exploit_detection_enabled=True,
        reproduction_enabled=True,
        explanation_enabled=True
    )
    
    print(f"Starting testing session...")
    print(f"Game: {testing_config.game_path}")
    print(f"Agent: {testing_config.agent_type}")
    print(f"Max duration: {testing_config.max_duration}s")
    print(f"Max episodes: {testing_config.max_episodes}")
    print()
    
    try:
        # Start testing session
        session_id = await orchestrator.start_testing_session(testing_config)
        
        print(f"✅ Testing session completed: {session_id}")
        
        # Get session results
        status = orchestrator.get_session_status()
        print(f"\n📊 Session Results:")
        print(f"  Duration: {status['end_time'] - status['start_time']:.1f}s")
        print(f"  Exploits found: {status['exploits_found']}")
        print(f"  Total actions: {status['total_actions']}")
        print(f"  Total states: {status['total_states']}")
        
        # Get system statistics
        stats = orchestrator.get_statistics()
        print(f"\n🔧 System Statistics:")
        print(f"  Agent type: {stats['agent_type']}")
        print(f"  Unity running: {stats['unity_running']}")
        print(f"  Monitoring active: {stats['monitoring_active']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        raise


def run_simple_example():
    """Run a simple example without Unity integration."""
    print("🎮 Simple Platformer Example")
    print("=" * 50)
    
    from examples.simple_platformer import SimplePlatformer
    
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
    print("Choose an example to run:")
    print("1. Full system example (requires Unity)")
    print("2. Simple platformer example")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        run_simple_example()
    else:
        print("Invalid choice. Running simple example...")
        run_simple_example()
