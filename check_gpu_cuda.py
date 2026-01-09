"""
Comprehensive GPU and CUDA Diagnostic Tool
Checks if the system is ready for GPU acceleration with the DEM Downscaling plugin
"""
import sys
import os
import platform
import subprocess

def check_nvidia_gpu():
    """Check for NVIDIA GPU and driver information"""
    print("=" * 70)
    print("GPU and CUDA Diagnostic for DEM Downscaling Plugin")
    print("=" * 70)
    print()
    
    print("1. Checking NVIDIA GPU and Driver...")
    print("-" * 70)
    
    try:
        # Try to run nvidia-smi
        result = subprocess.run(['nvidia-smi'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5,
                              shell=True)
        
        if result.returncode == 0:
            print("[OK] NVIDIA GPU Detected!")
            print()
            print("GPU Information:")
            print(result.stdout)
            
            # Extract CUDA version from nvidia-smi output
            lines = result.stdout.split('\n')
            cuda_version = None
            driver_version = None
            gpu_name = None
            
            for line in lines:
                if 'CUDA Version' in line:
                    parts = line.split('CUDA Version:')
                    if len(parts) > 1:
                        cuda_version = parts[1].strip().split()[0]
                if 'Driver Version' in line:
                    parts = line.split('Driver Version:')
                    if len(parts) > 1:
                        driver_version = parts[1].strip().split()[0]
                if 'NVIDIA' in line and ('GeForce' in line or 'Quadro' in line or 'Tesla' in line or 'RTX' in line or 'GTX' in line):
                    gpu_name = line.strip()
            
            if cuda_version:
                print(f"\n   CUDA Driver Version: {cuda_version}")
            if driver_version:
                print(f"   NVIDIA Driver Version: {driver_version}")
            if gpu_name:
                print(f"   GPU Name: {gpu_name}")
            
            return True, cuda_version, driver_version, gpu_name
        else:
            print("[X] nvidia-smi failed or not available")
            return False, None, None, None
    except FileNotFoundError:
        print("[X] NVIDIA GPU Driver not installed or nvidia-smi not found")
        print()
        print("   This usually means:")
        print("   - No NVIDIA GPU in the system")
        print("   - NVIDIA drivers are not installed")
        print("   - nvidia-smi is not in PATH")
        return False, None, None, None
    except Exception as e:
        print(f"[X] Error checking GPU: {e}")
        return False, None, None, None

def check_cuda_toolkit():
    """Check for CUDA Toolkit installation"""
    print()
    print("2. Checking CUDA Toolkit Installation...")
    print("-" * 70)
    
    if platform.system() != 'Windows':
        print("⚠️  This diagnostic is designed for Windows")
        return False, None
    
    cuda_installations = []
    
    # Check common installation paths
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    
    search_paths = [
        os.path.join(program_files, 'NVIDIA GPU Computing Toolkit', 'CUDA'),
        os.path.join(program_files_x86, 'NVIDIA GPU Computing Toolkit', 'CUDA'),
    ]
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            try:
                for item in os.listdir(base_path):
                    version_path = os.path.join(base_path, item)
                    if os.path.isdir(version_path):
                        bin_path = os.path.join(version_path, 'bin')
                        nvcc_path = os.path.join(bin_path, 'nvcc.exe')
                        if os.path.exists(nvcc_path):
                            cuda_installations.append({
                                'version': item,
                                'path': version_path,
                                'bin_path': bin_path
                            })
            except Exception as e:
                pass
    
    if cuda_installations:
        print(f"[OK] Found {len(cuda_installations)} CUDA Toolkit installation(s):")
        for cuda in cuda_installations:
            print(f"   - Version {cuda['version']} at {cuda['path']}")
        
        # Check if in PATH
        path_env = os.environ.get('PATH', '')
        in_path = False
        for cuda in cuda_installations:
            if cuda['bin_path'] in path_env:
                print(f"   [OK] CUDA {cuda['version']} is in PATH")
                in_path = True
                break
        
        if not in_path:
            latest = max(cuda_installations, key=lambda x: x['version'])
            print(f"   [WARNING] CUDA {latest['version']} NOT in PATH (this may cause DLL errors)")
            print(f"   Fix: Add to PATH: {latest['bin_path']}")
        
        latest = max(cuda_installations, key=lambda x: x['version'])
        return True, latest
    else:
        print("[X] CUDA Toolkit not found")
        print()
        print("   To install CUDA Toolkit:")
        print("   1. Visit: https://developer.nvidia.com/cuda-downloads")
        print("   2. Download and install CUDA Toolkit")
        print("   3. Restart your computer")
        print("   4. Run this diagnostic again")
        return False, None

def check_cupy():
    """Check CuPy installation and GPU access"""
    print()
    print("3. Checking CuPy Installation...")
    print("-" * 70)
    
    try:
        import cupy as cp
        print("[OK] CuPy is installed")
        
        try:
            if cp.cuda.is_available():
                print("[OK] CUDA is available in CuPy")
                
                # Get device info
                try:
                    device = cp.cuda.Device(0)
                    device.use()
                    
                    # Get compute capability
                    compute_cap = device.compute_capability
                    print(f"   GPU Compute Capability: {compute_cap[0]}.{compute_cap[1]}")
                    
                    # Get device properties
                    try:
                        props = cp.cuda.runtime.getDeviceProperties(0)
                        if 'name' in props:
                            gpu_name = props['name'].decode('utf-8') if isinstance(props['name'], bytes) else props['name']
                            print(f"   GPU Name: {gpu_name}")
                        
                        if 'totalGlobalMem' in props:
                            total_mem = props['totalGlobalMem'] / (1024**3)  # GB
                            print(f"   GPU Memory: {total_mem:.2f} GB")
                    except:
                        pass
                    
                        # Test GPU operations
                    try:
                        print()
                        print("   Testing GPU operations...")
                        test_array = cp.array([1.0, 2.0, 3.0, 4.0, 5.0])
                        result = cp.sum(test_array)
                        result_cpu = float(cp.asnumpy(result))
                        print(f"   [OK] GPU test successful: sum([1,2,3,4,5]) = {result_cpu}")
                        
                        # Test convolution-like operation
                        test_2d = cp.random.rand(100, 100)
                        result_2d = cp.mean(test_2d)
                        print(f"   [OK] GPU 2D array test successful")
                        
                        return True, "[OK] GPU is working correctly!"
                    except Exception as e:
                        return False, f"GPU test failed: {str(e)}"
                    
                except Exception as e:
                    return False, f"Error accessing GPU device: {str(e)}"
            else:
                return False, "CUDA is not available (check drivers and CUDA Toolkit)"
        except Exception as e:
            error_str = str(e)
            if "nvrtc" in error_str.lower() or "dll" in error_str.lower():
                return False, f"CUDA DLL error: {error_str}\n   This usually means CUDA Toolkit is not installed or not in PATH"
            else:
                return False, f"CuPy CUDA error: {error_str}"
                
    except ImportError:
        print("[X] CuPy is not installed")
        print()
        print("   To install CuPy:")
        print("   1. Determine your CUDA version (from step 1)")
        print("   2. Install matching CuPy:")
        print("      For CUDA 11.x: python -m pip install cupy-cuda11x")
        print("      For CUDA 12.x: python -m pip install cupy-cuda12x")
        print("   3. Restart QGIS")
        return False, "CuPy not installed"
    except Exception as e:
        return False, f"CuPy error: {str(e)}"

def get_recommendations(gpu_ok, cuda_toolkit_ok, cupy_ok, cupy_message):
    """Provide recommendations based on diagnostic results"""
    print()
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print()
    
    all_ok = gpu_ok and cuda_toolkit_ok and cupy_ok
    
    if all_ok:
        print("[OK] SYSTEM READY FOR GPU ACCELERATION!")
        print()
        print("Your laptop is fully configured for GPU processing.")
        print("The DEM Downscaling plugin will use GPU acceleration,")
        print("which is about 8x faster than CPU processing.")
    else:
        print("[WARNING] SYSTEM NOT FULLY CONFIGURED FOR GPU")
        print()
        
        if not gpu_ok:
            print("[X] NVIDIA GPU/Driver Issue:")
            print("   - No NVIDIA GPU detected, or")
            print("   - NVIDIA drivers not installed")
            print()
            print("   Solution:")
            print("   1. Verify you have an NVIDIA GPU")
            print("   2. Install NVIDIA drivers from: https://www.nvidia.com/drivers")
            print("   3. Restart your computer")
        
        if not cuda_toolkit_ok:
            print()
            print("[X] CUDA Toolkit Not Installed:")
            print("   - CUDA Toolkit is required for GPU processing")
            print("   - Even with GPU drivers, you need CUDA Toolkit")
            print()
            print("   Solution:")
            print("   1. Download CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
            print("   2. Install CUDA Toolkit (match version with CuPy)")
            print("   3. Restart your computer")
            print("   4. Run fix_cuda_dll.py to verify")
        
        if not cupy_ok:
            print()
            print("[X] CuPy Issue:")
            print(f"   {cupy_message}")
            print()
            if "not installed" in cupy_message.lower():
                print("   Solution:")
                print("   1. Check CUDA version from nvidia-smi")
                print("   2. Install matching CuPy:")
                print("      For CUDA 11.x: python -m pip install cupy-cuda11x")
                print("      For CUDA 12.x: python -m pip install cupy-cuda12x")
            elif "dll" in cupy_message.lower():
                print("   Solution:")
                print("   1. Install CUDA Toolkit (see above)")
                print("   2. Add CUDA bin to PATH")
                print("   3. Run fix_cuda_dll.py to auto-fix PATH")
        
        print()
        print("=" * 70)
        print("FALLBACK OPTION: CPU Processing")
        print("=" * 70)
        print()
        print("Even without GPU, the plugin will work using CPU:")
        print("  • Install SciPy for 10-100x speedup on CPU:")
        print("    python -m pip install scipy")
        print("  • Plugin will automatically use CPU processing")
        print("  • CPU processing is still fast for most DEMs")

def main():
    # Check GPU
    gpu_ok, cuda_version, driver_version, gpu_name = check_nvidia_gpu()
    
    # Check CUDA Toolkit
    cuda_toolkit_ok, cuda_toolkit_info = check_cuda_toolkit()
    
    # Check CuPy
    cupy_ok, cupy_message = check_cupy()
    
    # Recommendations
    get_recommendations(gpu_ok, cuda_toolkit_ok, cupy_ok, cupy_message)
    
    print()
    print("=" * 70)
    print("Diagnostic Complete")
    print("=" * 70)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass

