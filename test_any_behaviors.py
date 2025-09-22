#!/usr/bin/env python3
"""
Test to see if we can find ANY behavior specs or get more debugging info.
"""

import sys
sys.path.insert(0, '.')

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
import time

print("🔍 Looking for ANY ML-Agents behaviors...")

try:
    engine_config_channel = EngineConfigurationChannel()
    
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        seed=1,
        side_channels=[engine_config_channel],
        no_graphics=True,
        timeout_wait=30
    )
    
    print(f"✅ Unity connected")
    print(f"🔍 All behavior specs: {list(env.behavior_specs.keys())}")
    
    # Try to reset and see what happens
    print("🔄 Resetting environment...")
    env.reset()
    
    # Try common behavior names
    test_names = ["PlaytestAgent", "Agent", "PlaytestAgent?team=0"]
    
    for name in test_names:
        try:
            decision_steps, terminal_steps = env.get_steps(name)
            if len(decision_steps) > 0 or len(terminal_steps) > 0:
                print(f"✅ Found behavior '{name}': {len(decision_steps)} decision steps, {len(terminal_steps)} terminal steps")
            else:
                print(f"❌ No steps found for behavior '{name}'")
        except Exception as e:
            print(f"❌ Error testing behavior '{name}': {e}")
    
    # Let's also try stepping the environment a few times to see if anything shows up
    print("🔄 Stepping environment to see if agents appear...")
    for i in range(5):
        env.step()
        print(f"  Step {i+1}: behavior specs = {list(env.behavior_specs.keys())}")
        time.sleep(0.1)
    
    env.close()
    
except Exception as e:
    print(f"❌ Connection error: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 TROUBLESHOOTING SUGGESTIONS:")
print("1. In Unity Editor, check if PlaytestAgent GameObject is ACTIVE (checkbox checked)")
print("2. Make sure PlaytestAgent is in the SAME scene that was built")
print("3. Verify Behavior Parameters component has 'PlaytestAgent' as Behavior Name")
print("4. Try opening the built Unity game manually - does it show the agent?")
