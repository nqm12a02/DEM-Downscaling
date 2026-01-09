"""Check CuPy availability in QGIS Python environment"""
import sys
import os

print("=" * 70)
print("CuPy Check in QGIS Python Environment")
print("=" * 70)
print()
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version.split()[0]}")
print()

# Show sys.path
print("Python search paths:")
for i, path in enumerate(sys.path[:10], 1):
    print(f"  {i}. {path}")
if len(sys.path) > 10:
    print(f"  ... and {len(sys.path) - 10} more paths")
print()

# Check user site-packages
try:
    import site
    user_site = site.getusersitepackages()
    print(f"User site-packages: {user_site}")
    print(f"Exists: {os.path.exists(user_site)}")
    
    # Check if CuPy exists in user site-packages
    cupy_path = os.path.join(user_site, 'cupy')
    print(f"CuPy path: {cupy_path}")
    print(f"CuPy exists: {os.path.exists(cupy_path)}")
    
    if user_site not in sys.path:
        print("[WARNING] User site-packages NOT in sys.path!")
        print("Adding to sys.path...")
        sys.path.insert(0, user_site)
    else:
        print("[OK] User site-packages is in sys.path")
        
except Exception as e:
    print(f"[ERROR] Error checking site-packages: {e}")

print()

# Try to import CuPy
print("Attempting to import CuPy...")
try:
    import cupy as cp
    print("[SUCCESS] CuPy imported successfully!")
    print(f"    Version: {cp.__version__}")
    print(f"    Location: {cp.__file__}")
    print()
    
    # Check CUDA
    try:
        if cp.cuda.is_available():
            print("[SUCCESS] CUDA is available!")
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            major = cuda_version // 1000
            minor = (cuda_version % 1000) // 10
            print(f"    CUDA Runtime Version: {major}.{minor}")
            
            # Quick GPU test
            test = cp.array([1.0, 2.0, 3.0])
            result = float(cp.asnumpy(cp.sum(test)))
            print(f"[SUCCESS] GPU test: sum([1,2,3]) = {result}")
            
            print()
            print("=" * 70)
            print("[OK] CuPy is working in QGIS!")
            print("=" * 70)
        else:
            print("[WARNING] CUDA is not available (but CuPy is installed)")
            
    except Exception as e:
        print(f"[ERROR] CUDA check failed: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"[FAILED] Cannot import CuPy: {e}")
    print()
    print("Diagnosis:")
    
    # Check if cupy directory exists
    try:
        import site
        user_site = site.getusersitepackages()
        cupy_dirs = []
        
        # Check common locations
        check_paths = [
            user_site,
            os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python312", "site-packages"),
            sys.prefix + "\\Lib\\site-packages",
        ]
        
        for base_path in check_paths:
            if os.path.exists(base_path):
                cupy_path = os.path.join(base_path, "cupy")
                if os.path.exists(cupy_path):
                    cupy_dirs.append(cupy_path)
        
        if cupy_dirs:
            print(f"Found CuPy at:")
            for cp_path in cupy_dirs:
                print(f"  - {cp_path}")
            print()
            print("But Python cannot find it. This may be a PATH issue.")
            print()
            print("Solution:")
            print("1. Restart QGIS completely")
            print("2. If still not working, try installing CuPy again:")
            print('   "C:\\Program Files\\QGIS 3.40.13\\bin\\python-qgis-ltr.bat" -m pip install --force-reinstall cupy-cuda12x')
        else:
            print("CuPy not found in any standard location.")
            print()
            print("Solution: Install CuPy")
            print('   "C:\\Program Files\\QGIS 3.40.13\\bin\\python-qgis-ltr.bat" -m pip install cupy-cuda12x')
            
    except Exception as diag_error:
        print(f"Diagnosis error: {diag_error}")

except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print()

