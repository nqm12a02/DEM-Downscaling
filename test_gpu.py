"""
Test script to check GPU availability
Run this in QGIS Python Console to diagnose GPU issues
"""
try:
    import cupy as cp
    print("CuPy imported successfully")
    
    if cp.cuda.is_available():
        print(f"CUDA is available")
        print(f"Number of devices: {cp.cuda.runtime.getDeviceCount()}")
        
        for i in range(cp.cuda.runtime.getDeviceCount()):
            device = cp.cuda.Device(i)
            device.use()
            props = cp.cuda.runtime.getDeviceProperties(i)
            print(f"Device {i}: {props['name'].decode('utf-8')}")
            print(f"  Compute Capability: {device.compute_capability}")
            print(f"  Total Memory: {props['totalGlobalMem'] / 1024**3:.2f} GB")
            
            # Test with small array
            try:
                test = cp.array([1.0, 2.0, 3.0])
                result = cp.asnumpy(test)
                print(f"  GPU test: SUCCESS")
            except Exception as e:
                print(f"  GPU test: FAILED - {str(e)}")
    else:
        print("CUDA is NOT available")
        print("Possible reasons:")
        print("1. No NVIDIA GPU")
        print("2. CUDA drivers not installed")
        print("3. CuPy version doesn't match CUDA version")
        
except ImportError as e:
    print(f"CuPy is NOT installed: {str(e)}")
    print("Install with: python -m pip install cupy-cuda11x (or cupy-cuda12x)")
except Exception as e:
    print(f"Error checking GPU: {str(e)}")



