#!/bin/bash
echo "🚀 Đang khởi động ứng dụng Sổ Thu Chi Salon..."
echo "📡 Chế độ mạng nội bộ - Nhân viên có thể truy cập từ các máy khác"
echo ""
cd "$(dirname "$0")"

# Lấy địa chỉ IP
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$IP" ]; then
    IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")
fi

echo "🌐 Địa chỉ IP: $IP"
echo "📱 Nhân viên truy cập tại: http://$IP:8501"
echo ""
echo "Nhấn Ctrl+C để dừng ứng dụng"
echo ""

streamlit run app.py --server.address 0.0.0.0 --server.port 8501

