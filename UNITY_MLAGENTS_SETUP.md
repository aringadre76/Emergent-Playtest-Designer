# Unity ML-Agents Setup Guide

This guide will help you set up Unity ML-Agents integration for the Emergent Playtest Designer.

## Prerequisites

### System Requirements
- **Unity 2022.3 LTS or later**
- **Python 3.9 or later**
- **Git**
- At least 8GB RAM (16GB recommended)
- CUDA-capable GPU (optional but recommended for faster training)

### Environment Choice: WSL2 vs Native Linux

#### WSL2 (Windows Subsystem for Linux)
**Pros:**
- Works on Windows machines
- Good performance for development
- Easy to setup

**Cons:**
- GUI applications (Unity Editor) require additional setup
- Some performance overhead
- GPU acceleration more complex to setup

#### Native Linux
**Pros:**
- Best performance
- Direct GPU access
- Easier Unity Editor integration
- Better for production workloads

**Cons:**
- Requires Linux machine or dual boot

**Recommendation:** Use native Linux laptop if available for production work, WSL2 is fine for development and testing.

---

## Installation Steps

### 1. Python Environment Setup

First, install the updated Python dependencies:

```bash
cd /home/robot/emergent-playtest-designer

# Install/update Python packages
pip install -r requirements.txt

# Verify ML-Agents installation
python -c "import mlagents_envs; print('ML-Agents installed successfully')"
```

### 2. Unity Setup

#### Option A: WSL2 Setup

```bash
# Install Unity Hub (if not already installed)
# You'll need to install Unity Hub on Windows and add Unity 2022.3 LTS

# For headless Unity builds on WSL2:
# 1. Build your Unity project on Windows
# 2. Copy the executable to WSL2 filesystem
# 3. Run headless from WSL2
```

#### Option B: Native Linux Setup

```bash
# Install Unity Hub
wget -qO - https://hub.unity3d.com/linux/keys/public | gpg --dearmor | sudo tee /usr/share/keyrings/Unity_Technologies_ApS.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/Unity_Technologies_ApS.gpg] https://hub.unity3d.com/linux/repos/deb stable main" | sudo tee /etc/apt/sources.list.d/unityhub.list

sudo apt update
sudo apt install unityhub

# Launch Unity Hub
unityhub
```

### 3. Unity ML-Agents Package Installation

1. **Open Unity Editor**
2. **Create new Unity project** (or open existing one)
3. **Install ML-Agents Package:**
   - Window → Package Manager
   - Click "+" → Add package from git URL
   - Enter: `com.unity.ml-agents`
   - Click "Add"

### 4. Add Playtest Designer Scripts

Copy the provided Unity scripts to your Unity project:

```bash
# Create Scripts directory in your Unity project
mkdir -p /path/to/your/unity/project/Assets/Scripts/PlaytestDesigner

# Copy the scripts (adjust paths as needed)
cp Unity/Scripts/*.cs /path/to/your/unity/project/Assets/Scripts/PlaytestDesigner/
```

### 5. Unity Scene Setup

1. **Create a new scene** or open your game scene
2. **Create PlaytestAgent GameObject:**
   - GameObject → Create Empty → Name it "PlaytestAgent"
   - Add `PlaytestAgent` component
   - Add `ExploitDetector` component
   - Add `Rigidbody` component if not present

3. **Create PlaytestManager GameObject:**
   - GameObject → Create Empty → Name it "PlaytestManager"
   - Add `PlaytestManager` component
   - Add `PlaytestSideChannel` component

4. **Configure Agent:**
   - Set movement speed, jump force
   - Configure observation settings
   - Set detection bounds and thresholds
   - Assign spawn points

### 6. Build Configuration

Create a build configuration for headless training:

1. **File → Build Settings**
2. **Add current scene**
3. **Platform:** PC, Mac & Linux Standalone
4. **Target Platform:** Linux 64-bit (or appropriate platform)
5. **Build And Run Settings:**
   - Uncheck "Development Build" for production
   - Check "Headless Mode" for server builds

---

## Configuration

### Python Configuration

Update your configuration file to use ML-Agents:

```python
# emergent_playtest_designer/core/config.py
@dataclass
class UnityConfig:
    executable_path: str = "./build/YourGame"  # Path to Unity build
    project_path: str = ""  # Not needed for built games
    headless_mode: bool = True
    max_episode_steps: int = 10000
    timeout_seconds: int = 60
```

### Unity ML-Agents Configuration

Create a `config/trainer_config.yaml` for training configuration:

```yaml
behaviors:
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
      learning_rate_schedule: linear
      beta_schedule: constant
      epsilon_schedule: linear
    network_settings:
      normalize: false
      hidden_units: 128
      num_layers: 2
      vis_encode_type: simple
      memory:
        sequence_length: 64
        memory_size: 256
    reward_signals:
      extrinsic:
        gamma: 0.99
        strength: 1.0
    max_steps: 1000000
    time_horizon: 64
    summary_freq: 10000
```

---

## Running the System

### Method 1: Using the New ML-Agents Environment

```python
from emergent_playtest_designer.unity_integration import MLAgentsPlaytestEnvironment
from emergent_playtest_designer.core.config import UnityConfig

# Configure
config = UnityConfig(
    executable_path="./build/YourGame",
    headless_mode=True,
    max_episode_steps=10000
)

# Create environment
env = MLAgentsPlaytestEnvironment(config)

# Start environment
if env.start_environment():
    print("Environment started successfully")
    
    # Reset for new episode
    obs = env.reset_episode()
    
    # Run episode
    for step in range(1000):
        # Get action from your AI agent
        action = your_agent.get_action(obs)
        
        # Step environment
        obs, reward, done, info = env.step({"PlaytestAgent": action})
        
        # Check for exploits
        if "exploits" in info:
            print(f"Exploits detected: {info['exploits']}")
        
        if done:
            obs = env.reset_episode()
    
    env.stop_environment()
```

### Method 2: Using Direct ML-Agents Training

```bash
# Train with ML-Agents directly
mlagents-learn config/trainer_config.yaml --env=./build/YourGame --run-id=playtest_run_1

# Resume training
mlagents-learn config/trainer_config.yaml --env=./build/YourGame --run-id=playtest_run_1 --resume
```

---

## Testing Your Setup

### 1. Test Python Integration

```bash
cd /home/robot/emergent-playtest-designer
python3 -c "
from emergent_playtest_designer.unity_integration import MLAgentsPlaytestEnvironment
from emergent_playtest_designer.core.config import UnityConfig
print('Import successful')
"
```

### 2. Test Unity Build

```bash
# Test headless mode (adjust path)
./build/YourGame -batchmode -nographics
```

### 3. Test Full Integration

```python
# test_integration.py
import asyncio
from emergent_playtest_designer.unity_integration import MLAgentsPlaytestEnvironment
from emergent_playtest_designer.core.config import UnityConfig

async def test_integration():
    config = UnityConfig(executable_path="./build/YourGame")
    env = MLAgentsPlaytestEnvironment(config)
    
    if env.start_environment():
        print("✓ Environment started")
        obs = env.reset_episode()
        print("✓ Episode reset")
        env.stop_environment()
        print("✓ Environment stopped")
        return True
    return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    print(f"Integration test: {'PASSED' if success else 'FAILED'}")
```

---

## Troubleshooting

### Common Issues

1. **"No behaviors found in Unity environment"**
   - Ensure PlaytestAgent component is added to a GameObject in the scene
   - Check that the scene is included in build settings

2. **Connection timeout**
   - Increase timeout in UnityConfig
   - Check firewall settings
   - Ensure Unity build is executable

3. **WSL2 Unity Editor issues**
   - Install VcXsrv or similar X server for GUI
   - Set DISPLAY environment variable
   - Consider using Unity headless builds only

4. **Performance issues**
   - Reduce observation complexity
   - Lower max_episode_steps
   - Use GPU acceleration if available

### Debug Commands

```bash
# Check ML-Agents version
python -c "import mlagents_envs; print(mlagents_envs.__version__)"

# Test Unity build
./build/YourGame --help

# Monitor Unity logs
tail -f unity_logs/Player.log
```

---

## Next Steps

Once setup is complete:

1. **Configure your game-specific rewards** in PlaytestManager
2. **Customize exploit detection** in ExploitDetector  
3. **Train your first agent** using the provided configuration
4. **Integrate with the full Emergent Playtest Designer pipeline**

For advanced configuration and production deployment, refer to the main documentation.
