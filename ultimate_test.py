#!/usr/bin/env python3
"""
Ultimate test - bypass the numpy issue by testing connection only
"""

from mlagents_envs.environment import UnityEnvironment

print("🔥 ULTIMATE TEST - Just check connection...")

try:
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        base_port=5004,
        no_graphics=True,
        timeout_wait=5
    )
    
    print(f"✅ CONNECTION SUCCESS!")
    print(f"🎯 Behavior specs: {list(env.behavior_specs.keys())}")
    
    if len(env.behavior_specs) > 0:
        print("🎉 AGENTS FOUND - READY FOR TRAINING!")
    else:
        print("⚠️ Connected but no agents detected")
    
    env.close()
    
except Exception as e:
    print(f"Connection result: {str(e)[:100]}...")

print("🎯 Connection test complete!")
