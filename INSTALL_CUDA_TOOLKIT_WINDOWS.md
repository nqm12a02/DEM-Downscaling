# Hướng Dẫn Cài Đặt CUDA Toolkit trên Windows

## Thông tin hệ thống của bạn:
- **GPU**: NVIDIA RTX A5000 Laptop GPU
- **CUDA Driver Version**: 13.0
- **Hệ điều hành**: Windows

---

## Bước 1: Xác định phiên bản CUDA Toolkit cần cài

### Kiểm tra lại thông tin GPU và CUDA Driver:

1. Mở **Command Prompt** (không phải QGIS Python Console!)
   - Nhấn `Win + R`
   - Gõ `cmd` và nhấn Enter

2. Chạy lệnh:
   ```bash
   nvidia-smi
   ```

3. Xem dòng **"CUDA Version"** ở trên cùng (ví dụ: 13.0, 12.6, 11.8)

### Chọn phiên bản CUDA Toolkit:

- **Nếu CUDA Version là 13.0** (như máy bạn): Tải CUDA Toolkit 12.x (vì CuPy chưa hỗ trợ CUDA 13.x đầy đủ, nhưng 12.x tương thích ngược)
- **Nếu CUDA Version là 12.x**: Tải CUDA Toolkit 12.x
- **Nếu CUDA Version là 11.x**: Tải CUDA Toolkit 11.x

**Khuyến nghị cho máy bạn**: Cài **CUDA Toolkit 12.6** (tương thích với driver 13.0 và có CuPy hỗ trợ)

---

## Bước 2: Tải CUDA Toolkit

### Cách 1: Tải từ trang chính thức NVIDIA (Khuyến nghị)

1. Truy cập: https://developer.nvidia.com/cuda-downloads

2. Chọn các tùy chọn:
   - **Operating System**: Windows
   - **Architecture**: x86_64
   - **Version**: 
     - Chọn **CUDA 12.6** (khuyến nghị) hoặc
     - Chọn **CUDA 11.8** nếu muốn dùng CuPy cuda11x
   - **Installer Type**: **exe (local)** (file lớn, ~3GB)

3. Click **Download** và đợi file tải về

### Cách 2: Tải từ Archive (nếu cần phiên bản cũ)

1. Truy cập: https://developer.nvidia.com/cuda-toolkit-archive

2. Chọn phiên bản cần thiết (ví dụ: CUDA Toolkit 12.6.0)

3. Chọn:
   - **Operating System**: Windows
   - **Architecture**: x86_64
   - **Version**: Windows 10/11
   - **Installer Type**: exe (local)

4. Click **Download**

---

## Bước 3: Cài đặt CUDA Toolkit

### Trước khi cài:

1. **Đóng tất cả ứng dụng đang sử dụng GPU**, bao gồm:
   - QGIS
   - Game, video players
   - Các ứng dụng khác dùng GPU

2. **Chạy file cài đặt với quyền Administrator**:
   - Right-click file `.exe` đã tải
   - Chọn **"Run as administrator"**

### Quá trình cài đặt:

1. **Extraction**: 
   - File sẽ tự giải nén vào thư mục tạm
   - Đợi quá trình này hoàn tất (có thể mất vài phút)

2. **CUDA Setup Wizard**:
   - Chọn **"Express"** (khuyến nghị)
   - Hoặc chọn **"Custom"** nếu muốn tùy chọn

3. **Express Installation** sẽ cài:
   - ✅ CUDA Toolkit
   - ✅ CUDA Samples
   - ✅ CUDA Documentation
   - ✅ Driver (nếu chưa cập nhật)

4. **Đợi quá trình cài đặt**:
   - Có thể mất 10-30 phút tùy vào máy
   - **KHÔNG tắt máy hoặc ngắt kết nối** trong quá trình cài

5. **Khi cài xong**:
   - Click **"Close"**
   - **QUAN TRỌNG**: Restart máy tính ngay lập tức!

---

## Bước 4: Xác minh cài đặt

### Sau khi restart máy:

1. Mở **Command Prompt** (mới)

2. Kiểm tra CUDA Toolkit đã cài đặt:
   ```bash
   nvcc --version
   ```
   
   Kết quả mong đợi:
   ```
   nvcc: NVIDIA (R) Cuda compiler driver
   Copyright (c) 2005-2024 NVIDIA Corporation
   Built on ...
   Cuda compilation tools, release 12.6, V12.6.xxx
   ```

3. Kiểm tra nvcc trong PATH:
   ```bash
   where nvcc
   ```
   
   Kết quả sẽ hiển thị đường dẫn như:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe
   ```

4. Kiểm tra GPU vẫn hoạt động:
   ```bash
   nvidia-smi
   ```
   
   Xác nhận GPU vẫn hiển thị bình thường

---

## Bước 5: Kiểm tra với plugin DEM Downscaling

1. Mở QGIS

2. Chạy script kiểm tra:
   - Mở **Command Prompt**
   - Chạy:
     ```bash
     cd C:\Minh\DEM_Downscaling
     "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" check_gpu_cuda.py
     ```
   
   Hoặc double-click: `check_gpu_cuda.bat`

3. Kiểm tra kết quả:
   - Phần "2. Checking CUDA Toolkit Installation" phải hiển thị: `[OK] Found CUDA Toolkit`
   - Phần "3. Checking CuPy Installation" - tiếp tục cài CuPy nếu chưa có

---

## Bước 6: Sửa lỗi PATH (nếu cần)

Nếu `nvcc --version` không hoạt động sau khi cài:

### Cách 1: Tự động (Khuyến nghị)

1. Mở **Command Prompt** với quyền Administrator
2. Chạy:
   ```bash
   cd C:\Minh\DEM_Downscaling
   "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" fix_cuda_dll.py
   ```
   
   Script sẽ tự động thêm CUDA vào PATH

### Cách 2: Thủ công

1. Nhấn `Win + R`, gõ `sysdm.cpl`, nhấn Enter
2. Tab **"Advanced"** → **"Environment Variables"**
3. Trong **"User variables"**, tìm và chọn **"Path"** → Click **"Edit"**
4. Click **"New"** và thêm:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin
   ```
   (Thay `v12.6` bằng phiên bản bạn đã cài)
5. Click **OK** ở tất cả các cửa sổ
6. **Restart Command Prompt** (đóng và mở lại)

---

## Xử lý lỗi thường gặp

### Lỗi 1: "nvcc is not recognized"

**Nguyên nhân**: CUDA bin chưa có trong PATH

**Giải pháp**: 
- Xem **Bước 6** ở trên
- Hoặc chạy `fix_cuda_dll.py`

### Lỗi 2: Cài đặt bị gián đoạn hoặc lỗi

**Giải pháp**:
1. Uninstall CUDA Toolkit cũ (nếu có) từ Control Panel → Programs
2. Dọn dẹp registry (cẩn thận, chỉ nếu bạn biết cách)
3. Restart máy
4. Cài lại từ đầu

### Lỗi 3: GPU không hiển thị sau khi cài

**Giải pháp**:
1. Kiểm tra driver NVIDIA vẫn hoạt động: `nvidia-smi`
2. Nếu không hiển thị, cài lại NVIDIA Driver:
   - Tải từ: https://www.nvidia.com/drivers
   - Chọn GPU model: RTX A5000 Laptop
   - Cài driver mới nhất

### Lỗi 4: Không đủ dung lượng ổ cứng

**Yêu cầu**: CUDA Toolkit cần khoảng **3-5 GB** dung lượng

**Giải pháp**:
- Giải phóng dung lượng ổ C:
- Hoặc chọn thư mục cài đặt khác trong Custom Installation

---

## Tiếp theo: Cài đặt CuPy

Sau khi CUDA Toolkit đã hoạt động:

1. Xác định phiên bản CuPy cần cài:
   - Nếu cài CUDA 12.6: `cupy-cuda12x`
   - Nếu cài CUDA 11.8: `cupy-cuda11x`

2. Cài đặt CuPy:
   ```bash
   "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install cupy-cuda12x
   ```

3. Restart QGIS hoàn toàn

4. Kiểm tra lại với `check_gpu_cuda.py`

---

## Tóm tắt các bước:

1. ✅ Kiểm tra CUDA Driver version: `nvidia-smi`
2. ✅ Tải CUDA Toolkit 12.6 từ NVIDIA
3. ✅ Chạy installer với quyền Administrator
4. ✅ Chọn Express Installation
5. ✅ **Restart máy tính** (QUAN TRỌNG!)
6. ✅ Kiểm tra: `nvcc --version`
7. ✅ Chạy `fix_cuda_dll.py` để sửa PATH nếu cần
8. ✅ Kiểm tra lại với `check_gpu_cuda.py`
9. ✅ Cài CuPy: `pip install cupy-cuda12x`
10. ✅ Restart QGIS và test plugin

---

## Liên kết hữu ích:

- **CUDA Toolkit Download**: https://developer.nvidia.com/cuda-downloads
- **CUDA Toolkit Archive**: https://developer.nvidia.com/cuda-toolkit-archive
- **CUDA Documentation**: https://docs.nvidia.com/cuda/
- **CuPy Installation Guide**: https://docs.cupy.dev/en/stable/install.html

---

**Chúc bạn cài đặt thành công!** 🚀

Nếu gặp vấn đề, hãy chạy `check_gpu_cuda.py` và gửi kết quả để được hỗ trợ.


