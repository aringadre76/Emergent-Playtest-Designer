import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from playtest_ai import RandomAgent


def main():
    parser = argparse.ArgumentParser(
        description="PlaytestAI - Automated Game Testing Agent"
    )
    
    parser.add_argument(
        "--window",
        type=str,
        required=True,
        help="Game window title to target"
    )
    
    parser.add_argument(
        "--agent",
        type=str,
        default="random",
        choices=["random"],
        help="Agent type to use (default: random)"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="Maximum number of steps to run (default: 1000)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=10,
        help="Frame capture rate in FPS (default: 10)"
    )
    
    parser.add_argument(
        "--session-name",
        type=str,
        default=None,
        help="Custom session name (default: auto-generated)"
    )
    
    parser.add_argument(
        "--keys",
        type=str,
        nargs="+",
        default=None,
        help="Custom key list for random agent (e.g., w a s d space)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("PlaytestAI - Automated Game Testing")
    print("="*60)
    print(f"Window: {args.window}")
    print(f"Agent: {args.agent}")
    print(f"Steps: {args.steps}")
    print(f"FPS: {args.fps}")
    print("="*60)
    
    if args.agent == "random":
        agent = RandomAgent(
            window_title=args.window,
            session_name=args.session_name,
            fps=args.fps,
            max_steps=args.steps,
            action_keys=args.keys
        )
    else:
        print(f"Unknown agent type: {args.agent}")
        sys.exit(1)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        agent.stop()
    
    stats = agent.get_stats()
    print("\nFinal Statistics:")
    print(f"  Steps completed: {stats['current_step']}")
    print(f"  Anomalies detected: {stats['total_anomalies']}")
    print(f"  Session path: {stats['session_path']}")


if __name__ == "__main__":
    main()

