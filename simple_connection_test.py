#!/usr/bin/env python3
"""
Super simple ML-Agents connection test with longer wait times.
"""

from mlagents_envs.environment import UnityEnvironment
import time

print("🚀 Simple ML-Agents connection test...")

try:
    print("📱 Connecting to Unity...")
    env = UnityEnvironment(file_name="./build/EmergentPlaytestAI", no_graphics=False)
    
    print("⏳ Waiting for Unity to fully initialize...")
    time.sleep(3)
    
    print("🔄 Resetting environment...")
    env.reset()
    
    print("⏳ Waiting after reset...")
    time.sleep(2)
    
    print(f"🎯 Behavior specs found: {list(env.behavior_specs.keys())}")
    
    if len(env.behavior_specs) > 0:
        behavior_name = list(env.behavior_specs.keys())[0]
        print(f"✅ SUCCESS! Found behavior: {behavior_name}")
        
        spec = env.behavior_specs[behavior_name]
        print(f"👁️ Observations: {len(spec.observation_specs)} specs")
        print(f"🎮 Actions: {spec.action_spec.continuous_size} continuous, {spec.action_spec.discrete_size} discrete")
        
        # Test getting steps
        decision_steps, terminal_steps = env.get_steps(behavior_name)
        print(f"🔢 Active agents: {len(decision_steps)} decision, {len(terminal_steps)} terminal")
        
        if len(decision_steps) > 0:
            print("🎉 AGENT IS READY FOR TRAINING!")
        else:
            print("⚠️ Agent exists but not active - might need to step the environment")
    else:
        print("❌ No behavior specs found")
        print("🔧 Possible issues:")
        print("   1. PlaytestAgent GameObject is inactive")
        print("   2. Behavior Parameters component missing or misconfigured") 
        print("   3. Scene wasn't saved before building")
        print("   4. Wrong scene was built")
    
    env.close()
    print("✅ Test completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
