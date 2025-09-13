# Emergent Playtest Designer

An AI-powered automated testing system for discovering game exploits through unsupervised exploration of Unity games.

## Overview

The Emergent Playtest Designer uses advanced AI techniques including novelty search, evolutionary algorithms, and reinforcement learning to autonomously explore game mechanics and identify unexpected behaviors that human QA teams typically miss.

## Features

- **Automated Exploit Discovery**: Uses AI agents to discover non-obvious exploits and edge cases
- **Reproducible Test Cases**: Generates minimal reproducible input sequences for QA/development teams
- **Human-Readable Explanations**: Provides clear cause-and-effect explanations of discovered exploits using LLM technology
- **Unity Integration**: Seamlessly integrates with Unity games in headless mode
- **Real-time Analysis**: Detects exploits as they occur during gameplay
- **Comprehensive Reporting**: Generates detailed reports with videos, screenshots, and automated test cases

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/Emergent-Playtest-Designer.git
cd Emergent-Playtest-Designer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

## Quick Start

### 1. Configuration

Create a configuration file or set environment variables:

```python
from emergent_playtest_designer.core.config import Config

config = Config.from_env()
config.unity.executable_path = "/path/to/unity/executable"
config.unity.project_path = "/path/to/unity/project"
config.llm.api_key = "your_openai_api_key"
```

### 2. Basic Usage

```python
import asyncio
from emergent_playtest_designer.core.orchestrator import PlaytestOrchestrator, TestingConfig

async def main():
    orchestrator = PlaytestOrchestrator(config)
    
    testing_config = TestingConfig(
        game_path="/path/to/your/game",
        max_duration=3600,  # 1 hour
        max_episodes=1000,
        agent_type="novelty_search"
    )
    
    session_id = await orchestrator.start_testing_session(testing_config)
    print(f"Testing completed: {session_id}")

asyncio.run(main())
```

### 3. Command Line Interface

```bash
# Run a testing session
python -m emergent_playtest_designer.cli run /path/to/game --max-duration 3600

# Start the API server
python -m emergent_playtest_designer.cli server --host 0.0.0.0 --port 8000

# Validate configuration
python -m emergent_playtest_designer.cli validate-config
```

### 4. API Usage

Start the API server:
```bash
python -m emergent_playtest_designer.cli server
```

Then use the REST API:
```bash
# Start a testing session
curl -X POST "http://localhost:8000/api/v1/testing/start" \
  -H "Content-Type: application/json" \
  -d '{
    "game_path": "/path/to/game",
    "max_duration": 3600,
    "agent_type": "novelty_search"
  }'

# Get discovered exploits
curl "http://localhost:8000/api/v1/exploits"

# Get session status
curl "http://localhost:8000/api/v1/testing/status"
```

## Architecture

The system consists of several key components:

### Core Components

- **Orchestrator**: Main system coordinator that manages the testing workflow
- **Unity Integration**: Handles Unity game execution, state observation, and input injection
- **AI Agents**: Novelty search, evolutionary, and reinforcement learning agents for exploration
- **Exploit Detection**: Anomaly detection and pattern analysis for identifying exploits
- **Reproduction System**: Generates reproducible test cases with videos and screenshots
- **Explanation Engine**: LLM-powered system for generating human-readable explanations

### AI Agents

1. **Novelty Search Agent**: Explores game mechanics to discover novel behaviors
2. **Evolutionary Agent**: Uses genetic algorithms to evolve exploit strategies
3. **Reinforcement Learning Agent**: Learns optimal actions through trial and error

### Exploit Types

The system can detect various types of exploits:

- **Out of Bounds**: Player moves outside intended game boundaries
- **Infinite Resources**: Player gains unlimited resources or items
- **Stuck State**: Player becomes unresponsive or stuck
- **Infinite Loop**: Game enters an endless loop state
- **Clipping**: Player passes through solid objects
- **Sequence Break**: Game sequence is broken or skipped

## Examples

### Simple Platformer Example

```python
from examples.simple_platformer import SimplePlatformer

game = SimplePlatformer()
scenarios = game.simulate_exploit_scenarios()

for scenario in scenarios:
    result = game.run_scenario(scenario)
    print(f"Scenario: {scenario['name']}")
    print(f"Exploits found: {len(result['exploits'])}")
```

### Custom Exploit Callback

```python
def exploit_callback(exploit: ExploitReport):
    print(f"Exploit discovered: {exploit.exploit_id}")
    print(f"Type: {exploit.exploit_type.value}")
    print(f"Description: {exploit.description}")
    
    # Generate reproduction data
    reproduction_data = orchestrator.reproduction_generator.generate_reproduction(exploit)
    print(f"Video: {reproduction_data.video_path}")

orchestrator.register_exploit_callback(exploit_callback)
```

## Configuration

### Environment Variables

```bash
# Unity Configuration
UNITY_EXECUTABLE_PATH=/path/to/unity/executable
UNITY_PROJECT_PATH=/path/to/unity/project
HEADLESS_MODE=true

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/playtest_db
REDIS_URL=redis://localhost:6379/0

# Testing Configuration
TEST_GAME_PATH=/path/to/test/game
MAX_TESTING_TIME=3600
MAX_EPISODES=1000
```

### Configuration File

```python
from emergent_playtest_designer.core.config import Config

config = Config(
    unity=Config.UnityConfig(
        executable_path="/path/to/unity",
        project_path="/path/to/project",
        headless_mode=True
    ),
    llm=Config.LLMConfig(
        provider="openai",
        model="gpt-4",
        api_key="your_key"
    ),
    testing=Config.TestingConfig(
        max_testing_time=3600,
        max_episodes=1000
    )
)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=emergent_playtest_designer
```

## Development

### Project Structure

```
emergent_playtest_designer/
├── core/                 # Core system components
├── unity_integration/    # Unity game integration
├── agents/              # AI agents for exploration
├── detection/           # Exploit detection systems
├── reproduction/        # Test case generation
├── explanation/         # LLM-powered explanations
├── api/                # REST API endpoints
├── utils/              # Utility functions
└── cli.py              # Command-line interface

tests/
├── unit/               # Unit tests
└── integration/        # Integration tests

examples/
├── simple_platformer.py # Example game simulation
└── run_example.py      # Usage examples
```

### Adding New Agents

```python
from emergent_playtest_designer.core.types import AgentConfig
from emergent_playtest_designer.agents import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Initialize your agent
    
    def select_action(self, state: GameState) -> Action:
        # Implement action selection logic
        pass
    
    def update(self, state: GameState, action: Action, reward: float, next_state: GameState):
        # Implement learning logic
        pass
```

### Adding New Exploit Types

```python
from emergent_playtest_designer.core.types import ExploitType

# Add new exploit type
class ExploitType(Enum):
    # ... existing types ...
    NEW_EXPLOIT_TYPE = "new_exploit_type"

# Implement detection logic
def detect_new_exploit(self, states: List[GameState]) -> List[Dict[str, Any]]:
    # Your detection logic here
    pass
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions:

- Create an issue on GitHub
- Join our Discord community
- Check the documentation wiki

## Roadmap

- [ ] Unreal Engine support
- [ ] Multi-genre game support
- [ ] Real-time monitoring capabilities
- [ ] CI/CD pipeline integration
- [ ] Advanced exploit pattern recognition
- [ ] Community-driven exploit database