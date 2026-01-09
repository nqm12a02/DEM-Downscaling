"""Test CuPy import in QGIS Python environment"""
import sys
import os

print("=" * 70)
print("CuPy Import Test in QGIS Python Environment")
print("=" * 70)
print()
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print()

# Check sys.path
print("Python search paths:")
for i, path in enumerate(sys.path[:5], 1):  # Show first 5
    print(f"  {i}. {path}")
print("  ...")
print()

# Try to import CuPy
print("Attempting to import CuPy...")
try:
    import cupy as cp
    print("[OK] CuPy imported successfully!")
    print(f"    Version: {cp.__version__}")
    print(f"    Location: {cp.__file__}")
    print()
    
    # Check CUDA
    try:
        if cp.cuda.is_available():
            print("[OK] CUDA is available!")
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            major = cuda_version // 1000
            minor = (cuda_version % 1000) // 10
            print(f"    CUDA Runtime: {major}.{minor}")
            
            # Quick test
            test = cp.array([1, 2, 3])
            result = float(cp.asnumpy(cp.sum(test)))
            print(f"[OK] GPU test: sum([1,2,3]) = {result}")
            print()
            print("=" * 70)
            print("[SUCCESS] CuPy is working in QGIS Python!")
            print("=" * 70)
        else:
            print("[X] CUDA is not available")
    except Exception as e:
        print(f"[WARNING] CUDA check error: {e}")
        
except ImportError as e:
    print(f"[X] Failed to import CuPy: {e}")
    print()
    print("Checking if CuPy is in user site-packages...")
    user_site = None
    try:
        import site
        user_site = site.getusersitepackages()
        print(f"    User site-packages: {user_site}")
        if user_site and os.path.exists(os.path.join(user_site, 'cupy')):
            print(f"    [OK] CuPy found in user site-packages")
        else:
            print(f"    [X] CuPy NOT found in user site-packages")
    except:
        pass

print()

