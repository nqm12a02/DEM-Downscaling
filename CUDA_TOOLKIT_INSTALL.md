# Hướng dẫn Cài đặt CUDA Toolkit để Sử dụng GPU

## Lỗi: "CuPy failed to load nvrtc64_112_0.dll"

Nếu bạn gặp lỗi này, có nghĩa là **CUDA Toolkit** chưa được cài đặt hoặc không có trong PATH.

### Giải thích

CuPy (thư viện GPU) cần **CUDA Toolkit** để hoạt động. CUDA Toolkit bao gồm:
- CUDA Runtime
- CUDA Compiler (nvcc)
- CUDA Runtime Compiler (NVRTC) - file `nvrtc64_*.dll`
- Các thư viện CUDA khác

Khi cài CuPy, nó **KHÔNG tự động cài CUDA Toolkit**. Bạn phải cài CUDA Toolkit riêng.

---

## Cách Cài đặt CUDA Toolkit

### Bước 1: Xác định phiên bản CUDA cần cài

Chạy trong Command Prompt:
```bash
nvidia-smi
```

Xem dòng **"CUDA Version"** - đây là phiên bản CUDA driver hỗ trợ (ví dụ: 11.8, 12.0, 12.1).

### Bước 2: Tải CUDA Toolkit

Truy cập: https://developer.nvidia.com/cuda-downloads

Chọn:
- **OS**: Windows
- **Architecture**: x86_64
- **Version**: Phù hợp với phiên bản trong `nvidia-smi` (ví dụ: 11.8, 12.0)
- **Installer Type**: `exe (local)` (khuyên dùng)

### Bước 3: Cài đặt CUDA Toolkit

1. Chạy file `.exe` đã tải
2. Chọn **Express Installation** (cài nhanh)
3. Đợi cài đặt hoàn tất (có thể mất 10-20 phút)
4. **Khởi động lại máy tính** sau khi cài xong

### Bước 4: Kiểm tra Cài đặt

Mở Command Prompt mới và chạy:
```bash
nvcc --version
```

Nếu thấy phiên bản CUDA → Cài đặt thành công!

### Bước 5: Khởi động lại QGIS

Sau khi cài CUDA Toolkit và restart máy:
1. Đóng QGIS hoàn toàn
2. Mở lại QGIS
3. Mở plugin DEM Downscaling
4. Kiểm tra status bar - nên thấy "GPU Available"

---

## Lưu ý Quan trọng

### 1. Phiên bản CuPy và CUDA Toolkit phải khớp

- **CuPy cho CUDA 11.x** → Cài **CUDA Toolkit 11.x** (ví dụ: 11.8)
- **CuPy cho CUDA 12.x** → Cài **CUDA Toolkit 12.x** (ví dụ: 12.0, 12.1)

### 2. Phiên bản CUDA Toolkit có thể cao hơn CUDA Driver

Ví dụ:
- **CUDA Driver** (từ `nvidia-smi`): 11.8
- **CUDA Toolkit có thể cài**: 11.8, 11.9, 12.0, 12.1 (miễn là >= 11.8)

Nhưng **CuPy phải khớp với CUDA Toolkit**, không phải Driver.

### 3. Nếu không muốn cài CUDA Toolkit

Bạn vẫn có thể dùng plugin với **CPU vectorized** (có SciPy):
- Cài SciPy: `python -m pip install scipy`
- Plugin sẽ tự động dùng CPU (nhanh hơn 10-100x so với không có thư viện)
- Không cần GPU hoặc CUDA Toolkit

---

## Xử lý Lỗi

### Lỗi: "nvcc is not recognized"
**Nguyên nhân:** CUDA Toolkit chưa được cài hoặc không có trong PATH
**Giải pháp:** 
- Cài lại CUDA Toolkit
- Đảm bảo chọn "Add to PATH" khi cài đặt
- Khởi động lại máy tính

### Lỗi: "CUDA version mismatch"
**Nguyên nhân:** Phiên bản CuPy không khớp với CUDA Toolkit
**Giải pháp:**
- Gỡ CuPy: `python -m pip uninstall cupy`
- Cài lại CuPy đúng phiên bản CUDA Toolkit
- Ví dụ: Nếu có CUDA Toolkit 11.8 → Cài `cupy-cuda11x`
- Ví dụ: Nếu có CUDA Toolkit 12.0 → Cài `cupy-cuda12x`

### Lỗi vẫn còn sau khi cài CUDA Toolkit
**Giải pháp:**
1. Khởi động lại máy tính
2. Kiểm tra PATH environment variable có chứa CUDA bin không:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin
   ```
3. Nếu không có, thêm vào PATH:
   - Right-click **This PC** → **Properties**
   - **Advanced system settings** → **Environment Variables**
   - Thêm đường dẫn CUDA bin vào **Path**

---

## Tóm tắt

1. **Lỗi nvrtc64_*.dll** → Cần cài **CUDA Toolkit**
2. Tải CUDA Toolkit từ: https://developer.nvidia.com/cuda-downloads
3. Cài đặt và **khởi động lại máy**
4. **Khởi động lại QGIS**
5. Plugin sẽ tự động sử dụng GPU

Nếu vẫn gặp vấn đề, plugin sẽ tự động fallback về CPU processing (vẫn nhanh nếu có SciPy).



