"""
Check CuPy availability and compatibility with CUDA 13.0
"""
import sys
import subprocess

def check_cupy_installation():
    """Check if CuPy is installed"""
    print("=" * 70)
    print("CuPy Installation Check")
    print("=" * 70)
    print()
    
    try:
        import cupy as cp
        print("[OK] CuPy is installed")
        print(f"    Version: {cp.__version__}")
        
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
                    test_array = cp.array([1.0, 2.0, 3.0])
                    result = float(cp.asnumpy(cp.sum(test_array)))
                    print(f"[OK] GPU test successful: sum([1,2,3]) = {result}")
                    return True
                except Exception as e:
                    print(f"[X] GPU test failed: {e}")
                    return False
            else:
                print("[X] CUDA is not available in CuPy")
                return False
        except Exception as e:
            print(f"[X] CuPy CUDA error: {e}")
            return False
    except ImportError:
        print("[X] CuPy is NOT installed")
        return False

def check_pip_availability():
    """Check if pip can find CuPy packages"""
    print()
    print("=" * 70)
    print("Checking available CuPy packages on PyPI")
    print("=" * 70)
    print()
    
    cupy_versions = [
        'cupy-cuda12x',
        'cupy-cuda11x',
        'cupy-cuda10x',
    ]
    
    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    print()
    
    for version in cupy_versions:
        try:
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'search', version],
                capture_output=True,
                text=True,
                timeout=10
            )
            # pip search is deprecated, use pip index instead
            print(f"Checking {version}... (pip search is deprecated, trying alternative)")
        except:
            pass
        
        # Try to get info directly
        try:
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'index', 'versions', version],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"[OK] {version} is available")
                print(f"    {result.stdout.strip()}")
            else:
                # Try pip show
                result2 = subprocess.run(
                    [python_exe, '-m', 'pip', 'show', version],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result2.returncode == 0:
                    print(f"[OK] {version} information:")
                    for line in result2.stdout.split('\n'):
                        if line.startswith('Version:') or line.startswith('Name:'):
                            print(f"    {line}")
        except Exception as e:
            print(f"[?] Could not check {version}: {str(e)[:50]}")

def check_cuda_toolkit_compatibility():
    """Check CUDA Toolkit version compatibility"""
    print()
    print("=" * 70)
    print("CUDA Toolkit Compatibility Analysis")
    print("=" * 70)
    print()
    
    print("Your system:")
    print("  - CUDA Driver: 13.0")
    print("  - CUDA Toolkit: 13.0")
    print()
    
    print("CuPy package compatibility:")
    print("  - cupy-cuda12x: Supports CUDA 12.0 - 12.6")
    print("    -> May work with CUDA 13.0 driver (backward compatible)")
    print("  - cupy-cuda11x: Supports CUDA 11.0 - 11.8")
    print("    -> Older, but stable")
    print("  - cupy-cuda13x: NOT YET AVAILABLE (as of 2024)")
    print()
    
    print("Recommendation:")
    print("  1. Try installing cupy-cuda12x first:")
    print("     python -m pip install cupy-cuda12x")
    print()
    print("  2. If that doesn't work, try cupy-cuda11x:")
    print("     python -m pip install cupy-cuda11x")
    print()
    print("  3. If both fail, you may need to:")
    print("     - Wait for CuPy to support CUDA 13.0")
    print("     - Or downgrade to CUDA Toolkit 12.6")

def main():
    # Check if CuPy is installed
    cupy_installed = check_cupy_installation()
    
    if not cupy_installed:
        # Check package availability
        check_pip_availability()
        
        # Check compatibility
        check_cuda_toolkit_compatibility()
        
        print()
        print("=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print()
        print("To install CuPy, run this command in Command Prompt:")
        print("(NOT in QGIS Python Console!)")
        print()
        print('  "C:\\Program Files\\QGIS 3.40.13\\bin\\python-qgis-ltr.bat" -m pip install cupy-cuda12x')
        print()
        print("Or use the batch file: INSTALL_CUPY_NOW.bat")
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

