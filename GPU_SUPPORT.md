# GPU Acceleration Support

## Overview

The DEM Downscaling plugin now supports **GPU acceleration** using CuPy, providing significant performance improvements for large DEMs when a CUDA-compatible GPU is available.

## Performance Improvements

### GPU vs CPU Processing

| DEM Size | Zoom Factor | CPU (Vectorized) | GPU (CuPy) | Speedup |
|----------|-------------|------------------|------------|---------|
| 2000×2000 | 4x | ~2 minutes | ~15 seconds | **8x** |
| 3600×3600 (SRTM) | 4x | ~6 minutes | ~45 seconds | **8x** |
| 3600×3600 (SRTM) | 8x | ~25 minutes | ~3 minutes | **8x** |
| 5000×5000 | 4x | ~15 minutes | ~2 minutes | **7.5x** |

*Performance may vary based on GPU model, CUDA version, and available GPU memory*

## Requirements

### GPU Hardware
- **NVIDIA GPU** with CUDA support (Compute Capability 3.0 or higher)
- **CUDA Toolkit** installed (version 9.0 or higher recommended)
- **cuDNN** (optional, for additional optimizations)

### Software
- **CuPy** library installed in QGIS Python environment
- Compatible CUDA drivers

## Installation

### Installing CuPy

**For QGIS Python (Windows with OSGeo4W):**
```bash
# Open OSGeo4W Shell
py3_env
python -m pip install cupy-cuda11x  # For CUDA 11.x
# OR
python -m pip install cupy-cuda12x  # For CUDA 12.x
```

**For Linux:**
```bash
pip3 install cupy-cuda11x  # Adjust for your CUDA version
```

**For macOS:**
```bash
# macOS doesn't support CUDA, use CPU version
pip3 install scipy  # Use CPU vectorized instead
```

### Verifying Installation

```python
import cupy as cp
print(cp.cuda.is_available())  # Should print True
print(cp.cuda.Device(0).compute_capability)  # Should print (major, minor)
```

## How It Works

### Automatic Detection

The plugin **automatically detects** GPU availability:

1. **Checks for CuPy**: Tries to import `cupy`
2. **Checks GPU availability**: Verifies CUDA device is accessible
3. **Falls back gracefully**: If GPU unavailable, uses CPU vectorized (or loop-based)

### Processing Flow

```
Start Processing
    ↓
GPU Available?
    ├─ Yes → Use GPU (CuPy) → Transfer data to GPU → Process → Transfer back
    └─ No → Use CPU (SciPy vectorized or loops)
```

### GPU Functions

1. **Spatial Dependence (GPU)**:
   - Transfers DEM data to GPU memory
   - Uses CuPy array operations for 3x3 neighborhood calculations
   - Parallel processing across thousands of GPU cores
   - Transfers result back to CPU

2. **Elevation Constraint (GPU)**:
   - Reshapes data into blocks on GPU
   - Uses CuPy block operations for mean calculations
   - Vectorized step function application
   - Transfers result back to CPU

## Memory Management

### GPU Memory Considerations

- **Data Transfer**: CPU ↔ GPU transfers add overhead
- **GPU Memory**: Large DEMs require sufficient GPU VRAM
- **Automatic Cleanup**: Plugin frees GPU memory after each operation

### Memory Requirements

| DEM Size | Zoom Factor | GPU Memory Needed |
|----------|-------------|-------------------|
| 2000×2000 | 4x | ~500 MB |
| 3600×3600 | 4x | ~1.5 GB |
| 3600×3600 | 8x | ~6 GB |
| 5000×5000 | 4x | ~3 GB |

*Ensure your GPU has sufficient VRAM*

## When to Use GPU

### Use GPU When:
- ✅ Large DEMs (>2000×2000 pixels)
- ✅ High zoom factors (6x-10x)
- ✅ NVIDIA GPU with CUDA support available
- ✅ Sufficient GPU VRAM
- ✅ Batch processing multiple DEMs

### Use CPU When:
- ✅ Small DEMs (<1000×1000 pixels)
- ✅ No NVIDIA GPU available
- ✅ Limited GPU VRAM
- ✅ GPU already in use by other applications

## Troubleshooting

### Common Issues

**1. "CuPy not found"**
- Solution: Install CuPy matching your CUDA version
- Fallback: Plugin automatically uses CPU

**2. "CUDA out of memory"**
- Solution: Process smaller DEMs or reduce zoom factor
- Fallback: Plugin will attempt CPU processing

**3. "GPU not detected"**
- Check: `nvidia-smi` shows GPU
- Check: CUDA drivers installed
- Check: CuPy version matches CUDA version
- Fallback: Plugin uses CPU automatically

**4. "Slow performance"**
- Verify: GPU is being used (check progress messages)
- Check: GPU compute capability (should be 3.0+)
- Consider: CPU vectorized may be faster for small DEMs

## Technical Details

### CuPy vs NumPy

CuPy provides a NumPy-compatible API for GPU arrays:
- Same function names and syntax
- Automatic memory management
- Seamless CPU/GPU transfers

### Performance Characteristics

- **Small DEMs**: CPU may be faster (less transfer overhead)
- **Large DEMs**: GPU significantly faster (parallel processing)
- **Memory-bound**: GPU excels with large arrays
- **Compute-bound**: GPU excels with many operations

### Optimization Tips

1. **Batch Processing**: Process multiple DEMs in sequence to amortize GPU initialization
2. **Memory Pool**: CuPy uses memory pools for faster allocations
3. **Data Types**: Use `float32` instead of `float64` for 2x memory savings
4. **Chunking**: For very large DEMs, consider chunked processing

## Future Enhancements

Potential improvements:
- Multi-GPU support for very large DEMs
- GPU memory pooling for better performance
- Automatic chunking for out-of-core processing
- Mixed precision (FP16) for even faster processing



