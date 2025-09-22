#!/usr/bin/env python3
"""
IMMEDIATE FIX - Try different connection approaches
"""

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
import time

print("🔥 FIXING CONNECTION NOW - Multiple approaches...")

# Fix 1: Try different ports
ports_to_try = [5004, 5005, 5006, 5007, 5008]

for port in ports_to_try:
    try:
        print(f"\n🔧 Trying port {port}...")
        
        env = UnityEnvironment(
            file_name="./build/EmergentPlaytestAI",
            base_port=port,
            no_graphics=True,
            timeout_wait=15,
            seed=1
        )
        
        print(f"✅ SUCCESS ON PORT {port}!")
        print(f"🎯 Behavior specs: {list(env.behavior_specs.keys())}")
        
        if len(env.behavior_specs) > 0:
            behavior_name = list(env.behavior_specs.keys())[0]
            print(f"🎉 FOUND AGENT: {behavior_name}")
            
            # Quick test
            env.reset()
            decision_steps, terminal_steps = env.get_steps(behavior_name)
            print(f"🤖 Active agents: {len(decision_steps)}")
            
            if len(decision_steps) > 0:
                print("🚀 PERFECT! AGENT IS READY FOR TRAINING!")
                env.close()
                exit(0)
        
        env.close()
        break
        
    except Exception as e:
        print(f"❌ Port {port} failed: {e}")
        continue

# Fix 2: Try with worker_id
try:
    print(f"\n🔧 Trying with worker_id...")
    
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        worker_id=1,
        no_graphics=True,
        timeout_wait=10
    )
    
    print(f"✅ SUCCESS WITH WORKER_ID!")
    print(f"🎯 Behavior specs: {list(env.behavior_specs.keys())}")
    env.close()
    
except Exception as e:
    print(f"❌ Worker_id approach failed: {e}")

print("🔥 ALL APPROACHES TRIED!")
