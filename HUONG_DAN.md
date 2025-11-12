# 📖 HƯỚNG DẪN SỬ DỤNG VÀ TRIỂN KHAI

## 🚀 CÁCH 1: Deploy lên Streamlit Cloud (Khuyến nghị - Miễn phí)

### Bước 1: Tạo tài khoản GitHub
1. Truy cập https://github.com
2. Đăng ký tài khoản miễn phí (nếu chưa có)
3. Tạo repository mới (ví dụ: `so-thu-chi-salon`)

### Bước 2: Upload code lên GitHub
```bash
# Khởi tạo git (nếu chưa có)
git init
git add .
git commit -m "Initial commit"

# Thêm remote repository
git remote add origin https://github.com/TEN_USER/TEN_REPO.git
git push -u origin main
```

### Bước 3: Deploy lên Streamlit Cloud
1. Truy cập https://share.streamlit.io
2. Đăng nhập bằng tài khoản GitHub
3. Click "New app"
4. Chọn repository và branch
5. Main file path: `app.py`
6. Click "Deploy"

### Kết quả:
- Ứng dụng sẽ có URL công khai: `https://TEN_APP.streamlit.app`
- Nhân viên có thể truy cập từ bất kỳ đâu
- Dữ liệu lưu trên cloud (miễn phí)

---

## 🖥️ CÁCH 2: Chạy Local và Chia sẻ qua mạng nội bộ

### Bước 1: Cài đặt trên máy chủ
```bash
# Cài đặt Python (nếu chưa có)
# macOS: Python đã có sẵn
# Windows: Tải từ python.org

# Cài đặt thư viện
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng
```bash
streamlit run app.py
```

### Bước 3: Chia sẻ qua mạng nội bộ
1. Tìm địa chỉ IP máy chủ:
   - macOS/Linux: `ifconfig` hoặc `ipconfig`
   - Windows: `ipconfig`
   - Tìm dòng "IPv4 Address" (ví dụ: 192.168.1.100)

2. Chạy Streamlit với IP công khai:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

3. Nhân viên truy cập:
   - URL: `http://192.168.1.100:8501`
   - (Thay bằng IP thực tế của máy chủ)

### Lưu ý:
- Máy chủ phải bật và chạy ứng dụng
- Tất cả máy phải cùng mạng WiFi/LAN
- Có thể cần tắt firewall tạm thời

---

## 📱 CÁCH 3: Tạo file chạy tự động (Windows/macOS)

### Tạo file `start.bat` (Windows):
```batch
@echo off
echo Dang khoi dong ung dung...
cd /d %~dp0
python -m streamlit run app.py
pause
```

### Tạo file `start.sh` (macOS/Linux):
```bash
#!/bin/bash
echo "Đang khởi động ứng dụng..."
cd "$(dirname "$0")"
streamlit run app.py
```

### Cách sử dụng:
- Double-click vào file `start.bat` (Windows) hoặc `start.sh` (macOS)
- Ứng dụng sẽ tự động mở trong trình duyệt

---

## 📋 CHECKLIST TRƯỚC KHI ĐƯA CHO NHÂN VIÊN

- [ ] Đã test tất cả tính năng
- [ ] Đã tạo file hướng dẫn sử dụng
- [ ] Đã backup dữ liệu (nếu có)
- [ ] Đã kiểm tra kết nối mạng (nếu dùng cách 2)
- [ ] Đã thông báo URL/địa chỉ cho nhân viên

---

## 🔒 LƯU Ý BẢO MẬT

- **Cách 1 (Streamlit Cloud)**: Dữ liệu công khai, ai có link đều truy cập được
- **Cách 2 (Local)**: Chỉ truy cập trong mạng nội bộ, an toàn hơn
- Khuyến nghị: Dùng Cách 2 cho dữ liệu nhạy cảm

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề, kiểm tra:
1. Python đã cài đặt chưa: `python --version`
2. Thư viện đã cài đủ chưa: `pip list`
3. Port 8501 có bị chiếm không
4. Firewall có chặn không

