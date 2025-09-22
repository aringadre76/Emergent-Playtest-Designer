#!/usr/bin/env python3
"""
Try to trigger the agent by stepping the environment
"""

from mlagents_envs.environment import UnityEnvironment
import time

print("🔥 TRYING TO TRIGGER AGENT...")

env = UnityEnvironment(
    file_name="./build/EmergentPlaytestAI",
    base_port=6001,  # Use different port
    no_graphics=False,  # Show graphics so we can see what happens
    timeout_wait=10
)

print(f"✅ Connected! Initial behavior specs: {list(env.behavior_specs.keys())}")

# Try multiple resets and steps to see if agent appears
for i in range(3):
    print(f"\n🔄 Attempt {i+1}: Resetting and stepping...")
    
    env.reset()
    time.sleep(1)
    
    print(f"  After reset: {list(env.behavior_specs.keys())}")
    
    # Step environment multiple times
    for step in range(5):
        env.step()
        current_specs = list(env.behavior_specs.keys())
        if len(current_specs) > 0:
            print(f"  🎉 AGENT APPEARED AT STEP {step}! Specs: {current_specs}")
            env.close()
            exit()
    
    print(f"  After 5 steps: {list(env.behavior_specs.keys())}")

print("⚠️ Agent still not appearing - likely a Unity configuration issue")
env.close()
