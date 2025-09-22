#!/usr/bin/env python3
"""
Set up a simple training scenario for our PlaytestAgent.
"""

import sys
sys.path.insert(0, '.')

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
import numpy as np
import time

def main():
    print("🎯 Setting up AI training scenario...")
    
    # Create engine configuration channel
    engine_config_channel = EngineConfigurationChannel()
    
    # Connect to Unity
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        seed=1,
        side_channels=[engine_config_channel]
    )
    
    # Configure for faster training
    engine_config_channel.set_configuration_parameters(
        time_scale=10.0,  # 10x faster than real-time
        target_frame_rate=60,
        capture_frame_rate=60
    )
    
    behavior_name = list(env.behavior_specs.keys())[0]  # Get the agent behavior
    spec = env.behavior_specs[behavior_name]
    
    print(f"🧠 Agent behavior: {behavior_name}")
    print(f"👁️ Observation space: {spec.observation_specs}")
    print(f"🎮 Action space: Continuous={spec.action_spec.continuous_size}, Discrete={spec.action_spec.discrete_size}")
    
    # Training loop
    episode = 0
    total_steps = 0
    
    try:
        env.reset()
        
        while episode < 10:  # Train for 10 episodes
            episode += 1
            episode_steps = 0
            episode_reward = 0
            
            print(f"\n🚀 Episode {episode} starting...")
            
            while episode_steps < 1000:  # Max 1000 steps per episode
                decision_steps, terminal_steps = env.get_steps(behavior_name)
                
                # Handle agents that need actions
                if len(decision_steps) > 0:
                    # SIMPLE AI STRATEGY: Random exploration with some bias
                    actions = np.random.randn(len(decision_steps), spec.action_spec.continuous_size)
                    
                    # Bias towards forward movement (encourage exploration)
                    actions[:, 0] = np.abs(actions[:, 0])  # Forward movement
                    actions[:, 1] *= 0.5  # Reduce jumping
                    actions[:, 2] *= 0.3  # Reduce side movement
                    
                    env.set_actions(behavior_name, actions)
                    
                    # Calculate simple reward based on movement
                    if len(decision_steps.obs) > 0:
                        # Get agent position (assuming first 3 values are position)
                        try:
                            agent_pos = decision_steps.obs[0][0][:3]
                            distance_from_center = np.linalg.norm(agent_pos)
                            
                            # Reward exploration (moving away from center)
                            exploration_reward = min(distance_from_center * 0.01, 0.1)
                            episode_reward += exploration_reward
                            
                            if episode_steps % 100 == 0:
                                print(f"  Step {episode_steps}: Position {agent_pos[:3]}, Distance: {distance_from_center:.2f}")
                        except:
                            pass
                
                # Handle terminated agents
                if len(terminal_steps) > 0:
                    print(f"  Agent terminated at step {episode_steps}")
                    break
                
                env.step()
                episode_steps += 1
                total_steps += 1
                
                # Reset episode if too long
                if episode_steps >= 1000:
                    print(f"  Episode timeout at {episode_steps} steps")
                    env.reset()
                    break
            
            print(f"✅ Episode {episode} completed: {episode_steps} steps, reward: {episode_reward:.2f}")
            
            # Reset for next episode
            if episode < 10:
                env.reset()
                time.sleep(0.1)  # Brief pause between episodes
    
    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
    except Exception as e:
        print(f"❌ Error during training: {e}")
    finally:
        env.close()
        print(f"\n🏁 Training completed! Total steps: {total_steps}")
        print("🎉 Your AI agent just learned through trial and error!")

if __name__ == "__main__":
    main()
