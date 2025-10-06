import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from playtest_ai import ReplayEngine


def main():
    parser = argparse.ArgumentParser(
        description="PlaytestAI Replay - Reproduce recorded game sessions"
    )
    
    parser.add_argument(
        "--repro",
        type=str,
        required=True,
        help="Path to replay directory or replay.json file"
    )
    
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed multiplier (default: 1.0)"
    )
    
    parser.add_argument(
        "--window",
        type=str,
        default=None,
        help="Target window title (optional)"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay before starting replay in seconds (default: 3.0)"
    )
    
    parser.add_argument(
        "--export-video",
        action="store_true",
        help="Export replay as video instead of replaying"
    )
    
    parser.add_argument(
        "--video-fps",
        type=int,
        default=10,
        help="FPS for exported video (default: 10)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("PlaytestAI Replay Engine")
    print("="*60)
    
    replay_engine = ReplayEngine(
        session_path=args.repro,
        playback_speed=args.speed
    )
    
    if args.export_video:
        replay_engine.export_video(fps=args.video_fps)
    else:
        replay_engine.replay(
            window_title=args.window,
            delay_before_start=args.delay
        )


if __name__ == "__main__":
    main()

