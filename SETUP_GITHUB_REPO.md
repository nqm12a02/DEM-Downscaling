# Setup GitHub Repository for QGIS Plugin Repository

## Vấn Đề:
QGIS Plugin Repository yêu cầu `repository` và `tracker` URLs phải tồn tại và có thể truy cập được (accessible trong 10 giây).

## Giải Pháp Tạm Thời (Để Upload Ngay):
Hiện tại metadata.txt đang dùng homepage URL cho cả repository và tracker. Điều này sẽ cho phép upload, nhưng không phải là best practice.

## Giải Pháp Đúng (Khuyến Nghị):

### Bước 1: Tạo GitHub Repository

1. **Đăng nhập GitHub**: https://github.com/login
   - Hoặc tạo tài khoản mới: https://github.com/signup

2. **Tạo Repository Mới**:
   - Vào: https://github.com/new
   - Repository name: `DEM_Downscaling`
   - Description: "QGIS Plugin for DEM Downscaling using Hopfield Neural Network"
   - Public: ✅ (phải public để QGIS có thể access)
   - Không tích "Initialize with README" (vì bạn sẽ upload code)

3. **Upload Plugin Code**:
   ```bash
   cd C:\Minh\DEM_Downscaling
   git init
   git add .
   git commit -m "Initial commit: DEM Downscaling QGIS Plugin"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/DEM_Downscaling.git
   git push -u origin main
   ```
   Hoặc sử dụng GitHub Desktop/GUI để upload.

### Bước 2: Cập Nhật metadata.txt

Sau khi tạo repository, cập nhật metadata.txt:

```ini
repository=https://github.com/YOUR_USERNAME/DEM_Downscaling
tracker=https://github.com/YOUR_USERNAME/DEM_Downscaling/issues
```

Thay `YOUR_USERNAME` bằng GitHub username của bạn.

### Bước 3: Rebuild Plugin

Chạy lại `package_for_repository.py` để rebuild plugin với metadata mới.

---

## Nếu Không Muốn Tạo GitHub Repository:

Bạn có thể sử dụng các alternatives:

### Option 1: GitLab
- Tạo repository trên GitLab: https://gitlab.com
- Cập nhật URLs tương tự

### Option 2: Bitbucket
- Tạo repository trên Bitbucket: https://bitbucket.org
- Cập nhật URLs tương tự

### Option 3: Sử Dụng Homepage URL (Tạm Thời)
- Giữ nguyên như hiện tại (đã cấu hình)
- Có thể upload được, nhưng sẽ không có source code public
- Nên update sau khi có repository

---

## Kiểm Tra URLs Có Hợp Lệ:

Sau khi cập nhật, test URLs bằng cách:
1. Mở browser
2. Truy cập repository URL - phải load trong 10 giây
3. Truy cập tracker URL - phải load trong 10 giây

QGIS repository sẽ kiểm tra tương tự.

---

## Lưu Ý:
- Repository phải là **PUBLIC** (không phải private)
- URLs phải accessible không cần authentication
- Tracker URL thường là repository URL + "/issues" (cho GitHub)
