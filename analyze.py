import argparse
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from playtest_ai import SessionLogger


def main():
    parser = argparse.ArgumentParser(
        description="PlaytestAI Analyzer - Analyze recorded sessions"
    )
    
    parser.add_argument(
        "--session",
        type=str,
        required=True,
        help="Path to session directory"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed action list"
    )
    
    args = parser.parse_args()
    
    session_data = SessionLogger.load_session(args.session)
    metadata = session_data.get("metadata", {})
    actions = session_data.get("actions", [])
    anomalies = session_data.get("anomalies", [])
    
    print("="*60)
    print("Session Analysis")
    print("="*60)
    print(f"Session Name: {metadata.get('session_name', 'Unknown')}")
    print(f"Window: {metadata.get('window_title', 'Unknown')}")
    print(f"Agent Type: {metadata.get('agent_type', 'Unknown')}")
    print(f"Start Time: {metadata.get('start_time', 'Unknown')}")
    print(f"End Time: {metadata.get('end_time', 'Unknown')}")
    print(f"Duration: {metadata.get('duration_seconds', 0):.2f} seconds")
    print(f"Max Steps: {metadata.get('max_steps', 'Unknown')}")
    print(f"FPS: {metadata.get('fps', 'Unknown')}")
    print()
    
    print(f"Total Actions: {len(actions)}")
    print(f"Total Anomalies: {len(anomalies)}")
    print(f"Crashed: {metadata.get('crashed', False)}")
    
    if metadata.get('crashed'):
        crash_info = metadata.get('crash_info', {})
        print(f"\nCrash Information:")
        print(f"  Reason: {crash_info.get('reason', 'Unknown')}")
        print(f"  Step: {crash_info.get('step', 'Unknown')}")
    
    if anomalies:
        print(f"\n{'='*60}")
        print("Anomalies Detected:")
        print("="*60)
        
        anomaly_types = {}
        for anomaly in anomalies:
            atype = anomaly.get('type', 'unknown')
            anomaly_types[atype] = anomaly_types.get(atype, 0) + 1
        
        print("\nSummary by Type:")
        for atype, count in anomaly_types.items():
            print(f"  {atype}: {count}")
        
        print("\nDetailed List:")
        for i, anomaly in enumerate(anomalies, 1):
            print(f"\n  {i}. Type: {anomaly.get('type', 'unknown')}")
            print(f"     Time: {anomaly.get('timestamp', 0):.2f}s")
            print(f"     Frame: {anomaly.get('frame_number', 'N/A')}")
            print(f"     Description: {anomaly.get('description', 'No description')}")
            print(f"     Severity: {anomaly.get('severity', 'unknown')}")
            if 'screenshot' in anomaly:
                print(f"     Screenshot: {anomaly['screenshot']}")
    
    if args.verbose and actions:
        print(f"\n{'='*60}")
        print("Action List:")
        print("="*60)
        
        action_types = {}
        for action in actions:
            atype = action.get('action_type', 'unknown')
            action_types[atype] = action_types.get(atype, 0) + 1
        
        print("\nSummary by Type:")
        for atype, count in action_types.items():
            print(f"  {atype}: {count}")
        
        print("\nFirst 20 Actions:")
        for i, action in enumerate(actions[:20], 1):
            print(f"  {i}. [{action.get('timestamp', 0):.2f}s] {action.get('action_type', 'unknown')}: {action.get('action_data', {})}")
        
        if len(actions) > 20:
            print(f"\n  ... and {len(actions) - 20} more actions")
    
    session_path = Path(args.session)
    screenshots_dir = session_path / "screenshots"
    
    if screenshots_dir.exists():
        screenshot_count = len(list(screenshots_dir.glob("*.png")))
        print(f"\nScreenshots captured: {screenshot_count}")
    
    print("\n" + "="*60)
    print("Analysis Complete")
    print("="*60)


if __name__ == "__main__":
    main()

