#!/usr/bin/env python3
"""
Test script to verify GPU setup on Windows for ML-Agents training.
Copy this to Windows and run it there.
"""

def test_pytorch_gpu():
    """Test PyTorch GPU availability."""
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
                print(f"GPU {i} Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB")
        else:
            print("❌ CUDA not available - will use CPU only")
            
        return torch.cuda.is_available()
        
    except ImportError:
        print("❌ PyTorch not installed")
        return False

def test_mlagents():
    """Test ML-Agents installation."""
    try:
        import mlagents_envs
        print(f"✅ ML-Agents Envs version: {mlagents_envs.__version__}")
        return True
    except ImportError:
        print("❌ ML-Agents not installed")
        return False

def test_simple_training():
    """Test a simple GPU tensor operation."""
    try:
        import torch
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
            x = torch.randn(1000, 1000, device=device)
            y = torch.randn(1000, 1000, device=device)
            z = torch.matmul(x, y)
            print("✅ GPU tensor operations working!")
            return True
        else:
            print("⚠️ No GPU available for testing")
            return False
    except Exception as e:
        print(f"❌ GPU test failed: {e}")
        return False

def main():
    print("=== Windows GPU Setup Test ===\n")
    
    gpu_available = test_pytorch_gpu()
    mlagents_ok = test_mlagents()
    
    print("\n=== Performance Test ===")
    if gpu_available:
        test_simple_training()
    
    print(f"\n=== Results ===")
    print(f"GPU Ready: {'✅' if gpu_available else '❌'}")
    print(f"ML-Agents Ready: {'✅' if mlagents_ok else '❌'}")
    
    if gpu_available and mlagents_ok:
        print("\n🎉 Perfect! Your RTX 4070 Super is ready for ML-Agents training!")
        print("Expected training speed: 10-50x faster than CPU")
    elif mlagents_ok:
        print("\n⚠️ ML-Agents ready but no GPU - training will be slow")
    else:
        print("\n❌ Setup incomplete - follow installation instructions")

if __name__ == "__main__":
    main()
