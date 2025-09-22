#!/usr/bin/env python3
"""
Deep debug - let's see what Unity is actually doing
"""

from mlagents_envs.environment import UnityEnvironment
import time

print("🔍 DEEP DEBUG - Let's see what Unity is doing...")

try:
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        base_port=5004,
        no_graphics=False,  # Show graphics so we can see what's happening
        timeout_wait=15
    )
    
    print(f"✅ Connected to Unity")
    print(f"🔍 Behavior specs: {list(env.behavior_specs.keys())}")
    
    # Let's try stepping through multiple resets and steps to see if agent appears
    for i in range(5):
        print(f"\n🔄 Reset attempt {i+1}...")
        env.reset()
        
        # Wait a moment
        time.sleep(1)
        
        # Check all possible behavior names
        test_names = ["PlaytestAgent", "Agent", "PlaytestAgent?team=0"]
        
        for name in test_names:
            try:
                decision_steps, terminal_steps = env.get_steps(name)
                print(f"  Testing '{name}': {len(decision_steps)} decision, {len(terminal_steps)} terminal")
                if len(decision_steps) > 0 or len(terminal_steps) > 0:
                    print(f"  🎉 FOUND SOMETHING with name '{name}'!")
            except Exception as e:
                print(f"  Error testing '{name}': {e}")
        
        # Step the environment
        print(f"  Stepping environment...")
        env.step()
        
        # Check behavior specs again after step
        current_specs = list(env.behavior_specs.keys())
        if len(current_specs) > 0:
            print(f"  🎉 Behavior specs appeared: {current_specs}")
            break
        
        time.sleep(0.5)
    
    env.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 If still no behavior specs:")
print("1. Check if PlaytestAgent GameObject is actually ACTIVE in Unity scene")
print("2. Make sure PlaytestAgent script has no compilation errors")
print("3. Verify Behavior Parameters Behavior Name exactly matches script class name")
print("4. Try building in Development mode for better debugging")
