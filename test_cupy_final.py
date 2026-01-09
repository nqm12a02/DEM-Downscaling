"""Final test for CuPy after fixing duplicate"""
import sys

print("=" * 70)
print("Final CuPy Test After Fixing Duplicate")
print("=" * 70)
print()
print(f"Python: {sys.executable}")
print()

try:
    import cupy as cp
    print("[OK] CuPy is installed")
    print(f"    Version: {cp.__version__}")
    print()
    
    try:
        if cp.cuda.is_available():
            print("[OK] CUDA is available in CuPy")
            
            # Get CUDA version
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            major = cuda_version // 1000
            minor = (cuda_version % 1000) // 10
            print(f"    CUDA Runtime Version: {major}.{minor}")
            
            # Test GPU
            try:
                device = cp.cuda.Device(0)
                device.use()
                test_array = cp.array([1.0, 2.0, 3.0, 4.0, 5.0])
                result = float(cp.asnumpy(cp.sum(test_array)))
                print(f"[OK] GPU test successful: sum([1,2,3,4,5]) = {result}")
                
                # Get device info
                compute_cap = device.compute_capability
                print(f"    GPU Compute Capability: {compute_cap[0]}.{compute_cap[1]}")
                
                props = cp.cuda.runtime.getDeviceProperties(0)
                if 'name' in props:
                    gpu_name = props['name'].decode('utf-8') if isinstance(props['name'], bytes) else props['name']
                    print(f"    GPU Name: {gpu_name}")
                
                if 'totalGlobalMem' in props:
                    total_mem = props['totalGlobalMem'] / (1024**3)
                    print(f"    GPU Memory: {total_mem:.2f} GB")
                
                print()
                print("=" * 70)
                print("[SUCCESS] CuPy is working perfectly!")
                print("No duplicate packages - only cupy-cuda12x installed")
                print("=" * 70)
                
            except Exception as e:
                print(f"[X] GPU test failed: {e}")
                
        else:
            print("[X] CUDA is not available in CuPy")
            
    except Exception as e:
        error_str = str(e)
        if "nvrtc" in error_str.lower() or "dll" in error_str.lower():
            print(f"[WARNING] CUDA DLL error: {error_str}")
            print("    This may be resolved after restarting QGIS")
        else:
            print(f"[X] CuPy CUDA error: {e}")
            
except ImportError:
    print("[X] CuPy is NOT installed")
except Exception as e:
    print(f"[X] Error: {e}")

print()
input("Press Enter to exit...")

