# Hướng Dẫn Nhanh: Tạo GitHub Repository để Upload Plugin

## ⚡ Giải Pháp Nhanh (5 phút)

### Bước 1: Tạo GitHub Account (nếu chưa có)
1. Vào: https://github.com/signup
2. Đăng ký tài khoản miễn phí

### Bước 2: Tạo Repository
1. Đăng nhập GitHub
2. Click nút **"+"** (góc trên bên phải) → **"New repository"**
3. Điền thông tin:
   - **Repository name**: `DEM_Downscaling`
   - **Description**: `QGIS Plugin for DEM Downscaling using Hopfield Neural Network`
   - **Public**: ✅ (QUAN TRỌNG: phải public!)
   - **Không tích** "Add a README file"
   - **Không tích** "Add .gitignore"
   - **Không tích** "Choose a license"
4. Click **"Create repository"**

### Bước 3: Upload Code (Chọn 1 trong 2 cách)

#### Cách A: Sử dụng GitHub Web Interface (Dễ nhất)
1. Trên trang repository mới tạo, bạn sẽ thấy hướng dẫn "uploading an existing file"
2. Click **"uploading an existing file"**
3. Drag & drop tất cả files từ folder `C:\Minh\DEM_Downscaling` vào
4. Scroll xuống, nhập commit message: `Initial commit: QGIS DEM Downscaling Plugin`
5. Click **"Commit changes"**

#### Cách B: Sử dụng Git Command Line
Mở Command Prompt trong `C:\Minh\DEM_Downscaling` và chạy:

```bash
git init
git add .
git commit -m "Initial commit: QGIS DEM Downscaling Plugin"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/DEM_Downscaling.git
git push -u origin main
```
(Thay `YOUR_USERNAME` bằng GitHub username của bạn)

### Bước 4: Lấy Repository URL
Sau khi upload xong, repository URL sẽ là:
```
https://github.com/YOUR_USERNAME/DEM_Downscaling
```

Tracker URL sẽ là:
```
https://github.com/YOUR_USERNAME/DEM_Downscaling/issues
```

### Bước 5: Cập Nhật metadata.txt
Mở file `DEM_Downscaling/metadata.txt` và thay đổi:
```ini
repository=https://github.com/YOUR_USERNAME/DEM_Downscaling
tracker=https://github.com/YOUR_USERNAME/DEM_Downscaling/issues
```

### Bước 6: Rebuild Plugin
Chạy lại: `python package_for_repository.py`

### Bước 7: Upload Lên QGIS Repository
Upload file ZIP mới và metadata sẽ pass validation! ✅

---

## ✅ Checklist:
- [ ] GitHub account đã tạo
- [ ] Repository đã tạo (Public)
- [ ] Code đã upload
- [ ] Repository URL đã lấy được
- [ ] metadata.txt đã cập nhật với URLs mới
- [ ] Plugin đã rebuild
- [ ] Sẵn sàng upload lên QGIS repository

---

## ⚠️ Lưu Ý:
- Repository **PHẢI** là **PUBLIC** (không được private)
- URLs phải accessible không cần login
- Sau khi tạo repository, đợi 1-2 phút để GitHub index, rồi mới test URLs
