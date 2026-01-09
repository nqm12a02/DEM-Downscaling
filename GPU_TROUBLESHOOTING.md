# GPU Troubleshooting Guide

## Problem: Plugin Running on CPU Instead of GPU

If you have a GPU but the plugin is running on CPU, follow these steps to diagnose and fix the issue.

## Step 1: Check GPU Detection

When you open the plugin dialog, check the status bar. It should show:
- ✅ **GPU available** - GPU is detected and ready
- ✅ **CPU vectorized** - GPU not available, using CPU
- ⚠️ **Slow mode** - No GPU or SciPy

If it shows CPU instead of GPU, continue to Step 2.

## Step 2: Test GPU in QGIS Python Console

1. Open QGIS
2. Go to **Plugins** → **Python Console**
3. Copy and paste this code:

```python
import sys
import os
plugin_dir = r"C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\DEM_Downscaling"
sys.path.insert(0, plugin_dir)
exec(open(os.path.join(plugin_dir, "test_gpu.py")).read())
```

Or simply:
```python
exec(open(r"C:\path\to\plugin\test_gpu.py").read())
```

4. Check the output. It will tell you:
   - If CuPy is installed
   - If CUDA is available
   - GPU device information
   - Any errors

## Step 3: Common Issues and Solutions

### Issue 1: "CuPy is NOT installed"

**Solution:**
```bash
python -m pip install cupy-cuda11x  # For CUDA 11.x
# OR
python -m pip install cupy-cuda12x  # For CUDA 12.x
```

**Important:** Use the Python executable from QGIS, not system Python!

To find QGIS Python:
```python
import sys
print(sys.executable)
```

### Issue 2: "CUDA is NOT available"

**Possible causes:**
1. **No NVIDIA GPU** - Check Device Manager (Windows) or `lspci | grep VGA` (Linux)
2. **CUDA drivers not installed** - Download from NVIDIA website
3. **CuPy version mismatch** - CuPy version must match CUDA version

**Check CUDA version:**
```bash
nvidia-smi
```

Look for "CUDA Version" in the output.

**Solution:**
- Install matching CuPy version:
  - CUDA 11.x → `cupy-cuda11x`
  - CUDA 12.x → `cupy-cuda12x`

### Issue 3: "GPU test: FAILED"

**Possible causes:**
1. GPU memory full
2. CUDA runtime error
3. Driver issues

**Solution:**
1. Close other GPU applications
2. Restart QGIS
3. Update GPU drivers
4. Check GPU with `nvidia-smi`

### Issue 4: GPU Detected but Still Using CPU

**Check progress messages:**
- Should show: "Calculating spatial dependence (GPU accelerated)..."
- If shows: "Calculating spatial dependence (vectorized CPU)..." → GPU not being used

**Possible causes:**
1. GPU detection failed silently
2. Error during GPU processing
3. Fallback to CPU due to error

**Solution:**
1. Check the status bar for GPU error messages
2. Look at progress messages during processing
3. Check QGIS log for errors

## Step 4: Verify GPU Usage

During processing, check the progress messages:

**GPU mode:**
- "Reading input DEM... (GPU: [name], Compute X.Y)"
- "Calculating spatial dependence (GPU accelerated)..."
- "Applying elevation constraints (GPU accelerated)..."

**CPU mode:**
- "Reading input DEM... (CPU vectorized)"
- "Calculating spatial dependence (vectorized CPU)..."
- "Applying elevation constraints (vectorized CPU)..."

## Step 5: Manual GPU Test

Test GPU directly in QGIS Python Console:

```python
try:
    import cupy as cp
    print("CuPy version:", cp.__version__)
    print("CUDA available:", cp.cuda.is_available())
    
    if cp.cuda.is_available():
        device = cp.cuda.Device(0)
        device.use()
        print("Device:", device.id)
        print("Compute capability:", device.compute_capability)
        
        # Test array operation
        a = cp.array([1.0, 2.0, 3.0])
        b = cp.array([4.0, 5.0, 6.0])
        c = a + b
        result = cp.asnumpy(c)
        print("GPU test SUCCESS:", result)
    else:
        print("CUDA not available")
except Exception as e:
    print("Error:", str(e))
```

## Step 6: Check Plugin Logs

1. In QGIS, go to **View** → **Panels** → **Log Messages**
2. Look for messages from "DEM Downscaling"
3. Check for GPU-related errors

## Common Error Messages

### "GPU initialization failed: [error]"
- **Cause:** GPU device access failed
- **Solution:** Check GPU drivers, restart QGIS

### "CuPy is not installed"
- **Cause:** CuPy not installed in QGIS Python
- **Solution:** Install CuPy with correct CUDA version

### "CUDA is not available"
- **Cause:** No CUDA-capable GPU or drivers not installed
- **Solution:** Install NVIDIA drivers and CUDA toolkit

## Still Not Working?

1. **Verify GPU in system:**
   - Windows: Device Manager → Display adapters
   - Linux: `lspci | grep -i nvidia`
   - Check `nvidia-smi` output

2. **Check QGIS Python environment:**
   ```python
   import sys
   print(sys.executable)
   print(sys.path)
   ```

3. **Reinstall CuPy:**
   ```bash
   python -m pip uninstall cupy
   python -m pip install cupy-cuda11x  # or cupy-cuda12x
   ```

4. **Restart QGIS** after installing CuPy

5. **Check plugin status bar** - it should show GPU information if detected

## Performance Comparison

If GPU is working, you should see:
- **Much faster processing** (8x speedup for large DEMs)
- Progress messages showing "GPU accelerated"
- Status bar showing "GPU available"

If still slow, GPU is likely not being used.

## Contact

If issues persist, check:
1. GPU model and CUDA compatibility
2. CuPy installation matches CUDA version
3. QGIS Python environment is correct
4. No conflicts with other GPU applications



