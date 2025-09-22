# 🚀 Emergent Playtest Designer

**AI-Powered Automated Game Testing with Unity ML-Agents & GPU Acceleration**

A cutting-edge system that uses machine learning to automatically discover exploits, analyze gameplay patterns, and generate comprehensive playtest reports for Unity games.

## ✨ **Features**

- 🤖 **AI-Powered Playtesting**: Intelligent agents learn to play and break your game
- 🔥 **GPU Acceleration**: RTX 4070 Super support for 10-50x faster training
- 🎮 **Unity Integration**: Seamless ML-Agents integration with Unity 6.x
- 🔍 **Exploit Detection**: Automatically discover bugs and edge cases
- 📊 **Performance Analytics**: Real-time performance tracking and optimization
- 🧠 **Intelligent Exploration**: Novelty search and reinforcement learning
- 📝 **Automated Reports**: Generate comprehensive playtest documentation

## 🏆 **System Status**

✅ **Unity 6.2** + **ML-Agents 2.0.1** integration  
✅ **RTX 4070 Super** (12.9GB VRAM) GPU acceleration ready  
✅ **PlaytestAgent** with 3 continuous + 1 discrete actions  
✅ **Python ↔ Unity** bidirectional communication  
✅ **Complete testing framework** with diagnostics  

## 🛠️ **Quick Start**

### Prerequisites
- **Python 3.8+** with pip
- **Unity 6.x** with ML-Agents package
- **NVIDIA GPU** with CUDA support (optional but recommended)

### 1. Setup Python Environment
```bash
# Clone the repository
git clone https://github.com/your-username/emergent-playtest-designer.git
cd emergent-playtest-designer

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Verify GPU setup (optional)
python scripts/test_gpu_windows.py
```

### 2. Unity Project Setup
```bash
# Open Unity project
cd UnityProject/EmergentPlaytestAI

# In Unity:
# 1. Install ML-Agents package: Window > Package Manager > Add from git URL: com.unity.ml-agents@2.0.1
# 2. Build the project: File > Build Settings > Build (save as 'build/EmergentPlaytestAI')
```

### 3. Run AI Training
```bash
# Test system
python scripts/test_system.py

# Test ML-Agents connection
python scripts/test_mlagents_connection.py

# Run AI training example
python examples/mlagents_example.py
```

## 📁 **Project Structure**

```
emergent-playtest-designer/
├── 🏗️ build/                      # Unity executable (generated)
├── ⚙️ config/                      # ML-Agents training configurations
├── 📦 emergent_playtest_designer/   # Main Python package
│   ├── 🤖 agents/                  # AI agent implementations
│   ├── 🔍 detection/               # Exploit detection algorithms
│   ├── 📊 explanation/             # Analysis and reporting
│   └── 🎮 unity_integration/       # Unity communication
├── 📚 examples/                    # Usage examples and demos
├── 🔧 scripts/                     # Utility scripts
│   ├── test_gpu_windows.py        # GPU verification
│   ├── test_system.py             # System health check
│   └── test_mlagents_connection.py # ML-Agents connectivity
├── 🧪 tests/                      # Unit tests
├── 🎮 Unity/                      # Unity C# template scripts
│   └── Scripts/                   # PlaytestAgent, Manager, etc.
└── 🏗️ UnityProject/                # Complete Unity project
    └── EmergentPlaytestAI/        # Working Unity project with ML-Agents
```

## 🎯 **Core Components**

### **🤖 AI Agents**
- **PlaytestAgent**: Main Unity ML-Agents agent with 3D movement
- **Novelty Search**: Explores unusual game states and behaviors
- **Reinforcement Learning**: Learns optimal and suboptimal strategies
- **Evolutionary Algorithms**: Discovers creative exploit sequences

### **🔍 Detection Systems**
- **Real-time Exploit Detection**: Identifies bugs during gameplay
- **Anomaly Detection**: Flags unusual performance or behavior
- **Pattern Analysis**: Recognizes recurring issues and edge cases

### **📊 Analysis & Reporting**
- **Performance Tracking**: FPS, memory usage, GPU utilization
- **Causal Analysis**: Identifies root causes of issues
- **LLM Integration**: Natural language explanations of findings

## 🚀 **GPU Performance**

| Component | Performance Boost |
|-----------|-------------------|
| **Training Speed** | 10-50x faster with CUDA |
| **Batch Processing** | 100+ parallel environments |
| **Memory Capacity** | 12.9GB VRAM for large models |
| **Real-time Analysis** | Sub-millisecond inference |

## 📖 **Documentation**

- **[Quick Start Guide](QUICK_START.md)**: Get up and running in 5 minutes
- **[Unity Setup](UNITY_MLAGENTS_SETUP.md)**: Detailed Unity configuration
- **[Product Requirements](PRD.md)**: Complete system specifications
- **[Missing Features](MISSING_FUNCTIONALITY.md)**: Planned enhancements

## 🔧 **Development**

### Running Tests
```bash
# System verification
python scripts/test_system.py

# ML-Agents connectivity
python scripts/test_mlagents_connection.py

# Full test suite
python -m pytest tests/
```

### Adding New Agents
1. Create agent class in `emergent_playtest_designer/agents/`
2. Implement required interface methods
3. Add configuration to `config/trainer_config.yaml`
4. Test with Unity environment

## 📈 **Roadmap**

- 🎯 **Multi-game Support**: Template system for different game types
- 🌐 **Cloud Training**: Distributed GPU training across multiple machines  
- 📱 **Web Dashboard**: Real-time monitoring and control interface
- 🔌 **Plugin System**: Easy integration with existing game engines
- 📊 **Advanced Analytics**: Deeper insights and predictive modeling

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 **Acknowledgments**

- Unity ML-Agents team for the incredible framework
- NVIDIA for CUDA and GPU acceleration support
- The open-source community for inspiration and tools

---

**🎮 Ready to revolutionize game testing with AI? Let's build the future of automated playtesting together!**