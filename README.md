# PlaytestAI - Automated Game Testing

PlaytestAI automates game testing using intelligent agents that can play, observe, and analyze games in real time - identifying bugs, glitches, performance issues, and gameplay inconsistencies.

## Features

- Automated game window capture and input injection
- Multiple agent playstyles (Random agent in MVP)
- Visual anomaly detection using SSIM
- Softlock detection
- Crash detection and logging
- Reproducible replay system
- Session recording with screenshots
- Video export from replays

## Architecture

```
Controller / CLI
       |
   Agent Core
       |
  +----+----+
  |    |    |
Input Frame Analyzer
      Grabber
       |
    Logger
       |
   Replay Engine
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (Linux support coming soon)
- A game to test

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd emergent-playtest-designer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Optional: Install pywin32 for better window detection on Windows:
```bash
pip install pywin32
```

## Usage

### Running a Playtest Session

Basic usage with default settings:
```bash
python3 playtest.py --window "GameTitle"
```

Full options:
```bash
python3 playtest.py --window "GameTitle" --agent random --steps 1000 --fps 10 --keys w a s d space
```

Options:
- `--window`: Game window title (required)
- `--agent`: Agent type (default: random)
- `--steps`: Maximum steps to run (default: 1000)
- `--fps`: Frame capture rate (default: 10)
- `--session-name`: Custom session name (optional)
- `--keys`: Custom key list for random agent (optional)

Example:
```bash
python3 playtest.py --window "Celeste" --steps 5000 --fps 15 --keys left right space z x
```

### Replaying a Session

Replay a recorded session:
```bash
python3 replay.py --repro repro/session_2025-10-06T142030
```

Full options:
```bash
python3 replay.py --repro repro/session_2025-10-06T142030 --speed 1.5 --window "GameTitle" --delay 5
```

Options:
- `--repro`: Path to replay directory or replay.json (required)
- `--speed`: Playback speed multiplier (default: 1.0)
- `--window`: Target window title (optional)
- `--delay`: Delay before starting in seconds (default: 3.0)

### Exporting Video

Export a session as video:
```bash
python3 replay.py --repro repro/session_2025-10-06T142030 --export-video --video-fps 10
```

### Analyzing Sessions

Use the analyze tool to get session statistics:
```bash
python3 analyze.py --session repro/session_2025-10-06T142030
```

## Output Structure

Each session creates a directory under `repro/`:

```
repro/
  session_2025-10-06T142030/
    replay.json
    summary.txt
    screenshots/
      frame_000000.png
      frame_000010.png
      anomaly_0000_frame_000150.png
```

### replay.json

Contains complete session data:
- Metadata (session name, duration, crash status)
- All actions with timestamps
- All detected anomalies

### summary.txt

Human-readable summary with:
- Session info
- Total actions and anomalies
- List of detected issues

### screenshots/

- Regular frames captured every N steps
- Anomaly frames when issues detected

## Agent Types

### Random Agent

Baseline agent that takes random actions from a predefined key set.

Default keys: `w, a, s, d, space, left, right, up, down`

Perfect for:
- Initial testing
- Finding unexpected crashes
- Stress testing input handling

### Future Agents

- Explorer: Moves toward unexplored regions
- Glitch-Seeker: Spams inputs to find boundary exploits
- LLM-Driven: Uses vision + reasoning for strategic play

## Anomaly Detection

PlaytestAI automatically detects:

1. **Softlocks**: Frame unchanged for extended period
2. **Visual Changes**: Large sudden visual changes
3. **Crashes**: Game process termination
4. **Performance Issues**: CPU/memory spikes (coming soon)

Configure thresholds in the code:
```python
analyzer = Analyzer(
    ssim_threshold=0.95,
    softlock_threshold=30
)
```

## API Usage

You can use PlaytestAI as a library:

```python
from playtest_ai import RandomAgent

agent = RandomAgent(
    window_title="MyGame",
    fps=10,
    max_steps=1000,
    action_keys=['w', 'a', 's', 'd', 'space']
)

agent.run()
```

Custom agent:
```python
from playtest_ai import Agent
import numpy as np

class MyAgent(Agent):
    def decide_action(self, frame: np.ndarray, analysis: dict):
        return ActionType.KEY_PRESS, {'key': 'w', 'duration': 0.1}

agent = MyAgent(window_title="MyGame")
agent.run()
```

## Troubleshooting

### Game not detected

- Ensure the window title matches exactly
- Try running with partial window title
- Check if window is visible and not minimized

### Input not working

- Try running as administrator
- Check if game accepts external input
- Some games may have input protection

### High CPU usage

- Lower FPS: `--fps 5`
- Reduce screenshot frequency in logger
- Disable unnecessary visual analysis

### False anomalies

- Adjust SSIM threshold in analyzer
- Mask dynamic HUD elements
- Increase softlock threshold

## Performance

Typical resource usage:
- CPU: 20-35% per agent
- RAM: 200-500 MB per agent
- Disk: ~1 GB per 1000 steps with screenshots

Optimization tips:
- Use lower FPS for longer sessions
- Reduce screenshot frequency
- Run multiple agents on separate cores

## Roadmap

- [ ] LLM-driven agents
- [ ] Web dashboard for visualization
- [ ] Multi-agent orchestration
- [ ] Linux support
- [ ] Reinforcement learning integration
- [ ] CI/CD integration
- [ ] Performance profiling
- [ ] Memory leak detection

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open a GitHub issue
- Check existing documentation
- Review example sessions

## Acknowledgments

Built with:
- mss for screen capture
- OpenCV for image analysis
- scikit-image for SSIM
- pydirectinput for input injection

