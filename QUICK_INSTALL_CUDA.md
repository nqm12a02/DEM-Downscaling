# Quick Guide: Install CUDA Toolkit (Step-by-Step)

## Your System Info:
- **GPU**: NVIDIA RTX A5000 Laptop GPU ✅
- **CUDA Driver**: 13.0 ✅
- **Status**: Need CUDA Toolkit ❌

---

## 🚀 Quick Installation Steps:

### Step 1: Download CUDA Toolkit 12.6
👉 **Link**: https://developer.nvidia.com/cuda-12-6-0-download-archive

**Select:**
- Operating System: **Windows**
- Architecture: **x86_64**  
- Version: **Windows 10/11**
- Installer Type: **exe (local)**

**Download size**: ~3 GB (may take 10-30 minutes)

---

### Step 2: Install CUDA Toolkit

1. **Close all applications** using GPU (QGIS, games, etc.)

2. **Right-click** the downloaded `.exe` file
   - Select **"Run as administrator"**

3. **Choose "Express" installation**
   - Wait 10-30 minutes for installation

4. **Click "Close" when done**

5. **🔄 RESTART YOUR COMPUTER** (MANDATORY!)

---

### Step 3: Verify Installation

Open **Command Prompt** (not QGIS!) and run:

```bash
nvcc --version
```

**Expected output:**
```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
...
Cuda compilation tools, release 12.6, V12.6.xxx
```

✅ If you see this → CUDA Toolkit installed successfully!

❌ If "nvcc is not recognized" → See troubleshooting below

---

### Step 4: Fix PATH (if needed)

If `nvcc --version` doesn't work:

**Option A: Automatic fix**
```bash
cd C:\Minh\DEM_Downscaling
"C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" fix_cuda_dll.py
```

**Option B: Manual fix**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click **"Environment Variables"**
3. Under **"User variables"**, find **"Path"** → Click **"Edit"**
4. Click **"New"** → Add:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin
   ```
5. Click **OK** on all windows
6. Close and reopen Command Prompt

---

### Step 5: Test with Plugin

Run diagnostic:
```bash
cd C:\Minh\DEM_Downscaling
python check_gpu_cuda.py
```

**Expected result:**
```
2. Checking CUDA Toolkit Installation...
[OK] Found 1 CUDA Toolkit installation(s):
   - Version v12.6 at C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6
   [OK] CUDA v12.6 is in PATH
```

---

### Step 6: Install CuPy

After CUDA Toolkit works, install CuPy:

```bash
"C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install cupy-cuda12x
```

This may take 5-15 minutes (downloads ~500 MB)

---

### Step 7: Final Test

1. **Restart QGIS completely**

2. Run diagnostic again:
   ```bash
   python check_gpu_cuda.py
   ```

3. **Expected result:**
   ```
   [OK] SYSTEM READY FOR GPU ACCELERATION!
   Your laptop is fully configured for GPU processing.
   ```

---

## ⚠️ Troubleshooting

### Problem: "nvcc is not recognized"
**Solution**: See Step 4 above (Fix PATH)

### Problem: Installation fails
**Solution**: 
- Make sure you run as Administrator
- Close all GPU applications
- Check you have 5+ GB free disk space

### Problem: GPU not detected after install
**Solution**:
1. Run `nvidia-smi` to check driver
2. If not working, reinstall NVIDIA driver from: https://www.nvidia.com/drivers

---

## 📋 Checklist

- [ ] Downloaded CUDA Toolkit 12.6 (~3 GB)
- [ ] Ran installer as Administrator
- [ ] Selected Express installation
- [ ] Restarted computer
- [ ] Verified: `nvcc --version` works
- [ ] Ran `fix_cuda_dll.py` (if needed)
- [ ] Verified: `check_gpu_cuda.py` shows CUDA Toolkit [OK]
- [ ] Installed CuPy: `pip install cupy-cuda12x`
- [ ] Restarted QGIS
- [ ] Final test: `check_gpu_cuda.py` shows all [OK]

---

## 🎯 Next Steps

Once everything is [OK]:
1. Open QGIS
2. Use DEM Downscaling plugin
3. Plugin will automatically use GPU (8x faster!)

---

**Need more details?** See: `INSTALL_CUDA_TOOLKIT_WINDOWS.md`

**Having issues?** Run `check_gpu_cuda.py` and check the error messages.


