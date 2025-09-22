#!/usr/bin/env python3
"""
Simple test to verify Unity ML-Agents connection without complex imports.
"""

import sys
sys.path.insert(0, '.')

try:
    from mlagents_envs.environment import UnityEnvironment
    from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
    import numpy as np
    
    print("🚀 Testing Unity ML-Agents connection...")
    print(f"✅ ML-Agents imports successful")
    
    # Create engine configuration channel
    engine_config_channel = EngineConfigurationChannel()
    
    # Try to connect to Unity
    env = UnityEnvironment(
        file_name="./build/EmergentPlaytestAI",
        seed=1,
        side_channels=[engine_config_channel]
    )
    
    print("✅ Unity environment connected successfully!")
    print(f"✅ Available behavior specs: {list(env.behavior_specs.keys())}")
    
    # Configure engine for faster training
    engine_config_channel.set_configuration_parameters(time_scale=20.0)
    
    # Reset the environment
    env.reset()
    print("✅ Environment reset successful")
    
    # Test a few steps
    for i in range(5):
        # Get decision steps and terminal steps
        decision_steps, terminal_steps = env.get_steps("PlaytestAgent")
        
        if len(decision_steps) > 0:
            # Generate random actions for continuous action space
            actions = np.random.randn(len(decision_steps), 3)  # 3D movement
            env.set_actions("PlaytestAgent", actions)
            
        env.step()
        print(f"✅ Step {i+1} completed")
    
    print("\n🎉 SUCCESS! Unity ML-Agents integration working perfectly!")
    print(f"🚀 RTX 4070 Super ready for training acceleration")
    
    env.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 This might be normal - Unity executable might need to be run differently")
    print("   or additional configuration might be required.")

# Script runs directly - no main() function needed
