#!/usr/bin/env python3
"""
Debug script to understand why agents aren't showing up.
"""

import sys
sys.path.insert(0, '.')

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
import time

print("🔍 Debugging ML-Agents setup...")

try:
    # Create engine configuration channel
    engine_config_channel = EngineConfigurationChannel()
    
    # Connect to Unity with more verbose output
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        seed=1,
        side_channels=[engine_config_channel],
        no_graphics=False,  # Show graphics to see what's happening
        timeout_wait=60
    )
    
    print(f"✅ Unity environment connected")
    print(f"🔍 Behavior specs: {env.behavior_specs}")
    print(f"🔍 Number of behavior specs: {len(env.behavior_specs)}")
    
    if len(env.behavior_specs) == 0:
        print("\n❌ No behavior specs found!")
        print("🔧 This usually means:")
        print("   1. PlaytestAgent GameObject doesn't have Behavior Parameters component")
        print("   2. Behavior Parameters component isn't configured correctly")
        print("   3. PlaytestAgent script has compilation errors")
        print("   4. Scene wasn't saved before building")
        
        print("\n🔍 Trying to get more info...")
        env.reset()
        
        # Wait a moment and check again
        time.sleep(2)
        decision_steps, terminal_steps = env.get_steps("PlaytestAgent")
        print(f"🔍 Decision steps for 'PlaytestAgent': {len(decision_steps)}")
        
    else:
        behavior_name = list(env.behavior_specs.keys())[0]
        spec = env.behavior_specs[behavior_name]
        
        print(f"\n🎉 Found agent behavior: {behavior_name}")
        print(f"👁️ Observation specs: {spec.observation_specs}")
        print(f"🎮 Action spec: {spec.action_spec}")
        print(f"   - Continuous actions: {spec.action_spec.continuous_size}")
        print(f"   - Discrete actions: {spec.action_spec.discrete_size}")
        
        # Test reset and step
        env.reset()
        decision_steps, terminal_steps = env.get_steps(behavior_name)
        print(f"🔍 Active agents after reset: {len(decision_steps)}")
        
        if len(decision_steps) > 0:
            print("✅ Agent is active and ready for training!")
            
            # Show first observation
            if len(decision_steps.obs) > 0:
                obs = decision_steps.obs[0]
                print(f"🧠 First observation shape: {obs.shape}")
                print(f"🧠 First few observation values: {obs[0][:10] if len(obs[0]) >= 10 else obs[0]}")
    
    env.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Debug complete!")

