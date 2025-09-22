#!/usr/bin/env python3
"""
Quick test - minimal wait times to avoid hanging.
"""

from mlagents_envs.environment import UnityEnvironment

print("🔥 QUICK TEST - Minimal waiting...")

try:
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        no_graphics=True,  # Run without graphics for faster connection
        timeout_wait=10    # 10 second timeout
    )
    
    print(f"✅ Connected! Behavior specs: {list(env.behavior_specs.keys())}")
    
    if len(env.behavior_specs) > 0:
        print("🎉 SUCCESS! ML-Agents is working!")
    else:
        print("⚠️ Connected but no agents found")
    
    env.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

print("✅ Quick test complete!")
