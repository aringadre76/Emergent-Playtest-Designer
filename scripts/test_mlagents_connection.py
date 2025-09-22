#!/usr/bin/env python3
"""
Quick test to verify ML-Agents Unity connection works
"""

from mlagents_envs.environment import UnityEnvironment
import time

print("🚀 TESTING ML-AGENTS CONNECTION...")

try:
    env = UnityEnvironment(
        file_name="build/EmergentPlaytestAI",
        base_port=6010,
        no_graphics=True,
        timeout_wait=5
    )
    
    print("✅ Unity environment connected!")
    
    env.reset()
    behavior_specs = list(env.behavior_specs.keys())
    
    if len(behavior_specs) > 0:
        behavior_name = behavior_specs[0]
        spec = env.behavior_specs[behavior_name]
        
        print(f"✅ Agent detected: {behavior_name}")
        print(f"✅ Continuous actions: {spec.action_spec.continuous_size}")
        
        decision_steps, terminal_steps = env.get_steps(behavior_name)
        print(f"✅ Active agents: {len(decision_steps)}")
        
        print("🎉 ML-AGENTS CONNECTION: PERFECT!")
    else:
        print("⚠️ No agents detected")
    
    env.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Make sure Unity build is available and not running elsewhere")

print("✅ Test complete!")
