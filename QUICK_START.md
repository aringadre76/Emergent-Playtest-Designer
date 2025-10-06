# Quick Start Guide

Get PlaytestAI up and running in 5 minutes.

## Step 1: Install

```bash
pip install -r requirements.txt
```

Optional Windows dependency for better window detection:
```bash
pip install pywin32
```

## Step 2: Test the Installation

Run the simple test:
```bash
python3 examples/simple_test.py
```

This will do a 10-step test with random inputs.

## Step 3: Test with a Real Game

### Example: Testing Celeste

1. Launch Celeste
2. Run PlaytestAI:
```bash
python3 playtest.py --window "Celeste" --steps 500 --fps 10
```

3. Watch as the agent plays randomly
4. Check results in `repro/session_TIMESTAMP/`

### Example: Testing Hollow Knight

```bash
python3 playtest.py --window "Hollow Knight" --steps 1000 --keys left right up down z x c
```

### Example: Generic Game

```bash
python3 playtest.py --window "YourGame" --steps 2000 --fps 15
```

## Step 4: Review Results

Check the session directory:
```bash
ls repro/session_TIMESTAMP/
```

You'll find:
- `replay.json` - Complete action log
- `summary.txt` - Human-readable summary
- `screenshots/` - Captured frames

## Step 5: Replay a Session

Reproduce what the agent did:
```bash
python3 replay.py --repro repro/session_TIMESTAMP
```

## Step 6: Analyze Results

Get detailed statistics:
```bash
python3 analyze.py --session repro/session_TIMESTAMP --verbose
```

## Common Use Cases

### Overnight Testing

Run for 10,000 steps to find rare crashes:
```bash
python3 playtest.py --window "YourGame" --steps 10000 --fps 5
```

### Custom Keys

Test a platformer with specific controls:
```bash
python3 playtest.py --window "YourGame" --keys left right space z x --steps 2000
```

### Fast Exploration

High FPS for rapid testing:
```bash
python3 playtest.py --window "YourGame" --fps 20 --steps 5000
```

## Tips

1. Start with low step counts (100-500) to verify setup
2. Adjust FPS based on game speed and your CPU
3. Use --keys to limit actions to relevant game controls
4. Check summary.txt first for quick overview
5. Use replay to understand what caused issues

## Troubleshooting

### Game not detected
- Use partial window title: "Celeste" instead of "Celeste v1.4.0.0"
- Check Task Manager for exact window name

### No input reaching game
- Run as administrator
- Check if game accepts background input
- Try clicking on game window during countdown

### Too many false anomalies
- Increase softlock threshold in code
- Lower FPS to reduce sensitivity

## Next Steps

- Read full README.md for advanced features
- Check examples/custom_agent.py for custom behavior
- Modify analyzer thresholds for your game
- Create game-specific agent subclasses

## Getting Help

- Check README.md for full documentation
- Review example scripts in examples/
- Open GitHub issue for bugs

