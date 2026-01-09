"""Check and fix CuPy installation for QGIS"""
import sys
import os
import subprocess

print("=" * 70)
print("CuPy Installation Check and Fix for QGIS")
print("=" * 70)
print()

# Get QGIS Python executable
python_exe = sys.executable
print(f"Using Python: {python_exe}")
print()

# Check user site-packages
try:
    import site
    user_site = site.getusersitepackages()
    print(f"User site-packages: {user_site}")
    
    if user_site not in sys.path:
        print("[WARNING] User site-packages NOT in sys.path")
        print("Adding user site-packages to sys.path...")
        sys.path.insert(0, user_site)
        # Also check if .pth file exists
        pth_file = os.path.join(user_site, 'qgis.pth')
        if not os.path.exists(pth_file):
            print("Creating .pth file to ensure QGIS loads user packages...")
            try:
                with open(pth_file, 'w') as f:
                    f.write(user_site + '\n')
                print("[OK] Created .pth file")
            except Exception as e:
                print(f"[X] Failed to create .pth file: {e}")
    else:
        print("[OK] User site-packages in sys.path")
except Exception as e:
    print(f"[X] Error checking site-packages: {e}")

print()

# Check if CuPy exists
cupy_path = None
if user_site:
    cupy_path = os.path.join(user_site, 'cupy')
    if os.path.exists(cupy_path):
        print(f"[OK] CuPy found at: {cupy_path}")
    else:
        print(f"[X] CuPy NOT found at: {cupy_path}")

print()

# Try to import after adding to path
print("Attempting to import CuPy after fixing path...")
try:
    import cupy as cp
    print("[OK] CuPy imported successfully!")
    print(f"    Version: {cp.__version__}")
    
    if cp.cuda.is_available():
        print("[OK] CUDA available!")
        test = cp.array([1, 2, 3])
        result = float(cp.asnumpy(cp.sum(test)))
        print(f"[OK] GPU test: sum([1,2,3]) = {result}")
        print()
        print("=" * 70)
        print("[SUCCESS] CuPy is working!")
        print("=" * 70)
    else:
        print("[X] CUDA not available")
        
except ImportError:
    print("[X] CuPy still cannot be imported")
    print()
    print("Installing CuPy...")
    try:
        result = subprocess.run(
            [python_exe, '-m', 'pip', 'install', 'cupy-cuda12x'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("[OK] CuPy installation completed")
            print("Please restart QGIS and test again")
        else:
            print(f"[X] Installation failed: {result.stderr}")
    except Exception as e:
        print(f"[X] Installation error: {e}")

print()

