#!/usr/bin/env python3
"""
Example usage of ML-Agents integration with Emergent Playtest Designer.
"""

import numpy as np
from emergent_playtest_designer.unity_integration import MLAgentsPlaytestEnvironment
from emergent_playtest_designer.core.config import UnityConfig

def main():
    # Configure Unity environment
    config = UnityConfig(
        executable_path="./build/EmergentPlaytestAI",  # Path to your built Unity executable
        project_path="",  # Not needed for built games
        headless_mode=True,
        max_episode_steps=5000
    )
    
    # Create environment
    env = MLAgentsPlaytestEnvironment(config)
    
    try:
        # Start Unity environment
        if not env.start_environment():
            print("Failed to start Unity environment")
            return
            
        print("Unity environment started successfully")
        
        # Run a few episodes
        for episode in range(3):
            print(f"\n=== Episode {episode + 1} ===")
            
            # Reset environment
            obs = env.reset_episode()
            print(f"Episode reset, observation shape: {obs['observation'].shape}")
            
            # Run episode
            total_reward = 0
            for step in range(100):
                # Random actions for demonstration
                action_space = env.get_action_space()
                continuous_actions = np.random.randn(1, action_space.get('continuous_actions', 3))
                
                # Step environment
                obs, reward, done, info = env.step({"PlaytestAgent": continuous_actions})
                total_reward += reward
                
                # Check for exploits
                if "exploits" in info:
                    print(f"Step {step}: Exploits detected!")
                    for exploit in info["exploits"]:
                        print(f"  - {exploit['type']}: {exploit['description']}")
                
                if done:
                    print(f"Episode terminated at step {step}")
                    break
            
            print(f"Episode {episode + 1} total reward: {total_reward:.2f}")
            
            # Get episode statistics
            stats = env.get_episode_stats()
            print(f"Episode stats: {stats}")
    
    finally:
        # Clean up
        env.stop_environment()
        print("Environment closed")

if __name__ == "__main__":
    main()
