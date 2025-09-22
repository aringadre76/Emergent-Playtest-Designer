#!/usr/bin/env python3
"""
Test with a fresh port that's definitely not in use
"""

from mlagents_envs.environment import UnityEnvironment

print("🔥 TESTING WITH FRESH PORT 6000...")

try:
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        base_port=6000,  # Using fresh port 6000
        no_graphics=True,
        timeout_wait=8
    )
    
    print(f"✅ CONNECTION SUCCESS ON PORT 6000!")
    print(f"🎯 Behavior specs: {list(env.behavior_specs.keys())}")
    
    if len(env.behavior_specs) > 0:
        behavior_name = list(env.behavior_specs.keys())[0]
        print(f"🎉 SUCCESS! Found agent: {behavior_name}")
        
        spec = env.behavior_specs[behavior_name]
        print(f"👁️ Observations: {len(spec.observation_specs)}")
        print(f"🎮 Actions: {spec.action_spec.continuous_size} continuous, {spec.action_spec.discrete_size} discrete")
        print("🚀 READY FOR AI TRAINING!")
    else:
        print("⚠️ Connected but no behavior specs found")
    
    env.close()
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("🎯 Fresh port test complete!")
