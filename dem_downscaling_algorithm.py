"""
DEM Downscaling Algorithm

This module implements the DEM downscaling algorithm based on:
"Downscaling Gridded DEMs Using the Hopfield Neural Network"
by Nguyen Quang Minh et al.
IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing
Volume 12, Issue 11, pp. 4426-4437, 2019
DOI: 10.1109/IGARSS.2019.8932562

The algorithm uses spatial dependence maximization and elevation constraints
to increase DEM resolution.
"""
import numpy as np
from osgeo import gdal
import os

try:
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# GPU support with CuPy
GPU_AVAILABLE = False
GPU_DEVICE = None
cp = None
GPU_ERROR_MSG = None
CUDA_TOOLKIT_INSTALLED = False
CUDA_TOOLKIT_PATH = None

def _check_cuda_toolkit():
    """Check if CUDA Toolkit is installed by looking for nvcc or CUDA paths"""
    import os
    import platform
    
    # Common CUDA installation paths
    cuda_paths = []
    
    if platform.system() == 'Windows':
        # Check Program Files
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        cuda_base_paths = [
            os.path.join(program_files, 'NVIDIA GPU Computing Toolkit', 'CUDA'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'NVIDIA GPU Computing Toolkit', 'CUDA'),
        ]
        
        for cuda_base in cuda_base_paths:
            if os.path.exists(cuda_base):
                cuda_paths.append(cuda_base)
        
        # Check PATH environment variable
        path_env = os.environ.get('PATH', '')
        for path in path_env.split(os.pathsep):
            if 'CUDA' in path.upper() and 'bin' in path:
                cuda_base = os.path.dirname(path)
                if cuda_base not in cuda_paths and os.path.exists(cuda_base):
                    cuda_paths.append(cuda_base)
    
    # Check if any CUDA path exists and contains nvcc.exe or bin directory
    for cuda_base in cuda_paths:
        if os.path.exists(cuda_base):
            # Check for version subdirectories
            try:
                for item in os.listdir(cuda_base):
                    version_path = os.path.join(cuda_base, item)
                    if os.path.isdir(version_path):
                        bin_path = os.path.join(version_path, 'bin')
                        if os.path.exists(bin_path):
                            nvcc_path = os.path.join(bin_path, 'nvcc.exe' if platform.system() == 'Windows' else 'nvcc')
                            if os.path.exists(nvcc_path):
                                # Try to add to PATH dynamically for this session
                                _add_cuda_to_path_dynamic(bin_path)
                                return True, version_path
            except:
                continue
    
    # Also check if nvcc is in PATH
    try:
        import subprocess
        result = subprocess.run(['nvcc', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=2)
        if result.returncode == 0:
            # Try to extract path from output or find it
            return True, "Found in PATH"
    except:
        pass
    
    return False, None

def _add_cuda_to_path_dynamic(cuda_bin_path):
    """Dynamically add CUDA bin path to current process PATH (temporary)"""
    import os
    current_path = os.environ.get('PATH', '')
    if cuda_bin_path not in current_path:
        os.environ['PATH'] = cuda_bin_path + os.pathsep + current_path

# Check CUDA Toolkit installation
CUDA_TOOLKIT_INSTALLED, CUDA_TOOLKIT_PATH = _check_cuda_toolkit()

try:
    import cupy as cp
    # Check if GPU is available
    try:
        # Check if CUDA is available
        if cp.cuda.is_available():
            # Try to get device 0
            device = cp.cuda.Device(0)
            device.use()
            # Test with a small array to ensure GPU actually works
            test_array = cp.array([1.0, 2.0, 3.0])
            _ = cp.asnumpy(test_array)  # Transfer back to ensure it works
            GPU_AVAILABLE = True
            GPU_DEVICE = device
            GPU_ERROR_MSG = None
        else:
            GPU_AVAILABLE = False
            # Try to get more information about why CUDA is not available
            try:
                device_count = cp.cuda.runtime.getDeviceCount()
                if device_count == 0:
                    GPU_ERROR_MSG = "CUDA is not available: No GPU devices found"
                else:
                    GPU_ERROR_MSG = f"CUDA is not available: {device_count} device(s) found but not accessible"
            except:
                GPU_ERROR_MSG = "CUDA is not available: Check CUDA drivers and CuPy installation"
    except Exception as e:
        GPU_AVAILABLE = False
        error_str = str(e)
        if "nvrtc" in error_str.lower() or ("dll" in error_str.lower() and "cuda" in error_str.lower()):
            if not CUDA_TOOLKIT_INSTALLED:
                GPU_ERROR_MSG = f"CUDA Toolkit not installed: {error_str}. Please install CUDA Toolkit from NVIDIA (see CUDA_TOOLKIT_INSTALL.md)"
            else:
                GPU_ERROR_MSG = f"CUDA DLL error: {error_str}. CUDA Toolkit may not be properly configured in PATH."
        elif "out of memory" in error_str.lower():
            GPU_ERROR_MSG = f"GPU memory error: {error_str}"
        elif "device" in error_str.lower():
            GPU_ERROR_MSG = f"GPU device error: {error_str}"
        else:
            GPU_ERROR_MSG = f"GPU initialization failed: {error_str}"
except ImportError:
    GPU_AVAILABLE = False
    GPU_ERROR_MSG = "CuPy is not installed"
    cp = None
except Exception as e:
    GPU_AVAILABLE = False
    error_str = str(e)
    if "nvrtc" in error_str.lower() or ("dll" in error_str.lower() and "cuda" in error_str.lower()):
        if not CUDA_TOOLKIT_INSTALLED:
            GPU_ERROR_MSG = f"CUDA Toolkit not installed: {error_str}. Please install CUDA Toolkit from NVIDIA (see CUDA_TOOLKIT_INSTALL.md)"
        else:
            GPU_ERROR_MSG = f"CUDA DLL error: {error_str}. CUDA Toolkit found but DLLs not accessible."
    else:
        GPU_ERROR_MSG = f"GPU check failed: {str(e)}"
    cp = None


def estimate_memory_usage(width, height, zoom_factor):
    """
    Estimate memory usage for DEM processing
    
    Parameters:
    -----------
    width : int
        Width of input DEM in pixels
    height : int
        Height of input DEM in pixels
    zoom_factor : int
        Zoom factor for downscaling
    
    Returns:
    --------
    dict : Memory estimates in MB
    """
    # Input DEM (float32 = 4 bytes per pixel)
    input_mem = (width * height * 4) / (1024 * 1024)
    
    # Downscaled DEM (zoom_factor^2 larger)
    output_width = width * zoom_factor
    output_height = height * zoom_factor
    output_mem = (output_width * output_height * 4) / (1024 * 1024)
    
    # Temporary arrays during processing (usd, uec, u)
    temp_mem = output_mem * 3
    
    # Total estimated memory
    total_mem = input_mem + output_mem + temp_mem
    
    return {
        'input_mb': input_mem,
        'output_mb': output_mem,
        'temp_mb': temp_mem,
        'total_mb': total_mem,
        'output_size': (output_width, output_height)
    }


def estimate_runtime(width, height, zoom_factor, use_gpu=None, use_vectorized=None):
    """
    Estimate processing runtime for DEM downscaling
    
    Parameters:
    -----------
    width : int
        Width of input DEM in pixels
    height : int
        Height of input DEM in pixels
    zoom_factor : int
        Zoom factor (resolution increase)
    use_gpu : bool or None
        Whether GPU will be used (auto-detect if None)
    use_vectorized : bool or None
        Whether vectorized CPU will be used (auto-detect if None)
    
    Returns:
    --------
    dict : Dictionary with runtime estimates in seconds and formatted string
    """
    # Auto-detect if not specified
    if use_gpu is None:
        use_gpu = GPU_AVAILABLE
    if use_vectorized is None:
        use_vectorized = SCIPY_AVAILABLE
    
    # Calculate total pixels in output
    output_pixels = (width * zoom_factor) * (height * zoom_factor)
    input_pixels = width * height
    
    # Base processing time per million pixels (in seconds)
    # These are rough estimates based on typical performance
    if use_gpu:
        # GPU processing: ~0.1 seconds per million output pixels per iteration
        base_time_per_mpix = 0.1
        iterations_estimate = 50  # Typical iterations
    elif use_vectorized:
        # CPU vectorized: ~2 seconds per million output pixels per iteration
        base_time_per_mpix = 2.0
        iterations_estimate = 50
    else:
        # CPU loop-based: ~30 seconds per million output pixels per iteration
        base_time_per_mpix = 30.0
        iterations_estimate = 50
    
    # Estimate time per iteration
    output_mpix = output_pixels / 1_000_000
    time_per_iteration = base_time_per_mpix * output_mpix
    
    # Additional overhead
    overhead = 5.0  # Reading, writing, initialization
    
    # Total estimated time
    total_seconds = (time_per_iteration * iterations_estimate) + overhead
    
    # Format time string
    if total_seconds < 60:
        time_str = f"~{int(total_seconds)} seconds"
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        time_str = f"~{minutes} min {seconds} sec"
    else:
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        time_str = f"~{hours} hr {minutes} min"
    
    return {
        'total_seconds': total_seconds,
        'time_per_iteration': time_per_iteration,
        'iterations_estimate': iterations_estimate,
        'formatted_time': time_str,
        'processing_mode': 'GPU' if use_gpu else ('CPU vectorized' if use_vectorized else 'CPU loop-based')
    }


def open_raster(fn, access=gdal.GA_ReadOnly):
    """Open raster file and return dataset"""
    ds = gdal.Open(fn, access)
    if ds is None:
        raise Exception(f"Error opening raster dataset: {fn}")
    return ds


def get_raster_band(fn, band=1, access=gdal.GA_ReadOnly):
    """Read a band from raster file and return numpy array along with nodata value"""
    ds = open_raster(fn, access)
    raster_band = ds.GetRasterBand(1)
    band_array = raster_band.ReadAsArray()
    nodata_value = raster_band.GetNoDataValue()
    ds = None
    return band_array, nodata_value


def get_raster_info(fn):
    """Get raster information including nodata value"""
    ds = open_raster(fn)
    raster_band = ds.GetRasterBand(1)
    info = {
        'width': ds.RasterXSize,
        'height': ds.RasterYSize,
        'bands': ds.RasterCount,
        'data_type': raster_band.DataType,
        'nodata_value': raster_band.GetNoDataValue(),
        'file_size_mb': os.path.getsize(fn) / (1024 * 1024)
    }
    ds = None
    return info


def get_geo_transform(fn, access=gdal.GA_ReadOnly):
    """Lấy thông tin GeoTransform của raster"""
    ds = open_raster(fn, access)
    geot = ds.GetGeoTransform()
    ds = None
    return geot


def get_projection(fn, access=gdal.GA_ReadOnly):
    """Lấy thông tin projection của raster"""
    ds = open_raster(fn, access)
    proj = ds.GetProjection()
    ds = None
    return proj


def initialize(data, zoom, nodata_mask=None, progress_callback=None):
    """
    Initialize downscaling data
    Initial elevation values of sub-pixels equal the elevation value of the original pixel
    Nodata pixels are preserved
    """
    if progress_callback:
        progress_callback("Initializing downscaled DEM...", 5)
    band = np.repeat(data, zoom, axis=0)
    band = np.repeat(band, zoom, axis=1)
    
    # If nodata mask is provided, expand it to match the downscaled size
    if nodata_mask is not None:
        expanded_mask = np.repeat(nodata_mask, zoom, axis=0)
        expanded_mask = np.repeat(expanded_mask, zoom, axis=1)
        return band, expanded_mask
    
    return band, None


def spatial_dependence(dtin, nodata_mask=None, progress_callback=None, use_vectorized=True, use_gpu=None):
    """
    Calculate spatial dependence maximization function value
    With progress callback to update progress
    Handles nodata values by excluding them from calculations
    
    Parameters:
    -----------
    use_vectorized : bool
        If True and scipy is available, use vectorized convolution (much faster)
        If False or scipy unavailable, use pixel-by-pixel loop
    use_gpu : bool or None
        If True, try to use GPU (requires CuPy and CUDA GPU)
        If False, use CPU only
        If None, auto-detect (use GPU if available)
    """
    # Auto-detect GPU if not specified
    if use_gpu is None:
        use_gpu = GPU_AVAILABLE
    
    # Use GPU version if requested and available
    if use_gpu and GPU_AVAILABLE and use_vectorized:
        try:
            return spatial_dependence_gpu(dtin, nodata_mask, progress_callback)
        except Exception as e:
            # GPU failed, fallback to CPU
            error_msg = str(e)
            if "nvrtc" in error_msg.lower() or "dll" in error_msg.lower() or "cuda" in error_msg.lower():
                if progress_callback:
                    progress_callback(
                        f"GPU error detected (CUDA DLL missing): {error_msg}. "
                        f"Falling back to CPU processing...", 
                        30
                    )
            else:
                if progress_callback:
                    progress_callback(
                        f"GPU error: {error_msg}. Falling back to CPU processing...", 
                        30
                    )
            # Continue with CPU processing
    
    # Use vectorized version if available and requested
    if use_vectorized and SCIPY_AVAILABLE:
        return spatial_dependence_vectorized(dtin, nodata_mask, progress_callback)
    
    # Fall back to loop-based version
    width = dtin.shape[0]
    height = dtin.shape[1]
    usd = np.zeros((width, height))
    total_pixels = width * height
    processed = 0

    for i in range(0, width):
        for j in range(0, height):
            # Skip nodata pixels
            if nodata_mask is not None and nodata_mask[i, j]:
                usd[i][j] = 0.0
                processed += 1
                continue
            
            # Set window (3x3 neighborhood)
            count = 0
            sum_val = 0.0
            
            if i == 0:
                swr = 0
            else:
                swr = i - 1
                
            if i == width - 1:
                ewr = i + 1
            else:
                ewr = i + 2
                
            if j == 0:
                swc = 0
            else:
                swc = j - 1
                
            if j == height - 1:
                ewc = j + 1
            else:
                ewc = j + 2
                
            # Only count valid (non-nodata) pixels in the neighborhood
            for l in range(swr, ewr):
                for m in range(swc, ewc):
                    # Skip nodata pixels in neighborhood
                    if nodata_mask is not None and nodata_mask[l, m]:
                        continue
                    count += 1
                    sum_val += dtin[l][m]
                    
            v_current = dtin[i][j]
            if count > 1:
                vexp = (sum_val - v_current) / (count - 1)
                usd[i][j] = vexp - v_current
            else:
                # Not enough valid neighbors, set to 0
                usd[i][j] = 0.0
            
            processed += 1
            # Update progress every 10000 pixels or at the end
            if progress_callback and (processed % 10000 == 0 or processed == total_pixels):
                progress = 30 + int((processed / total_pixels) * 25)  # 30-55% range
                progress_callback(f"Calculating spatial dependence... {processed}/{total_pixels} pixels", progress)

    return usd


def spatial_dependence_vectorized(dtin, nodata_mask=None, progress_callback=None):
    """
    Vectorized version using scipy.ndimage convolution (much faster)
    Uses tensor operations for parallel processing on CPU
    """
    if progress_callback:
        progress_callback("Calculating spatial dependence (vectorized CPU)...", 30)
    
    width, height = dtin.shape
    
    # Create mask for valid pixels
    if nodata_mask is not None:
        valid_mask = ~nodata_mask.astype(bool)
    else:
        valid_mask = np.ones((width, height), dtype=bool)
    
    # Create masked array (set nodata to 0 for convolution)
    dtin_masked = np.where(valid_mask, dtin, 0.0)
    
    # 3x3 kernel excluding center pixel
    kernel = np.ones((3, 3), dtype=np.float64)
    kernel[1, 1] = 0  # Exclude center pixel
    
    # Count valid neighbors for each pixel using convolution
    neighbor_valid_count = ndimage.convolve(
        valid_mask.astype(np.float64), 
        kernel, 
        mode='constant', 
        cval=0.0
    )
    
    # Sum of valid neighbors using convolution
    neighbor_sum = ndimage.convolve(
        dtin_masked, 
        kernel, 
        mode='constant', 
        cval=0.0
    )
    
    # Calculate expected value (mean of neighbors)
    # Only where we have at least 2 valid neighbors
    has_enough_neighbors = neighbor_valid_count >= 2
    neighbor_count_safe = np.where(neighbor_valid_count > 0, neighbor_valid_count, 1)
    vexp = np.where(has_enough_neighbors, neighbor_sum / neighbor_count_safe, dtin)
    
    # Spatial dependence: expected - current
    usd = vexp - dtin
    
    # Zero out nodata and insufficient neighbors
    usd[~valid_mask] = 0.0
    usd[~has_enough_neighbors] = 0.0
    
    if progress_callback:
        progress_callback("Spatial dependence calculated (vectorized CPU)", 55)
    
    return usd


def spatial_dependence_gpu(dtin, nodata_mask=None, progress_callback=None):
    """
    GPU-accelerated version using CuPy (much faster for large DEMs)
    Uses CUDA tensor operations for parallel processing on GPU
    """
    if progress_callback:
        progress_callback("Calculating spatial dependence (GPU accelerated)...", 30)
    
    # Transfer data to GPU
    dtin_gpu = cp.asarray(dtin, dtype=cp.float32)
    
    width, height = dtin.shape
    
    # Create mask for valid pixels on GPU
    if nodata_mask is not None:
        valid_mask_gpu = cp.asarray(~nodata_mask.astype(bool))
    else:
        valid_mask_gpu = cp.ones((width, height), dtype=cp.bool_)
    
    # Create masked array (set nodata to 0 for convolution)
    dtin_masked_gpu = cp.where(valid_mask_gpu, dtin_gpu, 0.0)
    
    # 3x3 kernel excluding center pixel
    kernel_gpu = cp.ones((3, 3), dtype=cp.float32)
    kernel_gpu[1, 1] = 0  # Exclude center pixel
    
    # Use CuPy's convolution (faster than scipy on GPU)
    # Count valid neighbors
    neighbor_valid_count_gpu = cp.zeros_like(dtin_gpu, dtype=cp.float32)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue  # Skip center
            # Shift and accumulate
            shifted = cp.roll(cp.roll(valid_mask_gpu.astype(cp.float32), i, axis=0), j, axis=1)
            neighbor_valid_count_gpu += shifted
    
    # Sum of valid neighbors using manual convolution (CuPy doesn't have ndimage)
    neighbor_sum_gpu = cp.zeros_like(dtin_gpu, dtype=cp.float32)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue  # Skip center
            shifted = cp.roll(cp.roll(dtin_masked_gpu, i, axis=0), j, axis=1)
            neighbor_sum_gpu += shifted
    
    # Calculate expected value (mean of neighbors)
    has_enough_neighbors_gpu = neighbor_valid_count_gpu >= 2
    neighbor_count_safe_gpu = cp.where(neighbor_valid_count_gpu > 0, neighbor_valid_count_gpu, 1)
    vexp_gpu = cp.where(has_enough_neighbors_gpu, neighbor_sum_gpu / neighbor_count_safe_gpu, dtin_gpu)
    
    # Spatial dependence: expected - current
    usd_gpu = vexp_gpu - dtin_gpu
    
    # Zero out nodata and insufficient neighbors
    usd_gpu = cp.where(valid_mask_gpu, usd_gpu, 0.0)
    usd_gpu = cp.where(has_enough_neighbors_gpu, usd_gpu, 0.0)
    
    # Transfer result back to CPU
    usd = cp.asnumpy(usd_gpu)
    
    # Free GPU memory
    del dtin_gpu, valid_mask_gpu, dtin_masked_gpu, kernel_gpu
    del neighbor_valid_count_gpu, neighbor_sum_gpu, vexp_gpu, usd_gpu
    cp.get_default_memory_pool().free_all_blocks()
    
    if progress_callback:
        progress_callback("Spatial dependence calculated (GPU)", 55)
    
    return usd


def elevation_constraint(dtin, goc, rsme, nodata_mask_orig=None, nodata_mask_down=None, progress_callback=None, use_vectorized=True, use_gpu=None):
    """
    Elevation constraint function
    With progress callback to update progress
    Handles nodata values by preserving them in output
    
    Parameters:
    -----------
    use_vectorized : bool
        If True, use vectorized block operations (much faster)
        If False, use pixel-by-pixel loop
    use_gpu : bool or None
        If True, try to use GPU (requires CuPy and CUDA GPU)
        If False, use CPU only
        If None, auto-detect (use GPU if available)
    """
    # Auto-detect GPU if not specified
    if use_gpu is None:
        use_gpu = GPU_AVAILABLE
    
    # Use GPU version if requested and available
    if use_gpu and GPU_AVAILABLE and use_vectorized:
        try:
            return elevation_constraint_gpu(dtin, goc, rsme, nodata_mask_orig, nodata_mask_down, progress_callback)
        except Exception as e:
            # GPU failed, fallback to CPU
            error_msg = str(e)
            if "nvrtc" in error_msg.lower() or ("dll" in error_msg.lower() and "cuda" in error_msg.lower()):
                # CUDA Toolkit DLL missing
                if not CUDA_TOOLKIT_INSTALLED:
                    fallback_msg = (
                        f"⚠️ GPU Error: CUDA Toolkit not installed!\n"
                        f"Error: {error_msg}\n\n"
                        f"Solution: Install CUDA Toolkit from NVIDIA:\n"
                        f"https://developer.nvidia.com/cuda-downloads\n\n"
                        f"Falling back to CPU processing..."
                    )
                else:
                    fallback_msg = (
                        f"⚠️ GPU Error: CUDA DLL not accessible!\n"
                        f"Error: {error_msg}\n\n"
                        f"CUDA Toolkit found at: {CUDA_TOOLKIT_PATH}\n"
                        f"Check PATH environment variable.\n\n"
                        f"Falling back to CPU processing..."
                    )
                if progress_callback:
                    progress_callback(fallback_msg, 50)
            else:
                if progress_callback:
                    progress_callback(
                        f"⚠️ GPU Error: {error_msg}\nFalling back to CPU processing...", 
                        50
                    )
            # Continue with CPU processing
    
    # Use vectorized version if possible
    if use_vectorized:
        return elevation_constraint_vectorized(dtin, goc, rsme, nodata_mask_orig, nodata_mask_down, progress_callback)
    
    # Fall back to loop-based version
    width = dtin.shape[0]
    height = dtin.shape[1]
    goc_w = goc.shape[0]
    goc_h = goc.shape[1]
    zoom = int(width / goc_w)
    uec = np.zeros((width, height))
    total_pixels = goc_w * goc_h
    processed = 0
    
    for i in range(0, goc_w):
        for j in range(0, goc_h):
            # Skip if original pixel is nodata
            if nodata_mask_orig is not None and nodata_mask_orig[i, j]:
                # All sub-pixels for this original pixel should be nodata
                swr = i * zoom
                ewr = swr + zoom
                swc = j * zoom
                ewc = swc + zoom
                for l in range(swr, ewr):
                    for m in range(swc, ewc):
                        uec[l][m] = 0.0  # No correction for nodata areas
                processed += 1
                continue
            
            # Determine the average elevation
            # Determine the range of a pixel in the original DEM
            sum_val = 0.0
            valid_count = 0
            swr = i * zoom
            ewr = swr + zoom
            swc = j * zoom
            ewc = swc + zoom
            
            # Calculate sum of valid elevation points of sub-pixels in one pixel
            for l in range(swr, ewr):
                for m in range(swc, ewc):
                    # Skip nodata pixels
                    if nodata_mask_down is not None and nodata_mask_down[l, m]:
                        continue
                    sum_val += dtin[l][m]
                    valid_count += 1
                    
            # Original elevation to calculate du_elevation of an original pixel
            elev = goc[i][j]
            
            # Calculate average elevation only from valid pixels
            if valid_count > 0:
                velc = sum_val / valid_count
            else:
                # All sub-pixels are nodata, skip correction
                processed += 1
                continue
            
            # Calculate elevation correction value for each sub-pixel
            for l in range(swr, ewr):
                for m in range(swc, ewc):
                    # Skip nodata pixels
                    if nodata_mask_down is not None and nodata_mask_down[l, m]:
                        uec[l][m] = 0.0
                        continue
                    
                    uec[l][m] = elev - velc
                    step = abs(uec[l][m]) / rsme if rsme > 0 else 0
                    if step < 3:
                        uec[l][m] = 0.8 * uec[l][m]
                        # 0.8 is the coefficient of the elevation constraint function
            
            processed += 1
            # Update progress every 1000 pixels or at the end
            if progress_callback and (processed % 1000 == 0 or processed == total_pixels):
                progress = 55 + int((processed / total_pixels) * 15)  # 55-70% range
                progress_callback(f"Applying elevation constraints... {processed}/{total_pixels} pixels", progress)

    return uec


def elevation_constraint_vectorized(dtin, goc, rsme, nodata_mask_orig=None, nodata_mask_down=None, progress_callback=None):
    """
    Vectorized version using NumPy block operations (much faster)
    Uses tensor/array operations for parallel processing on CPU
    """
    if progress_callback:
        progress_callback("Applying elevation constraints (vectorized CPU)...", 55)
    
    width, height = dtin.shape
    goc_w, goc_h = goc.shape
    zoom = int(width / goc_w)
    
    # Reshape downscaled DEM into blocks using NumPy array operations
    # Each block corresponds to one original pixel
    # Shape: (goc_w, zoom, goc_h, zoom)
    dtin_blocks = dtin.reshape(goc_w, zoom, goc_h, zoom)
    
    # Create mask for valid pixels in blocks
    if nodata_mask_down is not None:
        nodata_blocks = nodata_mask_down.reshape(goc_w, zoom, goc_h, zoom)
        # Count valid pixels per block
        valid_count_per_block = np.sum(~nodata_blocks, axis=(1, 3))  # Sum over zoom dimensions
        # Mask the blocks
        dtin_blocks_masked = np.where(nodata_blocks, 0.0, dtin_blocks)
    else:
        valid_count_per_block = np.full((goc_w, goc_h), zoom * zoom)
        dtin_blocks_masked = dtin_blocks
    
    # Calculate mean of each block (average elevation of sub-pixels) using vectorized operations
    # Sum over zoom dimensions (axis 1 and 3)
    block_sums = np.sum(dtin_blocks_masked, axis=(1, 3))  # Shape: (goc_w, goc_h)
    
    # Calculate mean only for blocks with valid pixels
    valid_count_safe = np.where(valid_count_per_block > 0, valid_count_per_block, 1)
    block_means = block_sums / valid_count_safe  # Shape: (goc_w, goc_h)
    
    # Handle nodata in original: set means to original value (will result in 0 correction)
    if nodata_mask_orig is not None:
        block_means = np.where(nodata_mask_orig, goc, block_means)
    
    # Calculate elevation constraint: original - mean
    elevation_diff = goc - block_means  # Shape: (goc_w, goc_h)
    
    # Expand elevation_diff to match downscaled size using vectorized repeat
    # Each original pixel value is repeated for all its sub-pixels
    elevation_diff_expanded = np.repeat(elevation_diff, zoom, axis=0)
    elevation_diff_expanded = np.repeat(elevation_diff_expanded, zoom, axis=1)
    
    # Apply step function with RSME parameter using vectorized operations
    step = np.abs(elevation_diff_expanded) / rsme if rsme > 0 else np.abs(elevation_diff_expanded)
    uec = np.where(step < 3, 0.8 * elevation_diff_expanded, elevation_diff_expanded)
    
    # Handle nodata: set to 0 for nodata areas
    if nodata_mask_orig is not None:
        # Expand original nodata mask
        nodata_expanded = np.repeat(nodata_mask_orig, zoom, axis=0)
        nodata_expanded = np.repeat(nodata_expanded, zoom, axis=1)
        uec[nodata_expanded] = 0.0
    
    if nodata_mask_down is not None:
        uec[nodata_mask_down] = 0.0
    
    if progress_callback:
        progress_callback("Elevation constraints applied (vectorized)", 70)
    
    return uec


def create_raster(fn, data, geot, proj, nodata_value=None, driver_fmt="GTiff", progress_callback=None):
    """Write result to raster file with nodata value preserved"""
    if progress_callback:
        progress_callback("Writing output file...", 90)
    
    driver = gdal.GetDriverByName(driver_fmt)
    if driver is None:
        raise Exception(f"Driver {driver_fmt} not available")
        
    outds = driver.Create(
        fn,
        xsize=data.shape[1],
        ysize=data.shape[0],
        bands=1,
        eType=gdal.GDT_Float32
    )
    outds.SetGeoTransform(geot)
    outds.SetProjection(proj)
    
    # Write data
    outds.GetRasterBand(1).WriteArray(data)
    
    # Set nodata value (use original if provided, otherwise use -9999 as default)
    if nodata_value is not None:
        outds.GetRasterBand(1).SetNoDataValue(nodata_value)
    else:
        outds.GetRasterBand(1).SetNoDataValue(-9999)
    
    outds = None
    
    if progress_callback:
        progress_callback("Completed!", 100)


def downscale_dem(input_file, output_file, zoom_factor, rsme, threshold=0.001, progress_callback=None, max_iterations=1000):
    """
    Main function to downscale DEM with detailed progress reporting
    
    Parameters:
    -----------
    input_file : str
        Path to input DEM file
    output_file : str
        Path to output DEM file
    zoom_factor : int
        Resolution increase factor (e.g., 4 = 4x increase)
    rsme : float
        RSME parameter for elevation constraint
    threshold : float
        Loop stopping threshold (default: 0.001)
    progress_callback : callable
        Callback function to update progress (receives message, percentage)
    max_iterations : int
        Maximum number of iterations to prevent infinite loops
    
    Returns:
    --------
    dict : Result information (iterations, final_energy, output_file, memory_info)
    """
    # Get raster info and estimate memory
    if progress_callback:
        device_info = ""
        if GPU_AVAILABLE:
            try:
                compute_cap = cp.cuda.Device(0).compute_capability
                try:
                    device_name = cp.cuda.runtime.getDeviceProperties(0)['name'].decode('utf-8')
                except:
                    device_name = "GPU"
                device_info = f" (GPU: {device_name}, Compute {compute_cap[0]}.{compute_cap[1]})"
            except Exception as e:
                device_info = f" (GPU: available, error getting info: {str(e)})"
        elif SCIPY_AVAILABLE:
            device_info = " (CPU vectorized)"
            if GPU_ERROR_MSG:
                device_info += f" [GPU unavailable: {GPU_ERROR_MSG}]"
        else:
            device_info = " (CPU loop-based)"
            if GPU_ERROR_MSG:
                device_info += f" [GPU unavailable: {GPU_ERROR_MSG}]"
        # Add runtime estimate
        raster_info = get_raster_info(input_file)
        runtime_est = estimate_runtime(
            raster_info['width'],
            raster_info['height'],
            zoom_factor,
            use_gpu=GPU_AVAILABLE,
            use_vectorized=SCIPY_AVAILABLE
        )
        runtime_info = f" | Est. time: {runtime_est['formatted_time']}"
        progress_callback(f"Reading input DEM...{device_info}{runtime_info}", 0)
    
    raster_info = get_raster_info(input_file)
    mem_estimate = estimate_memory_usage(
        raster_info['width'], 
        raster_info['height'], 
        zoom_factor
    )
    
    # Check available memory
    if PSUTIL_AVAILABLE:
        available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
    else:
        available_memory_mb = 4096  # Default assumption of 4GB if psutil not available
    
    if mem_estimate['total_mb'] > available_memory_mb * 0.8:
        warning_msg = (
            f"Warning: Estimated memory usage ({mem_estimate['total_mb']:.1f} MB) "
            f"may exceed available memory ({available_memory_mb:.1f} MB).\n"
            f"Processing may be slow or fail.\n\n"
            f"Input: {raster_info['width']}x{raster_info['height']} pixels\n"
            f"Output: {mem_estimate['output_size'][0]}x{mem_estimate['output_size'][1]} pixels\n"
            f"Estimated runtime: {runtime_est['formatted_time']}"
        )
        # Return warning but continue (user can cancel if needed)
        if progress_callback:
            progress_callback(warning_msg, 0)
    
    # Read original DEM data and nodata value
    if progress_callback:
        progress_callback("Loading DEM data into memory...", 2)
    goc, nodata_value = get_raster_band(input_file)
    
    # Create nodata mask for original DEM
    if nodata_value is not None:
        nodata_mask_orig = (goc == nodata_value) | np.isnan(goc)
    else:
        nodata_mask_orig = None
    
    # Get geo transform and projection information
    geotgoc = get_geo_transform(input_file)
    projgoc = get_projection(input_file)
    
    # Calculate new geo transform for downscaled DEM
    geotnew = [
        geotgoc[0],
        geotgoc[1] / zoom_factor,
        geotgoc[2],
        geotgoc[3],
        geotgoc[4],
        geotgoc[5] / zoom_factor
    ]
    
    # Initialize downscaling data (with nodata mask)
    dscal, nodata_mask_down = initialize(goc, zoom_factor, nodata_mask_orig, progress_callback)
    
    # Set nodata values in downscaled DEM
    if nodata_mask_down is not None and nodata_value is not None:
        dscal[nodata_mask_down] = nodata_value
    
    # Vòng lặp tối ưu hóa
    Energy_old = 100000000000.0
    Energy_dif = 100000000.0
    iteration = 0
    
    while abs(Energy_dif) > threshold and iteration < max_iterations:
        iteration += 1
        
        if progress_callback:
            progress_callback(
                f"Iteration {iteration}: Calculating spatial dependence...",
                70 + int((iteration / max_iterations) * 10)  # 70-80% range
            )
        
        # Auto-detect GPU availability
        use_gpu = GPU_AVAILABLE
        usd = spatial_dependence(dscal, nodata_mask_down, progress_callback, use_vectorized=True, use_gpu=use_gpu)
        
        if progress_callback:
            progress_callback(
                f"Iteration {iteration}: Applying elevation constraints...",
                80
            )
        
        uec = elevation_constraint(dscal, goc, rsme, nodata_mask_orig, nodata_mask_down, progress_callback, use_vectorized=True, use_gpu=use_gpu)
        
        u = usd + uec
        Energy_new = abs(usd).sum() + abs(uec).sum()
        dscal = dscal + u
        
        # Preserve nodata values after each iteration
        if nodata_mask_down is not None and nodata_value is not None:
            dscal[nodata_mask_down] = nodata_value
        
        Energy_dif = Energy_old - Energy_new
        Energy_old = Energy_new
        
        if progress_callback:
            progress_callback(
                f"Iteration {iteration}/{max_iterations}: Energy = {Energy_new:.6f}, "
                f"Change = {Energy_dif:.6f}",
                85
            )
    
    if iteration >= max_iterations:
        warning = f"Reached maximum iterations ({max_iterations}). Algorithm may not have converged."
        if progress_callback:
            progress_callback(warning, 85)
    
    # Ensure nodata values are preserved in final output
    if nodata_mask_down is not None and nodata_value is not None:
        dscal[nodata_mask_down] = nodata_value
    
    # Write result to file with nodata value preserved
    create_raster(output_file, dscal, geotnew, projgoc, nodata_value, progress_callback=progress_callback)
    
    return {
        'iterations': iteration,
        'final_energy': Energy_new,
        'output_file': output_file,
        'memory_estimate_mb': mem_estimate['total_mb'],
        'input_size': (raster_info['width'], raster_info['height']),
        'output_size': mem_estimate['output_size'],
        'converged': abs(Energy_dif) <= threshold,
        'nodata_preserved': nodata_value is not None
    }
