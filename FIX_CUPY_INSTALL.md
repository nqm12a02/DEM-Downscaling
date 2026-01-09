# CÁCH CÀI CUPY ĐÚNG - QUAN TRỌNG!

## Vấn đề: "Invalid Data Source: cupy-cuda11x..."

**Nguyên nhân:** Bạn đang dùng `qgis-ltr-bin.exe` - đây là file chạy QGIS, KHÔNG phải Python!

## Giải pháp: Dùng Python executable đúng

### Cách 1: Tìm Python executable đúng trong QGIS

1. Mở QGIS
2. Vào **Plugins** → **Python Console**
3. Chạy lệnh này:
   ```python
   import sys
   import os
   print("Python executable:", sys.executable)
   print("Python directory:", os.path.dirname(sys.executable))
   ```
4. Copy đường dẫn Python executable

**Thường thì sẽ là một trong những file sau:**
- `C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat`
- `C:\Program Files\QGIS 3.40.13\bin\python3.exe`
- `C:\OSGeo4W64\bin\python-qgis-ltr.bat`

### Cách 2: Sử dụng Python từ thư mục bin

Thay vì dùng `qgis-ltr-bin.exe`, thử dùng:

```bash
"C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install cupy-cuda11x
```

HOẶC:

```bash
"C:\Program Files\QGIS 3.40.13\bin\python3.exe" -m pip install cupy-cuda11x
```

### Cách 3: Sử dụng Python trực tiếp với full path

Trong Command Prompt:

```bash
cd "C:\Program Files\QGIS 3.40.13\bin"
python-qgis-ltr.bat -m pip install cupy-cuda11x
```

HOẶC:

```bash
cd "C:\Program Files\QGIS 3.40.13\bin"
python3.exe -m pip install cupy-cuda11x
```

## Kiểm tra Python executable đúng

Trong QGIS Python Console, chạy:
```python
import sys
print(sys.executable)
```

Nếu kết quả là:
- `C:\Program Files\QGIS 3.40.13\bin\qgis-ltr-bin.exe` → **SAI**, đây là QGIS executable
- `C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat` → **ĐÚNG**
- `C:\Program Files\QGIS 3.40.13\bin\python3.exe` → **ĐÚNG**

## Nếu sys.executable trả về qgis-ltr-bin.exe

Trong trường hợp này, bạn cần dùng Python từ cùng thư mục:

1. Lấy thư mục bin:
   ```python
   import sys
   import os
   bin_dir = os.path.dirname(sys.executable)
   print("Bin directory:", bin_dir)
   ```

2. Trong Command Prompt, thử một trong các lệnh sau:
   ```bash
   # Option 1: python-qgis-ltr.bat
   "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" -m pip install cupy-cuda11x
   
   # Option 2: python3.exe
   "C:\Program Files\QGIS 3.40.13\bin\python3.exe" -m pip install cupy-cuda11x
   
   # Option 3: python.exe
   "C:\Program Files\QGIS 3.40.13\bin\python.exe" -m pip install cupy-cuda11x
   ```



