# 🚀 HƯỚNG DẪN DEPLOY LÊN STREAMLIT CLOUD

## Bước 1: Tạo tài khoản GitHub (nếu chưa có)

1. Truy cập: https://github.com
2. Click "Sign up" để đăng ký (miễn phí)
3. Xác nhận email

## Bước 2: Tạo Repository trên GitHub

1. Đăng nhập GitHub
2. Click nút **"+"** ở góc trên bên phải → **"New repository"**
3. Điền thông tin:
   - **Repository name**: `so-thu-chi-salon` (hoặc tên bạn muốn)
   - **Description**: "Ứng dụng quản lý thu chi salon"
   - Chọn **Public** (miễn phí) hoặc **Private** (nếu muốn riêng tư)
   - **KHÔNG** tích "Add a README file"
   - **KHÔNG** tích "Add .gitignore"
   - **KHÔNG** tích "Choose a license"
4. Click **"Create repository"**

## Bước 3: Upload code lên GitHub

### Cách 1: Dùng Terminal (Khuyến nghị)

Mở Terminal và chạy các lệnh sau:

```bash
# Di chuyển vào thư mục dự án
cd "/Users/huynhchitam/Downloads/ALT-CHÍ TÂM/thu chi hang ngay"

# Khởi tạo git (nếu chưa có)
git init

# Thêm tất cả file
git add .

# Commit
git commit -m "Initial commit - So Thu Chi Salon"

# Thêm remote repository (thay TEN_USER và TEN_REPO bằng thông tin của bạn)
git remote add origin https://github.com/TEN_USER/TEN_REPO.git

# Push lên GitHub
git branch -M main
git push -u origin main
```

**Lưu ý**: 
- Thay `TEN_USER` bằng tên GitHub của bạn
- Thay `TEN_REPO` bằng tên repository bạn vừa tạo
- Nếu GitHub yêu cầu đăng nhập, bạn sẽ cần tạo Personal Access Token

### Cách 2: Dùng GitHub Desktop (Dễ hơn)

1. Tải GitHub Desktop: https://desktop.github.com
2. Cài đặt và đăng nhập
3. File → Add Local Repository
4. Chọn thư mục dự án
5. Click "Publish repository"
6. Chọn repository vừa tạo và click "Publish"

### Cách 3: Upload trực tiếp trên web

1. Vào repository vừa tạo trên GitHub
2. Click "uploading an existing file"
3. Kéo thả các file: `app.py`, `requirements.txt`, `README.md`, `.gitignore`
4. Click "Commit changes"

## Bước 4: Deploy lên Streamlit Cloud

1. Truy cập: https://share.streamlit.io
2. Click **"Sign in"** → Chọn **"Continue with GitHub"**
3. Cho phép Streamlit truy cập GitHub
4. Click **"New app"**
5. Điền thông tin:
   - **Repository**: Chọn repository vừa tạo
   - **Branch**: `main` (hoặc `master`)
   - **Main file path**: `app.py`
6. Click **"Deploy"**

## Bước 5: Chờ deploy hoàn tất

- Streamlit sẽ tự động cài đặt dependencies
- Thời gian: 2-5 phút
- Khi xong, bạn sẽ có URL: `https://TEN_APP.streamlit.app`

## ✅ Hoàn tất!

Bây giờ bạn có thể:
- Chia sẻ URL cho nhân viên
- Truy cập từ bất kỳ đâu
- Dữ liệu lưu trên cloud (miễn phí)

---

## 🔧 Xử lý lỗi thường gặp

### Lỗi: "Module not found"
- Kiểm tra `requirements.txt` đã có đủ thư viện chưa
- Đảm bảo đã commit file `requirements.txt`

### Lỗi: "File not found"
- Kiểm tra đường dẫn file trong code
- Đảm bảo các file cần thiết đã được commit

### Lỗi: "Permission denied"
- Kiểm tra quyền truy cập repository
- Đảm bảo repository là Public hoặc bạn đã cấp quyền

---

## 📝 Lưu ý quan trọng

1. **Dữ liệu**: Dữ liệu sẽ lưu trên Streamlit Cloud (tạm thời)
2. **Bảo mật**: URL công khai, ai có link đều truy cập được
3. **Backup**: Nên xuất Excel định kỳ để backup
4. **Cập nhật**: Mỗi lần push code mới, Streamlit sẽ tự động deploy lại

---

## 🔄 Cập nhật ứng dụng sau này

Khi có thay đổi code:

```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

Streamlit sẽ tự động deploy lại trong vài phút.

