#!/bin/bash

echo "🚀 Thiết lập Git và chuẩn bị deploy..."
echo ""

# Kiểm tra git đã cài chưa
if ! command -v git &> /dev/null; then
    echo "❌ Git chưa được cài đặt. Vui lòng cài đặt Git trước."
    exit 1
fi

# Khởi tạo git nếu chưa có
if [ ! -d ".git" ]; then
    echo "📦 Khởi tạo Git repository..."
    git init
    echo "✅ Đã khởi tạo Git"
else
    echo "✅ Git đã được khởi tạo"
fi

# Thêm file vào git
echo "📝 Thêm file vào Git..."
git add .

# Kiểm tra có thay đổi không
if git diff --staged --quiet; then
    echo "⚠️  Không có thay đổi để commit"
else
    echo "💾 Tạo commit..."
    git commit -m "Initial commit - So Thu Chi Salon"
    echo "✅ Đã commit"
fi

echo ""
echo "📋 Bước tiếp theo:"
echo "1. Tạo repository trên GitHub: https://github.com/new"
echo "2. Chạy lệnh sau (thay TEN_USER và TEN_REPO):"
echo ""
echo "   git remote add origin https://github.com/TEN_USER/TEN_REPO.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy lên Streamlit Cloud: https://share.streamlit.io"
echo ""
echo "📖 Xem chi tiết trong file DEPLOY.md"

