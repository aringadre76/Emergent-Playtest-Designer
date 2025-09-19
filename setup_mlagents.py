#!/usr/bin/env python3
"""
Setup script for Unity ML-Agents integration with Emergent Playtest Designer.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: Command failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    return True

def check_python_version():
    """Check if Python version is 3.9+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"ERROR: Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install Python requirements."""
    print("\n=== Installing Python Requirements ===")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        return False
    
    print("✓ Requirements installed")
    return True

def verify_mlagents_install():
    """Verify ML-Agents installation."""
    print("\n=== Verifying ML-Agents Installation ===")
    
    try:
        import mlagents_envs
        print(f"✓ mlagents-envs version: {mlagents_envs.__version__}")
    except ImportError as e:
        print(f"ERROR: Could not import mlagents_envs: {e}")
        return False
    
    try:
        import mlagents
        print(f"✓ mlagents installed")
    except ImportError:
        print("Warning: mlagents package not found (trainer not installed)")
    
    return True

def test_integration():
    """Test the ML-Agents environment wrapper."""
    print("\n=== Testing Integration ===")
    
    try:
        from emergent_playtest_designer.unity_integration import MLAgentsPlaytestEnvironment
        from emergent_playtest_designer.core.config import UnityConfig
        
        config = UnityConfig(
            executable_path="./test_build/game",
            project_path="",  # Not needed for built games
            headless_mode=True
        )
        
        env = MLAgentsPlaytestEnvironment(config)
        print("✓ ML-Agents environment wrapper created successfully")
        
        # Test observation/action space methods (without starting Unity)
        obs_space = env.get_observation_space()
        action_space = env.get_action_space()
        print("✓ Environment interface methods work")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Integration test failed: {e}")
        return False

def create_example_config():
    """Create example configuration files."""
    print("\n=== Creating Example Configuration ===")
    
    # Create Unity trainer config
    trainer_config = """behaviors:
  PlaytestAgent:
    trainer_type: ppo
    hyperparameters:
      batch_size: 1024
      buffer_size: 10240
      learning_rate: 3.0e-4
      beta: 5.0e-4
      epsilon: 0.2
      lambd: 0.99
      num_epoch: 3
    network_settings:
      normalize: false
      hidden_units: 128
      num_layers: 2
    reward_signals:
      extrinsic:
        gamma: 0.99
        strength: 1.0
    max_steps: 500000
    time_horizon: 64
    summary_freq: 10000
"""
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "trainer_config.yaml", "w") as f:
        f.write(trainer_config)
    
    print("✓ Created config/trainer_config.yaml")
    
    # Create Python example
    python_example = '''#!/usr/bin/env python3
"""
Example usage of ML-Agents integration with Emergent Playtest Designer.
"""

import numpy as np
from emergent_playtest_designer.unity_integration import MLAgentsPlaytestEnvironment
from emergent_playtest_designer.core.config import UnityConfig

def main():
    # Configure Unity environment
    config = UnityConfig(
        executable_path="./build/YourGame",  # Update this path
        project_path="",  # Not needed for built games
        headless_mode=True,
        max_episode_steps=5000
    )
    
    # Create environment
    env = MLAgentsPlaytestEnvironment(config)
    
    try:
        # Start Unity environment
        if not env.start_environment():
            print("Failed to start Unity environment")
            return
            
        print("Unity environment started successfully")
        
        # Run a few episodes
        for episode in range(3):
            print(f"\\n=== Episode {episode + 1} ===")
            
            # Reset environment
            obs = env.reset_episode()
            print(f"Episode reset, observation shape: {obs['observation'].shape}")
            
            # Run episode
            total_reward = 0
            for step in range(100):
                # Random actions for demonstration
                action_space = env.get_action_space()
                continuous_actions = np.random.randn(1, action_space.get('continuous_actions', 3))
                
                # Step environment
                obs, reward, done, info = env.step({"PlaytestAgent": continuous_actions})
                total_reward += reward
                
                # Check for exploits
                if "exploits" in info:
                    print(f"Step {step}: Exploits detected!")
                    for exploit in info["exploits"]:
                        print(f"  - {exploit['type']}: {exploit['description']}")
                
                if done:
                    print(f"Episode terminated at step {step}")
                    break
            
            print(f"Episode {episode + 1} total reward: {total_reward:.2f}")
            
            # Get episode statistics
            stats = env.get_episode_stats()
            print(f"Episode stats: {stats}")
    
    finally:
        # Clean up
        env.stop_environment()
        print("Environment closed")

if __name__ == "__main__":
    main()
'''
    
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    with open(examples_dir / "mlagents_example.py", "w") as f:
        f.write(python_example)
    
    print("✓ Created examples/mlagents_example.py")
    return True

def main():
    """Main setup function."""
    print("=== Unity ML-Agents Integration Setup ===")
    print("This script will set up ML-Agents integration for Emergent Playtest Designer\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Verify installation
    if not verify_mlagents_install():
        sys.exit(1)
    
    # Test integration
    if not test_integration():
        sys.exit(1)
    
    # Create example files
    if not create_example_config():
        sys.exit(1)
    
    print("\n=== Setup Complete! ===")
    print("✓ ML-Agents packages installed")
    print("✓ Integration verified")
    print("✓ Example configuration created")
    
    print(f"\nNext steps:")
    print(f"1. Follow the Unity setup guide: UNITY_MLAGENTS_SETUP.md")
    print(f"2. Build your Unity project with ML-Agents")
    print(f"3. Update the executable path in examples/mlagents_example.py")
    print(f"4. Run: python examples/mlagents_example.py")
    
    print(f"\nFor training with ML-Agents directly:")
    print(f"mlagents-learn config/trainer_config.yaml --env=./build/YourGame --run-id=test_run")

if __name__ == "__main__":
    main()
