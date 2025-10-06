import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playtest_ai import RandomAgent


def simple_test():
    print("Simple PlaytestAI Test")
    print("This will capture your entire screen and send random inputs")
    print("Press Ctrl+C to stop")
    print()
    
    input("Press Enter to start 10-step test...")
    
    agent = RandomAgent(
        window_title="",
        session_name="simple_test",
        fps=5,
        max_steps=10,
        action_keys=['space', 'enter']
    )
    
    agent.run()
    
    print("\nTest complete! Check repro/simple_test/ for results")


if __name__ == "__main__":
    simple_test()

