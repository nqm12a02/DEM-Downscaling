"""
Script to automatically fix CUDA DLL issues on Windows
This script:
1. Checks if CUDA Toolkit is installed
2. Finds CUDA installation paths
3. Adds CUDA to PATH if needed
4. Tests if CuPy can now access CUDA DLLs
"""
import os
import sys
import platform
import subprocess

def find_cuda_installations():
    """Find all CUDA Toolkit installations on Windows"""
    cuda_installations = []
    
    if platform.system() != 'Windows':
        return cuda_installations
    
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
                                'bin_path': bin_path,
                                'nvcc_path': nvcc_path
                            })
            except Exception as e:
                print(f"Error scanning {base_path}: {e}")
    
    return cuda_installations

def check_path_for_cuda():
    """Check if CUDA paths are in PATH environment variable"""
    path_env = os.environ.get('PATH', '')
    path_dirs = path_env.split(os.pathsep)
    
    cuda_in_path = []
    for path_dir in path_dirs:
        if 'CUDA' in path_dir.upper() and 'bin' in path_dir.lower():
            cuda_in_path.append(path_dir)
    
    return cuda_in_path

def get_system_path():
    """Get system PATH (User + System)"""
    import winreg
    
    system_path = []
    user_path = []
    
    try:
        # Get System PATH
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                          r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                          0, winreg.KEY_READ) as key:
            system_path = winreg.QueryValueEx(key, "Path")[0].split(os.pathsep)
    except:
        pass
    
    try:
        # Get User PATH
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                          r"Environment",
                          0, winreg.KEY_READ) as key:
            user_path = winreg.QueryValueEx(key, "Path")[0].split(os.pathsep)
    except:
        pass
    
    return system_path, user_path

def add_cuda_to_path(cuda_bin_path, user_only=True):
    """Add CUDA bin path to PATH environment variable"""
    import winreg
    
    if not os.path.exists(cuda_bin_path):
        return False, "CUDA bin path does not exist"
    
    try:
        if user_only:
            # Add to User PATH
            key_path = r"Environment"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        else:
            # Add to System PATH (requires admin)
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
            path_list = current_path.split(os.pathsep)
        except FileNotFoundError:
            path_list = []
        
        if cuda_bin_path not in path_list:
            path_list.append(cuda_bin_path)
            new_path = os.pathsep.join(path_list)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            return True, "CUDA added to PATH successfully. Please restart your terminal/QGIS for changes to take effect."
        else:
            winreg.CloseKey(key)
            return True, "CUDA already in PATH"
    except PermissionError:
        return False, "Permission denied. Please run as Administrator to add to System PATH."
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_cupy_import():
    """Test if CuPy can now import successfully"""
    try:
        import cupy as cp
        if cp.cuda.is_available():
            try:
                # Test GPU access
                test_array = cp.array([1.0, 2.0, 3.0])
                _ = cp.asnumpy(test_array)
                return True, "CuPy is working correctly with GPU!"
            except Exception as e:
                return False, f"CuPy imported but GPU test failed: {str(e)}"
        else:
            return False, "CuPy imported but CUDA is not available"
    except ImportError:
        return False, "CuPy is not installed"
    except Exception as e:
        error_str = str(e)
        if "nvrtc" in error_str.lower() or ("dll" in error_str.lower() and "cuda" in error_str.lower()):
            return False, f"CUDA DLL error: {error_str}"
        else:
            return False, f"CuPy import error: {error_str}"

def main():
    print("=" * 70)
    print("CUDA DLL Fix Utility for QGIS DEM Downscaling Plugin")
    print("=" * 70)
    print()
    
    # Step 1: Check for CUDA installations
    print("Step 1: Checking for CUDA Toolkit installations...")
    cuda_installations = find_cuda_installations()
    
    if not cuda_installations:
        print("❌ No CUDA Toolkit installations found!")
        print()
        print("Solution:")
        print("1. Download CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads")
        print("2. Install CUDA Toolkit (choose version matching your CuPy installation)")
        print("3. Restart your computer after installation")
        print("4. Run this script again to verify")
        return
    
    print(f"✅ Found {len(cuda_installations)} CUDA installation(s):")
    for cuda in cuda_installations:
        print(f"   - Version {cuda['version']} at {cuda['path']}")
    print()
    
    # Step 2: Check PATH
    print("Step 2: Checking PATH environment variable...")
    cuda_in_path = check_path_for_cuda()
    
    if cuda_in_path:
        print(f"✅ CUDA already in PATH:")
        for path in cuda_in_path:
            print(f"   - {path}")
    else:
        print("⚠️  CUDA not found in PATH!")
        print()
        # Use the latest CUDA version
        latest_cuda = max(cuda_installations, key=lambda x: x['version'])
        print(f"Attempting to add CUDA {latest_cuda['version']} to PATH...")
        
        success, message = add_cuda_to_path(latest_cuda['bin_path'], user_only=True)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            print()
            print("Manual fix:")
            print(f"1. Add this path to your PATH environment variable:")
            print(f"   {latest_cuda['bin_path']}")
            print()
            print("2. To do this:")
            print("   a. Right-click 'This PC' → Properties")
            print("   b. Advanced system settings → Environment Variables")
            print("   c. Edit 'Path' in User variables")
            print("   d. Add new entry: " + latest_cuda['bin_path'])
            print("   e. Click OK and restart QGIS")
    print()
    
    # Step 3: Test CuPy
    print("Step 3: Testing CuPy...")
    cupy_works, cupy_message = test_cupy_import()
    
    if cupy_works:
        print(f"✅ {cupy_message}")
        print()
        print("=" * 70)
        print("SUCCESS! CUDA is working correctly.")
        print("You can now use GPU acceleration in the DEM Downscaling plugin.")
        print("=" * 70)
    else:
        print(f"❌ {cupy_message}")
        print()
        
        if "not installed" in cupy_message:
            print("Solution: Install CuPy matching your CUDA version")
            if cuda_installations:
                latest_cuda = max(cuda_installations, key=lambda x: x['version'])
                cuda_version = latest_cuda['version'].split('.')[0]  # e.g., "11" from "11.8"
                print(f"   For CUDA {cuda_version}.x, run:")
                print(f'   python -m pip install cupy-cuda{cuda_version}x')
        elif "DLL" in cupy_message or "nvrtc" in cupy_message:
            print("Solution:")
            print("1. Ensure CUDA Toolkit is properly installed")
            print("2. Restart your computer (required after CUDA installation)")
            print("3. Restart QGIS completely")
            print("4. If still not working, check that CUDA bin is in PATH")
            if cuda_installations:
                latest_cuda = max(cuda_installations, key=lambda x: x['version'])
                print(f"   CUDA bin path: {latest_cuda['bin_path']}")
        
        print()
        print("=" * 70)
        print("The plugin will automatically fallback to CPU processing.")
        print("GPU is optional - CPU processing (with SciPy) is still fast!")
        print("=" * 70)

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
    input()



