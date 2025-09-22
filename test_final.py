#!/usr/bin/env python3
"""
Final test after adding Decision Requester
"""

from mlagents_envs.environment import UnityEnvironment
import numpy as np

print("🚀 FINAL TEST - Should work now!")

try:
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        base_port=5004,
        no_graphics=True,
        timeout_wait=10
    )
    
    behavior_specs = list(env.behavior_specs.keys())
    print(f"🎯 Behavior specs: {behavior_specs}")
    
    if len(behavior_specs) > 0:
        behavior_name = behavior_specs[0]
        print(f"🎉 SUCCESS! Found agent: {behavior_name}")
        
        spec = env.behavior_specs[behavior_name]
        print(f"👁️ Observations: {len(spec.observation_specs)}")
        print(f"🎮 Continuous actions: {spec.action_spec.continuous_size}")
        
        env.reset()
        decision_steps, terminal_steps = env.get_steps(behavior_name)
        print(f"🤖 Active agents: {len(decision_steps)}")
        
        if len(decision_steps) > 0:
            print("🚀 PERFECT! READY FOR AI TRAINING!")
            
            # Test one action
            actions = np.random.randn(len(decision_steps), spec.action_spec.continuous_size)
            env.set_actions(behavior_name, actions)
            env.step()
            print("✅ Action test successful!")
    else:
        print("❌ Still no behavior specs - need Decision Requester component")
    
    env.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

print("🎯 Add Decision Requester component if behavior specs still empty!")
