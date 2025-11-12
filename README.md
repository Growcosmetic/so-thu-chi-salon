# 💰 SỔ THU CHI SALON

Ứng dụng quản lý thu chi hàng ngày cho salon, đơn giản và dễ sử dụng.

## 🚀 Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## 📱 Chạy ứng dụng

### Chạy local (chỉ máy này):
```bash
streamlit run app.py
```
Hoặc double-click vào `start.sh` (macOS/Linux) hoặc `start.bat` (Windows)

### Chạy cho mạng nội bộ (nhân viên truy cập được):
```bash
./start_network.sh
```
Hoặc:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Ứng dụng sẽ mở tự động trong trình duyệt tại `http://localhost:8501`

**Lưu ý**: Xem file `HUONG_DAN.md` để biết cách deploy lên cloud hoặc chia sẻ cho nhân viên.

## ✨ Tính năng

### 📝 Nhập liệu
- Nhập nhanh các giao dịch Thu/Chi hàng ngày
- Chọn danh mục phù hợp
- Ghi chú tùy chọn
- Hỗ trợ nhiều phương thức thanh toán (Tiền mặt, Chuyển khoản, VNPay, Quẹt thẻ...)

### 📊 Tổng kết
- Xem tổng kết theo ngày
- Tổng thu, tổng chi, số dư
- Chi tiết theo phương thức thanh toán
- Chi tiết theo danh mục

### 📋 Xem dữ liệu
- Xem tất cả giao dịch
- Lọc theo khoảng thời gian
- Lọc theo loại (Thu/Chi)
- Tổng kết theo bộ lọc

## 💾 Lưu trữ

Dữ liệu được lưu trong thư mục `data/transactions.json`

## 📝 Danh mục mặc định

**Chi tiêu:**
- Đồ ăn
- Đồ dùng salon
- Nước uống
- Ship/Giao hàng
- Nạp điện thoại
- Giữ xe
- Sửa chữa
- Khác

**Thu nhập:**
- Doanh thu dịch vụ
- Doanh thu sản phẩm
- Khác

**Phương thức thanh toán:**
- Tiền mặt
- Chuyển khoản
- VNPay
- Quẹt thẻ ACB
- Quẹt thẻ BIDV
- Khách nợ

