#!/usr/bin/env python3
"""
System verification test - ensures everything still works after cleanup
"""

import sys
import os
sys.path.insert(0, '..')

def test_gpu_setup():
    """Test GPU setup"""
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        
        return True
    except Exception as e:
        print(f"❌ GPU test failed: {e}")
        return False

def test_mlagents():
    """Test ML-Agents installation"""
    try:
        import mlagents_envs
        print(f"✅ ML-Agents Envs: {mlagents_envs.__version__}")
        return True
    except Exception as e:
        print(f"❌ ML-Agents test failed: {e}")
        return False

def test_unity_build():
    """Test Unity build exists"""
    build_path = "../build/EmergentPlaytestAI.exe"
    if not os.path.exists(build_path):
        # Try relative path from project root
        build_path = "build/EmergentPlaytestAI.exe"
    if os.path.exists(build_path):
        print(f"✅ Unity Build: {build_path}")
        return True
    else:
        print(f"❌ Unity build not found: {build_path}")
        return False

def test_package_import():
    """Test main package imports"""
    try:
        from emergent_playtest_designer.core.config import UnityConfig
        print(f"✅ Package Import: emergent_playtest_designer")
        return True
    except Exception as e:
        print(f"❌ Package import failed: {e}")
        return False

def main():
    print("🔍 SYSTEM VERIFICATION TEST")
    print("=" * 50)
    
    tests = [
        ("GPU Setup", test_gpu_setup),
        ("ML-Agents", test_mlagents), 
        ("Unity Build", test_unity_build),
        ("Package Import", test_package_import)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 Testing {name}...")
        success = test_func()
        results.append(success)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("✅ System is ready for ML-Agents training!")
    else:
        print(f"⚠️ {passed}/{total} tests passed")
        print("Some components may need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
