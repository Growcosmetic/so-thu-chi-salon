# 📖 HƯỚNG DẪN SETUP GOOGLE SHEETS - CHI TIẾT TỪNG BƯỚC

## 🎯 Mục đích
Xuất dữ liệu thu chi lên Google Sheets để:
- ✅ Truy cập online từ mọi nơi
- ✅ Xem và chỉnh sửa trên điện thoại/tablet
- ✅ Chia sẻ với người khác dễ dàng
- ✅ Tự động backup dữ liệu

---

## 📋 BƯỚC 1: TẠO GOOGLE CLOUD PROJECT

1. **Vào Google Cloud Console:**
   - Mở trình duyệt, vào: https://console.cloud.google.com/
   - Đăng nhập bằng tài khoản Google của bạn

2. **Tạo Project mới:**
   - Click vào dropdown "Select a project" ở đầu trang
   - Click "NEW PROJECT"
   - Đặt tên: `So Thu Chi Salon` (hoặc tên khác)
   - Click "CREATE"
   - Đợi vài giây để project được tạo

---

## 📋 BƯỚC 2: BẬT GOOGLE SHEETS API VÀ DRIVE API

1. **Vào API Library:**
   - Ở menu bên trái, click "APIs & Services" > "Library"
   - Hoặc vào: https://console.cloud.google.com/apis/library

2. **Bật Google Sheets API:**
   - Tìm kiếm: `Google Sheets API`
   - Click vào "Google Sheets API"
   - Click nút "ENABLE" (Bật)

3. **Bật Google Drive API:**
   - Quay lại Library (click "APIs & Services" > "Library")
   - Tìm kiếm: `Google Drive API`
   - Click vào "Google Drive API"
   - Click nút "ENABLE" (Bật)

---

## 📋 BƯỚC 3: TẠO SERVICE ACCOUNT

1. **Vào Credentials:**
   - Ở menu bên trái, click "APIs & Services" > "Credentials"
   - Hoặc vào: https://console.cloud.google.com/apis/credentials

2. **Tạo Service Account:**
   - Click nút "CREATE CREDENTIALS" ở đầu trang
   - Chọn "Service account"
   - Điền thông tin:
     - **Service account name:** `so-thu-chi-salon` (hoặc tên khác)
     - **Service account ID:** Tự động điền (có thể giữ nguyên)
   - Click "CREATE AND CONTINUE"

3. **Bỏ qua bước Grant access (tùy chọn):**
   - Click "CONTINUE" để bỏ qua
   - Click "DONE"

4. **Tạo Key (Credentials):**
   - Bạn sẽ thấy Service Account vừa tạo trong danh sách
   - Click vào Service Account đó (click vào email)
   - Vào tab "KEYS" ở trên
   - Click "ADD KEY" > "Create new key"
   - Chọn "JSON"
   - Click "CREATE"
   - File JSON sẽ tự động tải về máy

**⚠️ QUAN TRỌNG:** Lưu file JSON này cẩn thận! Đây là "chìa khóa" để app có thể truy cập Google Sheets.

---

## 📋 BƯỚC 4: LẤY EMAIL CỦA SERVICE ACCOUNT

1. **Mở file JSON vừa tải:**
   - Tìm file JSON trong thư mục Downloads (hoặc nơi bạn lưu)
   - Mở bằng Notepad/TextEdit hoặc bất kỳ trình soạn thảo nào

2. **Tìm email:**
   - Trong file JSON, tìm dòng có `"client_email"`
   - Copy email đó (ví dụ: `so-thu-chi-salon@project-123456.iam.gserviceaccount.com`)
   - Email này có dạng: `tên-service-account@tên-project.iam.gserviceaccount.com`

**Ví dụ:**
```json
{
  "type": "service_account",
  "project_id": "my-project",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "so-thu-chi@my-project.iam.gserviceaccount.com",  ← EMAIL NÀY
  ...
}
```

---

## 📋 BƯỚC 5: SHARE GOOGLE SHEET VỚI SERVICE ACCOUNT

1. **Mở Google Sheet của bạn:**
   - Vào: https://docs.google.com/spreadsheets/d/1PpA-w8fsLrLq7EkfOqZo4B6Itlz0ned79sLah0ETfAQ/edit
   - Hoặc mở sheet bất kỳ bạn muốn dùng

2. **Share với Service Account:**
   - Click nút "Share" (Chia sẻ) ở góc trên bên phải
   - Dán email của Service Account (đã copy ở bước 4)
   - Chọn quyền: **"Editor"** (Chỉnh sửa)
   - **BỎ TICK** "Notify people" (không cần gửi thông báo)
   - Click "Share" hoặc "Send"

**✅ Xong!** Service Account giờ đã có quyền chỉnh sửa Google Sheet của bạn.

---

## 📋 BƯỚC 6: SỬ DỤNG TRONG APP

1. **Mở app Streamlit:**
   - Chạy app như bình thường
   - Vào trang "☁️ Google Sheets"

2. **Upload Credentials:**
   - Click "Browse files" hoặc kéo thả file JSON vào
   - File JSON sẽ được upload
   - App sẽ hiển thị email của Service Account
   - **Kiểm tra:** Email này phải khớp với email bạn đã share Google Sheet

3. **Nhập Google Sheet URL:**
   - Copy URL của Google Sheet
   - Dán vào ô "Google Sheet URL"
   - URL có dạng: `https://docs.google.com/spreadsheets/d/...`

4. **Xuất dữ liệu:**
   - Click nút "📤 Xuất lên Google Sheets"
   - Đợi vài giây
   - Nếu thành công, sẽ có thông báo "✅ Đã xuất dữ liệu lên Google Sheets thành công!"

5. **Kiểm tra:**
   - Mở Google Sheet
   - Bạn sẽ thấy các sheet mới: "Tổng hợp", "Thu", "Chi", "Tất cả"
   - Dữ liệu đã được cập nhật!

---

## 🔄 XUẤT LẠI DỮ LIỆU

Mỗi lần bạn:
- Nhập giao dịch mới
- Chỉnh sửa giao dịch
- Xóa giao dịch

Bạn có thể vào trang "☁️ Google Sheets" và click "📤 Xuất lên Google Sheets" để cập nhật lại.

**💡 Tip:** Bạn có thể setup một lần, sau đó chỉ cần upload credentials và nhập URL lại mỗi lần muốn cập nhật.

---

## ❌ XỬ LÝ LỖI

### Lỗi: "Permission denied" hoặc "Access denied"
- **Nguyên nhân:** Chưa share Google Sheet với Service Account email
- **Giải pháp:** Làm lại Bước 5, đảm bảo share với đúng email

### Lỗi: "API not enabled"
- **Nguyên nhân:** Chưa bật Google Sheets API hoặc Drive API
- **Giải pháp:** Làm lại Bước 2

### Lỗi: "Invalid credentials"
- **Nguyên nhân:** File JSON không đúng hoặc đã bị thay đổi
- **Giải pháp:** Tải lại file JSON từ Google Cloud Console (Bước 3)

### Lỗi: "Sheet not found"
- **Nguyên nhân:** URL Google Sheet không đúng
- **Giải pháp:** Copy lại URL từ thanh địa chỉ trình duyệt

---

## 📸 VỀ HÌNH ẢNH

Hình ảnh trong Google Sheets:
- App sẽ hiển thị tên file hình ảnh
- Để xem hình, bạn cần:
  1. Upload hình lên Google Drive
  2. Share hình với quyền "Anyone with the link can view"
  3. Copy link hình
  4. Cập nhật link vào cột "Hình ảnh" trong Google Sheet

Hoặc bạn có thể:
- Tạo một sheet riêng để lưu link hình ảnh
- Link hình từ Google Drive vào Google Sheet

---

## ✅ CHECKLIST

Trước khi sử dụng, đảm bảo bạn đã:
- [ ] Tạo Google Cloud Project
- [ ] Bật Google Sheets API
- [ ] Bật Google Drive API
- [ ] Tạo Service Account
- [ ] Tải file JSON credentials
- [ ] Copy email của Service Account
- [ ] Share Google Sheet với Service Account email (quyền Editor)
- [ ] Cài đặt thư viện: `pip install gspread google-auth`
- [ ] Upload credentials vào app
- [ ] Nhập Google Sheet URL
- [ ] Click "Xuất lên Google Sheets"

---

## 🆘 CẦN GIÚP ĐỠ?

Nếu gặp lỗi, hãy:
1. Kiểm tra lại từng bước trên
2. Xem thông báo lỗi trong app
3. Kiểm tra email Service Account đã được share chưa
4. Đảm bảo đã bật đủ 2 APIs (Sheets và Drive)

**Chúc bạn thành công! 🎉**

