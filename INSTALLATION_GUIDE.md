# Hướng dẫn Cài đặt Thư viện Hiệu năng

## Tổng quan

Plugin DEM Downscaling **hoạt động tốt ngay cả khi không cài đặt** SciPy hoặc CuPy. Tuy nhiên, việc cài đặt các thư viện này sẽ giúp xử lý nhanh hơn đáng kể:

- **Không có thư viện nào**: Xử lý chậm (loop-based)
- **Có SciPy**: Nhanh hơn **10-100 lần** trên CPU
- **Có CuPy (và GPU NVIDIA)**: Nhanh hơn thêm **8 lần** nữa (tổng cộng 80-800 lần so với không có thư viện)

## Trả lời câu hỏi

### 1. Có phải cài CuPy và SciPy từ trước không?

**Không bắt buộc!** Plugin sẽ tự động phát hiện và sử dụng các thư viện có sẵn:
- Nếu có CuPy và GPU → dùng GPU (nhanh nhất)
- Nếu có SciPy → dùng CPU vectorized (nhanh)
- Nếu không có gì → dùng CPU loop-based (chậm nhưng vẫn hoạt động)

### 2. Nếu không có các thư viện này thì sao?

Plugin vẫn hoạt động bình thường, chỉ là xử lý sẽ chậm hơn. Bạn vẫn có thể:
- Xử lý DEM nhỏ (<1000×1000 pixels) mà không vấn đề gì
- Xử lý DEM lớn nhưng mất nhiều thời gian hơn
- Tất cả các tính năng đều hoạt động (NoData, progress bar, etc.)

### 3. Có thể hướng dẫn cài các thư viện này không?

**Có!** Đọc hướng dẫn bên dưới hoặc nhấn nút **"📦 Install Performance Libraries"** trong dialog của plugin.

---

## Hướng dẫn Cài đặt

### Bước 1: Xác định Python của QGIS

1. Mở QGIS
2. Vào menu **Plugins** → **Python Console**
3. Gõ lệnh sau và nhấn Enter:
   ```python
   import sys; print(sys.executable)
   ```
4. Copy đường dẫn Python được hiển thị (ví dụ: `C:\OSGeo4W64\bin\python-qgis-ltr.bat`)

### Bước 2: Mở Command Prompt/Terminal

**⚠️ QUAN TRỌNG:** Phải cài đặt từ **Command Prompt/Terminal** (bên ngoài QGIS), KHÔNG phải trong QGIS Python Console!

**Windows:**
- Nhấn `Win + R`
- Gõ `cmd` và nhấn Enter
- Hoặc tìm "Command Prompt" trong Start Menu
- **KHÔNG** cài trong QGIS Python Console!

**Linux/Mac:**
- Mở Terminal

### Bước 3: Cài đặt SciPy (Khuyến nghị)

SciPy làm cho xử lý nhanh hơn **10-100 lần** trên CPU.

**Windows (OSGeo4W):**
```bash
C:\OSGeo4W64\bin\python-qgis-ltr.bat -m pip install scipy
```

**Windows (QGIS installed in Program Files - CÓ KHOẢNG TRẮNG):**
```bash
"C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install scipy
```
**⚠️ LƯU Ý:** Nếu đường dẫn có khoảng trắng (như "Program Files"), phải đặt trong dấu ngoặc kép `"..."`

**Linux:**
```bash
pip3 install scipy
```

**Mac:**
```bash
pip3 install scipy
```

**Hoặc dùng Python path từ Bước 1 (QUAN TRỌNG: thêm dấu ngoặc kép nếu có khoảng trắng):**
```bash
# Nếu đường dẫn có khoảng trắng:
"<đường_dẫn_python_từ_bước_1>" -m pip install scipy

# Nếu đường dẫn không có khoảng trắng:
<đường_dẫn_python_từ_bước_1> -m pip install scipy
```

### Bước 4: Cài đặt CuPy (Tùy chọn, cho GPU)

Chỉ cần cài nếu bạn có **NVIDIA GPU** với CUDA support.

**Kiểm tra GPU:**
```bash
nvidia-smi
```

Nếu lệnh này hoạt động, bạn có GPU NVIDIA.

**Cài đặt CuPy (CUDA 11.x):**
```bash
# Nếu đường dẫn có khoảng trắng (như "Program Files"):
"<đường_dẫn_python>" -m pip install cupy-cuda11x

# Ví dụ:
"C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install cupy-cuda11x
```

**Cài đặt CuPy (CUDA 12.x):**
```bash
# Nếu đường dẫn có khoảng trắng:
"<đường_dẫn_python>" -m pip install cupy-cuda12x

# Ví dụ:
"C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install cupy-cuda12x
```

**⚠️ QUAN TRỌNG:** 
- Nếu đường dẫn Python có khoảng trắng (ví dụ: `C:\Program Files\...`), **phải đặt trong dấu ngoặc kép** `"..."`
- Nếu không có khoảng trắng, không cần dấu ngoặc kép

**Xác định phiên bản CUDA:**
- Chạy `nvidia-smi` và xem dòng "CUDA Version"
- Hoặc xem trong NVIDIA Control Panel

### Bước 5: Khởi động lại QGIS

Sau khi cài đặt, **khởi động lại QGIS** để các thư viện được tải.

### Bước 6: Kiểm tra Cài đặt

1. Mở lại plugin DEM Downscaling
2. Xem thông báo trong status bar:
   - ✅ **GPU available** → CuPy đã cài đặt và hoạt động
   - ✅ **CPU vectorized** → SciPy đã cài đặt và hoạt động
   - ⚠️ **Slow mode** → Chưa cài thư viện nào

---

## Sử dụng Nút "Install Performance Libraries" trong Plugin

1. Mở plugin DEM Downscaling
2. Nhấn nút **"📦 Install Performance Libraries"**
3. Hộp thoại sẽ hiển thị:
   - Hướng dẫn cài đặt chi tiết
   - Lệnh cài đặt được tạo tự động cho Python của bạn
   - Nút để copy lệnh vào clipboard
4. **⚠️ QUAN TRỌNG:** Copy lệnh và chạy trong **Command Prompt/Terminal** (bên ngoài QGIS), KHÔNG phải trong QGIS Python Console!
5. Đợi cài đặt hoàn tất (có thể mất vài phút)
6. Khởi động lại QGIS hoàn toàn

---

## Xử lý Lỗi

### Lỗi: "pip is not recognized"
**Nguyên nhân:** pip chưa được cài hoặc không có trong PATH
**Giải pháp:** Dùng Python path đầy đủ:
```bash
python -m pip install scipy
```

### Lỗi: "Permission denied"
**Windows:** Chạy Command Prompt với quyền Administrator
**Linux/Mac:** Thêm `sudo`:
```bash
sudo pip3 install scipy
```

### Lỗi: "No module named 'pip'"
**Giải pháp:** Cài pip trước:
```bash
python -m ensurepip --upgrade
```

### CuPy: "CUDA not found" hoặc "nvrtc64_*.dll not found"
**Nguyên nhân:** CUDA Toolkit chưa được cài đặt
**Giải pháp:** 
- **Bắt buộc cài CUDA Toolkit** từ NVIDIA: https://developer.nvidia.com/cuda-downloads
- Xem hướng dẫn chi tiết trong `CUDA_TOOLKIT_INSTALL.md`
- Hoặc chỉ dùng SciPy (CPU vectorized cũng rất nhanh) - không cần GPU

### CuPy: "CuPy failed to load nvrtc64_112_0.dll"
**Nguyên nhân:** CUDA Toolkit chưa được cài đặt hoặc không có trong PATH
**Giải pháp:**
1. Cài đặt CUDA Toolkit từ NVIDIA (xem `CUDA_TOOLKIT_INSTALL.md`)
2. Khởi động lại máy tính sau khi cài
3. Khởi động lại QGIS
4. Plugin sẽ tự động fallback về CPU nếu GPU vẫn lỗi (vẫn nhanh nếu có SciPy)

---

## Hiệu năng Mong đợi

| Cấu hình | DEM 1000×1000 (zoom 4x) | DEM 3600×3600 (zoom 4x) |
|----------|-------------------------|-------------------------|
| Không có thư viện | ~15 phút | ~4 giờ |
| Có SciPy (CPU) | ~30 giây | ~6 phút |
| Có CuPy (GPU) | ~5 giây | ~45 giây |

*Hiệu năng có thể khác nhau tùy vào phần cứng*

---

## Câu hỏi Thường gặp

**Q: Tôi có thể cài đặt sau không?**  
A: Có! Plugin hoạt động ngay cả khi không có các thư viện này. Bạn có thể cài đặt bất cứ lúc nào.

**Q: Có ảnh hưởng gì đến plugin khác không?**  
A: Không. Các thư viện này chỉ được plugin DEM Downscaling sử dụng khi có sẵn.

**Q: Có tốn tiền không?**  
A: Không! SciPy và CuPy đều là phần mềm miễn phí và mã nguồn mở.

**Q: Tôi có thể gỡ cài đặt không?**  
A: Có:
```bash
python -m pip uninstall scipy cupy
```

---

## Tóm tắt

1. **Không bắt buộc** cài đặt SciPy/CuPy - plugin vẫn hoạt động
2. **Nên cài SciPy** để có hiệu năng tốt nhất trên CPU
3. **Có thể cài CuPy** nếu có GPU NVIDIA để tăng tốc thêm
4. Sử dụng nút **"📦 Install Performance Libraries"** trong plugin để được hướng dẫn tự động
5. Khởi động lại QGIS sau khi cài đặt

