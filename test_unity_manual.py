#!/usr/bin/env python3
"""
Test Unity executable with command line arguments to see if it responds to ML-Agents.
"""

import subprocess
import time
import sys

print("🔧 Testing Unity executable manually...")

# First, test if Unity executable exists and runs
try:
    print("1️⃣ Testing if Unity executable exists...")
    import os
    unity_path = "./build/EmergentPlaytestAI.exe"
    
    if not os.path.exists(unity_path):
        print(f"❌ Unity executable not found at: {unity_path}")
        sys.exit(1)
    
    print(f"✅ Unity executable found: {unity_path}")
    
    print("2️⃣ Testing Unity executable with ML-Agents arguments...")
    
    # Try running Unity with ML-Agents specific arguments
    cmd = [
        unity_path,
        "--mlagents-port", "5004",
        "--mlagents-base-port", "5005",
        "--no-graphics"  # Run headless for testing
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    # Start Unity process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit to see if it starts successfully
    time.sleep(3)
    
    if process.poll() is None:
        print("✅ Unity is running with ML-Agents arguments!")
        print("🔄 Terminating Unity process...")
        process.terminate()
        process.wait()
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Unity exited with code: {process.returncode}")
        if stdout:
            print(f"📝 STDOUT: {stdout[:500]}")
        if stderr:
            print(f"❌ STDERR: {stderr[:500]}")
    
except Exception as e:
    print(f"❌ Error testing Unity: {e}")

print("\n💡 NEXT STEPS:")
print("1. Make sure you rebuilt Unity after adding Behavior Parameters")
print("2. Check Unity Package Manager - ML-Agents version should be 2.0.1") 
print("3. In Unity, verify PlaytestAgent has all required components")
print("4. Try building in Development mode for better debugging")
