# Hướng dẫn Cài đặt CuPy trên Windows - Chi tiết

## Lỗi: "Invalid Data Source: cupy-cuda11x is not a valid or recognized data source"

**Nguyên nhân:** Bạn đang cố chạy lệnh cài đặt trong QGIS (hoặc QGIS đang cố mở tên package), thay vì chạy từ Command Prompt.

**Giải pháp:** Phải cài đặt từ **Command Prompt** (bên ngoài QGIS), KHÔNG phải trong QGIS!

---

## Các Bước Cài đặt CuPy (Windows)

### Bước 1: Xác định Python của QGIS

1. Mở QGIS
2. Vào **Plugins** → **Python Console**
3. Gõ lệnh sau:
   ```python
   import sys; print(sys.executable)
   ```
4. Copy đường dẫn được hiển thị (ví dụ: `C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe` hoặc `C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat`)

### Bước 2: Mở Command Prompt (bên ngoài QGIS)

⚠️ **QUAN TRỌNG:** Phải mở Command Prompt riêng, KHÔNG chạy trong QGIS Python Console!

1. Nhấn `Win + R`
2. Gõ `cmd` và nhấn Enter
3. Hoặc tìm "Command Prompt" trong Start Menu

### Bước 3: Kiểm tra CUDA Version

Trong Command Prompt, chạy:
```bash
nvidia-smi
```

Xem dòng "CUDA Version" (ví dụ: 11.8, 12.0, 12.1, ...)

### Bước 4: Cài đặt CuPy

**Cho CUDA 11.x (phổ biến nhất):**
```bash
"C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe" -m pip install cupy-cuda11x
```

**Cho CUDA 12.x:**
```bash
"C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe" -m pip install cupy-cuda12x
```

**Lưu ý:**
- Thay đường dẫn bằng đường dẫn Python từ Bước 1
- **Bắt buộc** đặt trong dấu ngoặc kép `"..."` nếu có khoảng trắng
- Đợi cài đặt hoàn tất (có thể mất 5-10 phút)

### Bước 5: Kiểm tra Cài đặt

Trong Command Prompt, chạy:
```bash
"C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe" -c "import cupy; print('CuPy version:', cupy.__version__); print('CUDA available:', cupy.cuda.is_available())"
```

Nếu thấy "CuPy version: ..." và "CUDA available: True" → Cài đặt thành công!

### Bước 6: Khởi động lại QGIS

**Quan trọng:** Đóng QGIS hoàn toàn và mở lại để plugin phát hiện GPU.

---

## Ví dụ Lệnh Đầy đủ (Copy và Paste)

Nếu đường dẫn Python của bạn là: `C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe`

**Và bạn có CUDA 11.x:**
```bash
"C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe" -m pip install cupy-cuda11x
```

**Và bạn có CUDA 12.x:**
```bash
"C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe" -m pip install cupy-cuda12x
```

---

## Xử lý Lỗi Thường gặp

### Lỗi 1: "Invalid Data Source: cupy-cuda11x..."
**Nguyên nhân:** Đang chạy lệnh trong QGIS hoặc QGIS đang cố mở package
**Giải pháp:** 
- Đóng QGIS hoàn toàn
- Mở Command Prompt riêng (bên ngoài QGIS)
- Chạy lệnh trong Command Prompt

### Lỗi 2: "'C:\Program' is not recognized"
**Nguyên nhân:** Thiếu dấu ngoặc kép cho đường dẫn có khoảng trắng
**Giải pháp:** Thêm dấu ngoặc kép:
```bash
# SAI:
C:\Program Files\...\qgis-ltr-bin.exe -m pip install cupy-cuda11x

# ĐÚNG:
"C:\Program Files\...\qgis-ltr-bin.exe" -m pip install cupy-cuda11x
```

### Lỗi 3: "No module named 'pip'"
**Giải pháp:** Cài pip trước:
```bash
"C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe" -m ensurepip --upgrade
```

### Lỗi 4: "CUDA not found" hoặc "No CUDA-capable device"
**Nguyên nhân:** 
- CUDA drivers chưa được cài
- GPU không hỗ trợ CUDA
- CuPy version không khớp với CUDA version

**Giải pháp:**
- Cài đặt NVIDIA CUDA Toolkit từ NVIDIA website
- Kiểm tra GPU có hỗ trợ CUDA không (phải là NVIDIA GPU)
- Đảm bảo CuPy version khớp với CUDA version (cupy-cuda11x cho CUDA 11.x, cupy-cuda12x cho CUDA 12.x)

---

## Sau khi Cài đặt Thành công

1. **Khởi động lại QGIS** hoàn toàn
2. Mở plugin DEM Downscaling
3. Status bar sẽ hiển thị: `✅ GPU available: [Tên GPU]`
4. Runtime estimate sẽ hiển thị: `Est. time: ... (GPU)`
5. Xử lý sẽ nhanh hơn ~8x so với CPU vectorized

---

## Kiểm tra GPU hoạt động

Trong QGIS Python Console (sau khi cài CuPy và restart QGIS):
```python
import cupy as cp
print("CuPy version:", cp.__version__)
print("CUDA available:", cp.cuda.is_available())
if cp.cuda.is_available():
    print("GPU count:", cp.cuda.runtime.getDeviceCount())
    device = cp.cuda.Device(0)
    print("Compute capability:", device.compute_capability)
```

Nếu thấy "CUDA available: True" → GPU đã sẵn sàng!



