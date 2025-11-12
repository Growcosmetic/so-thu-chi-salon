import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import os
from pathlib import Path
import shutil

# Cấu hình trang
st.set_page_config(
    page_title="Sổ Thu Chi Salon",
    page_icon="💰",
    layout="wide"
)

# Đường dẫn file lưu trữ
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
EXCEL_DIR = DATA_DIR / "excel"
EXCEL_DIR.mkdir(exist_ok=True)
IMAGES_DIR = DATA_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Khởi tạo dữ liệu nếu chưa có
def init_data():
    if not TRANSACTIONS_FILE.exists():
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

# Đọc dữ liệu
def load_transactions():
    init_data()
    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Lưu dữ liệu
def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)

# Danh mục chi tiêu
EXPENSE_CATEGORIES = [
    "Đồ ăn",
    "Đồ dùng salon",
    "Nước uống",
    "Ship/Giao hàng",
    "Nạp điện thoại",
    "Giữ xe",
    "Sửa chữa",
    "Khác"
]

# Danh mục thu nhập
INCOME_CATEGORIES = [
    "Doanh thu dịch vụ",
    "Doanh thu sản phẩm",
    "Công nợ",
    "Khác"
]

# Phương thức thanh toán
PAYMENT_METHODS = [
    "Tiền mặt",
    "Chuyển khoản",
    "Quẹt thẻ"
]

# Loại giao dịch đặc biệt
SPECIAL_TRANSACTION_TYPES = [
    "💰 Thu",
    "💸 Chi",
    "💵 TIP",
    "🏦 CHI HỘ"
]

# Format số tiền
def format_currency(amount):
    return f"{amount:,.0f}".replace(",", ".")

# Xuất ra Excel
def export_to_excel(transactions, filename=None):
    if not transactions:
        return None
    
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    # Tạo tên file nếu chưa có
    if filename is None:
        # Tạo file tổng hợp duy nhất, luôn cập nhật
        filename = EXCEL_DIR / "so_thu_chi.xlsx"
    else:
        filename = EXCEL_DIR / filename
    
    # Tách các loại giao dịch
    thu_df = df[df['type'] == 'thu'].copy()
    chi_df = df[df['type'] == 'chi'].copy()
    tip_df = df[df['type'] == 'tip'].copy()
    chi_ho_df = df[df['type'] == 'chi_ho'].copy()
    
    # Chuẩn bị dữ liệu cho Excel
    # Kiểm tra và thêm các cột mới nếu chưa có (cho dữ liệu cũ)
    if 'invoice_count' not in thu_df.columns:
        thu_df['invoice_count'] = 0
    if 'staff_name' not in thu_df.columns:
        thu_df['staff_name'] = ''
    if 'staff_name' not in chi_df.columns:
        chi_df['staff_name'] = ''
    if 'purchase_item' not in chi_df.columns:
        chi_df['purchase_item'] = ''
    if 'boss_order' not in chi_df.columns:
        chi_df['boss_order'] = False
    if 'image_path' not in chi_df.columns:
        chi_df['image_path'] = ''
    
    thu_columns = ['date', 'category', 'amount', 'invoice_count', 'staff_name', 'description', 'payment_method', 'created_at']
    thu_export = thu_df[thu_columns].copy()
    thu_export.columns = ['Ngày', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Ghi chú', 'Phương thức', 'Thời gian tạo']
    thu_export['Ngày'] = thu_export['Ngày'].dt.strftime('%d/%m/%Y')
    thu_export['Số tiền'] = thu_export['Số tiền'].astype(int)
    thu_export['Số HĐ'] = thu_export['Số HĐ'].astype(int)
    
    chi_columns = ['date', 'category', 'amount', 'purchase_item', 'staff_name', 'boss_order', 'description', 'payment_method', 'created_at']
    chi_export = chi_df[chi_columns].copy()
    chi_export.columns = ['Ngày', 'Danh mục', 'Số tiền', 'Chi mua gì', 'Nhân viên', 'Lệnh sếp', 'Ghi chú', 'Phương thức', 'Thời gian tạo']
    chi_export['Ngày'] = chi_export['Ngày'].dt.strftime('%d/%m/%Y')
    chi_export['Số tiền'] = chi_export['Số tiền'].astype(int)
    chi_export['Lệnh sếp'] = chi_export['Lệnh sếp'].apply(lambda x: "Có" if x else "Không")
    
    # Tạo file Excel với nhiều sheet
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet Tổng hợp
        if 'invoice_count' not in thu_df.columns:
            thu_df['invoice_count'] = 0
        tong_hoa_don = int(thu_df['invoice_count'].sum()) if not thu_df.empty else 0
        
        summary_data = {
            'Loại': ['Tổng Thu', 'Tổng Chi', 'Số dư', 'Tổng HĐ'],
            'Số tiền': [
                int(thu_df['amount'].sum()),
                int(chi_df['amount'].sum()),
                int(thu_df['amount'].sum() - chi_df['amount'].sum()),
                tong_hoa_don
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Tổng hợp', index=False)
        
        # Sheet Thu
        if not thu_export.empty:
            thu_export.to_excel(writer, sheet_name='Thu', index=False)
            
            # Tổng theo phương thức thanh toán
            if 'payment_method' in thu_df.columns:
                payment_summary = thu_df.groupby('payment_method')['amount'].sum().reset_index()
                payment_summary.columns = ['Phương thức', 'Tổng tiền']
                payment_summary['Tổng tiền'] = payment_summary['Tổng tiền'].astype(int)
                payment_summary.to_excel(writer, sheet_name='Thu theo PT', index=False)
        else:
            pd.DataFrame({'Thông báo': ['Chưa có dữ liệu thu']}).to_excel(writer, sheet_name='Thu', index=False)
        
        # Sheet Chi
        if not chi_export.empty:
            chi_export.to_excel(writer, sheet_name='Chi', index=False)
            
            # Tổng theo danh mục
            category_summary = chi_df.groupby('category')['amount'].sum().reset_index()
            category_summary.columns = ['Danh mục', 'Tổng tiền']
            category_summary['Tổng tiền'] = category_summary['Tổng tiền'].astype(int)
            category_summary.to_excel(writer, sheet_name='Chi theo DM', index=False)
            
            # Tổng theo phương thức thanh toán
            if 'payment_method' in chi_df.columns:
                payment_summary = chi_df.groupby('payment_method')['amount'].sum().reset_index()
                payment_summary.columns = ['Phương thức', 'Tổng tiền']
                payment_summary['Tổng tiền'] = payment_summary['Tổng tiền'].astype(int)
                payment_summary.to_excel(writer, sheet_name='Chi theo PT', index=False)
        else:
            pd.DataFrame({'Thông báo': ['Chưa có dữ liệu chi']}).to_excel(writer, sheet_name='Chi', index=False)
        
        # Sheet Tất cả
        if 'invoice_count' not in df.columns:
            df['invoice_count'] = 0
        if 'staff_name' not in df.columns:
            df['staff_name'] = ''
        if 'purchase_item' not in df.columns:
            df['purchase_item'] = ''
        if 'boss_order' not in df.columns:
            df['boss_order'] = False
        if 'image_path' not in df.columns:
            df['image_path'] = ''
        
        all_columns = ['date', 'type', 'category', 'amount', 'invoice_count', 'staff_name', 'purchase_item', 'boss_order', 'description', 'payment_method', 'created_at']
        all_export = df[all_columns].copy()
        all_export.columns = ['Ngày', 'Loại', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Chi mua gì', 'Lệnh sếp', 'Ghi chú', 'Phương thức', 'Thời gian tạo']
        all_export['Ngày'] = all_export['Ngày'].dt.strftime('%d/%m/%Y')
        all_export['Loại'] = all_export['Loại'].apply(lambda x: "Thu" if x == "thu" else "Chi")
        all_export['Số tiền'] = all_export['Số tiền'].astype(int)
        all_export['Số HĐ'] = all_export['Số HĐ'].astype(int)
        all_export['Lệnh sếp'] = all_export['Lệnh sếp'].apply(lambda x: "Có" if x else "Không")
        all_export.to_excel(writer, sheet_name='Tất cả', index=False)
        
        # Sheet theo format Excel (Chuyển khoản, Quẹt thẻ, Chi, Thu, TIP, CHI HỘ, NỢ)
        excel_format_data = []
        
        # Thêm dữ liệu Thu (theo phương thức thanh toán)
        for idx, row in thu_df.iterrows():
            if 'payment_method' in row and row['payment_method']:
                if row['payment_method'] == 'Chuyển khoản':
                    excel_format_data.append({
                        'Chuyển khoản': int(row['amount']),
                        'QT': '',
                        'CHI': '',
                        'Nội dung chi': '',
                        'THU': '',
                        'Nội dung thu': row.get('description', '') or row.get('category', ''),
                        'TIP': '',
                        'Nội dung TIP': '',
                        'CHI HỘ': '',
                        'Nội dung CHI HỘ': '',
                        'NỢ': ''
                    })
                elif row['payment_method'] == 'Quẹt thẻ':
                    excel_format_data.append({
                        'Chuyển khoản': '',
                        'QT': int(row['amount']),
                        'CHI': '',
                        'Nội dung chi': '',
                        'THU': '',
                        'Nội dung thu': row.get('description', '') or row.get('category', ''),
                        'TIP': '',
                        'Nội dung (NV)': '',
                        'CHI HỘ': '',
                        'Nội dung (NV)': '',
                        'NỢ': ''
                    })
                else:  # Tiền mặt
                    excel_format_data.append({
                        'Chuyển khoản': '',
                        'QT': '',
                        'CHI': '',
                        'Nội dung chi': '',
                        'THU': int(row['amount']),
                        'Nội dung thu': row.get('description', '') or row.get('category', ''),
                        'TIP': '',
                        'Nội dung (NV)': '',
                        'CHI HỘ': '',
                        'Nội dung (NV)': '',
                        'NỢ': ''
                    })
            else:
                excel_format_data.append({
                    'Chuyển khoản': '',
                    'QT': '',
                    'CHI': '',
                    'Nội dung chi': '',
                    'THU': int(row['amount']),
                    'Nội dung thu': row.get('description', '') or row.get('category', ''),
                    'TIP': '',
                    'Nội dung (NV)': '',
                    'CHI HỘ': '',
                    'Nội dung (NV)': '',
                    'NỢ': ''
                })
            
            # Thêm NỢ nếu có
            if 'debt_amount' in row and row.get('debt_amount', 0) > 0:
                excel_format_data[-1]['NỢ'] = int(row['debt_amount'])
        
        # Thêm dữ liệu Chi
        for idx, row in chi_df.iterrows():
            payment = row.get('payment_method', '')
            if payment == 'Chuyển khoản':
                excel_format_data.append({
                    'Chuyển khoản': int(row['amount']),
                    'QT': '',
                    'CHI': '',
                    'Nội dung chi': row.get('purchase_item', '') or row.get('category', ''),
                    'THU': '',
                    'Nội dung thu': '',
                    'TIP': '',
                    'Nội dung (NV)': '',
                    'CHI HỘ': '',
                    'Nội dung (NV)': '',
                    'NỢ': ''
                })
            elif payment == 'Quẹt thẻ':
                excel_format_data.append({
                    'Chuyển khoản': '',
                    'QT': int(row['amount']),
                    'CHI': '',
                    'Nội dung chi': row.get('purchase_item', '') or row.get('category', ''),
                    'THU': '',
                    'Nội dung thu': '',
                    'TIP': '',
                    'Nội dung (NV)': '',
                    'CHI HỘ': '',
                    'Nội dung (NV)': '',
                    'NỢ': ''
                })
            else:  # Tiền mặt
                excel_format_data.append({
                    'Chuyển khoản': '',
                    'QT': '',
                    'CHI': int(row['amount']),
                    'Nội dung chi': row.get('purchase_item', '') or row.get('category', ''),
                    'THU': '',
                    'Nội dung thu': '',
                    'TIP': '',
                    'Nội dung (NV)': '',
                    'CHI HỘ': '',
                    'Nội dung (NV)': '',
                    'NỢ': ''
                })
        
        # Thêm dữ liệu TIP
        for idx, row in tip_df.iterrows():
            excel_format_data.append({
                'Chuyển khoản': '',
                'QT': '',
                'CHI': '',
                'Nội dung chi': '',
                'THU': '',
                'Nội dung thu': '',
                'TIP': int(row['amount']),
                'Nội dung TIP': row.get('staff_name', ''),
                'CHI HỘ': '',
                'Nội dung CHI HỘ': '',
                'NỢ': ''
            })
        
        # Thêm dữ liệu CHI HỘ
        for idx, row in chi_ho_df.iterrows():
            excel_format_data.append({
                'Chuyển khoản': '',
                'QT': '',
                'CHI': '',
                'Nội dung chi': '',
                'THU': '',
                'Nội dung thu': '',
                'TIP': '',
                'Nội dung TIP': '',
                'CHI HỘ': int(row['amount']),
                'Nội dung CHI HỘ': row.get('staff_name', ''),
                'NỢ': ''
            })
        
        # Tạo DataFrame và xuất
        if excel_format_data:
            excel_format_df = pd.DataFrame(excel_format_data)
            excel_format_df.to_excel(writer, sheet_name='Theo Format Excel', index=False)
        else:
            pd.DataFrame({
                'Chuyển khoản': [''], 'QT': [''], 'CHI': [''], 'Nội dung chi': [''], 
                'THU': [''], 'Nội dung thu': [''], 'TIP': [''], 'Nội dung TIP': [''], 
                'CHI HỘ': [''], 'Nội dung CHI HỘ': [''], 'NỢ': ['']
            }).to_excel(writer, sheet_name='Theo Format Excel', index=False)
    
    return filename

# Main App
def main():
    st.title("💰 SỔ THU CHI SALON")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Chọn trang",
        ["📝 Nhập liệu", "📊 Tổng kết", "📋 Xem dữ liệu"]
    )
    
    if page == "📝 Nhập liệu":
        input_page()
    elif page == "📊 Tổng kết":
        summary_page()
    elif page == "📋 Xem dữ liệu":
        view_data_page()

def input_page():
    st.header("📝 Nhập liệu hàng ngày")
    
    # Chọn loại giao dịch
    transaction_type = st.radio(
        "Loại giao dịch",
        SPECIAL_TRANSACTION_TYPES,
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Form nhập liệu
        if transaction_type == "💰 Thu":
            category = st.selectbox("Danh mục", INCOME_CATEGORIES)
            payment_method = st.selectbox("Phương thức thanh toán", PAYMENT_METHODS)
            invoice_count = st.number_input(
                "Số lượng hóa đơn (Số khách)",
                min_value=0,
                step=1,
                format="%d",
                value=1,
                help="1 hóa đơn = 1 khách"
            )
            purchase_item = ""
            boss_order = False
            uploaded_image = None
        elif transaction_type == "💸 Chi":
            category = st.text_input("Danh mục (tự điền)", placeholder="Nhập danh mục chi tiêu...")
            payment_method = st.selectbox("Phương thức thanh toán", PAYMENT_METHODS)
            invoice_count = 0
            purchase_item = st.text_input("Chi mua gì?", placeholder="Nhập món hàng/dịch vụ...")
            boss_order = st.checkbox("Lệnh từ sếp", help="Đánh dấu nếu khoản chi theo lệnh của sếp")
            uploaded_image = st.file_uploader(
                "Hình chụp (tùy chọn)",
                type=['png', 'jpg', 'jpeg'],
                help="Upload hình ảnh liên quan đến khoản chi"
            )
        elif transaction_type == "💵 TIP":
            category = "TIP"
            payment_method = ""  # TIP không có phương thức thanh toán
            invoice_count = 0
            purchase_item = ""
            boss_order = False
            uploaded_image = None
        elif transaction_type == "🏦 CHI HỘ":
            category = "CHI HỘ"
            payment_method = ""  # CHI HỘ không có phương thức thanh toán
            invoice_count = 0
            purchase_item = ""
            boss_order = False
            uploaded_image = None
        
        amount = st.number_input(
            "Số tiền (VNĐ)",
            min_value=0,
            step=1000,
            format="%d"
        )
        
        # Nhân viên (bắt buộc cho tất cả)
        staff_name = st.text_input("Nhân viên", placeholder="Nhập tên nhân viên...", 
                                   help="Tên nhân viên nhận tip hoặc được ứng tiền")
        
        # NỢ (chỉ cho Thu - Công nợ)
        debt_amount = 0
        if transaction_type == "💰 Thu" and category == "Công nợ":
            debt_amount = st.number_input(
                "Số tiền nợ (VNĐ)",
                min_value=0,
                step=1000,
                format="%d",
                help="Số tiền khách nợ"
            )
        
        description = st.text_input("Ghi chú (tùy chọn)")
        
        transaction_date = st.date_input(
            "Ngày",
            value=date.today()
        )
    
    with col2:
        if transaction_type == "💰 Thu":
            st.info("""
            **THU (Thu nhập):**
            - Chọn danh mục và phương thức thanh toán
            - Nhập số tiền và số hóa đơn
            - Nhập tên nhân viên thực hiện
            """)
        elif transaction_type == "💸 Chi":
            st.info("""
            **CHI (Chi tiêu):**
            - Nhập danh mục và chi mua gì
            - Chọn phương thức thanh toán
            - Nhập tên nhân viên thực hiện
            - Upload hình ảnh nếu có
            """)
        elif transaction_type == "💵 TIP":
            st.info("""
            **TIP (Tiền tip và salon nợ nhân viên):**
            - Nhập số tiền tip hoặc số tiền salon nợ
            - Nhập tên nhân viên
            - Ghi chú (tùy chọn)
            """)
        elif transaction_type == "🏦 CHI HỘ":
            st.info("""
            **CHI HỘ (Salon ứng cho nhân viên):**
            - Nhập số tiền ứng
            - Nhập tên nhân viên được ứng
            - Ghi chú (tùy chọn)
            """)
    
    # Nút lưu
    if st.button("💾 Lưu giao dịch", type="primary", use_container_width=True):
        # Validation
        if amount <= 0:
            st.error("⚠️ Vui lòng nhập số tiền lớn hơn 0")
        elif not staff_name.strip():
            st.error("⚠️ Vui lòng nhập tên nhân viên")
        elif transaction_type == "💸 Chi" and not category.strip():
            st.error("⚠️ Vui lòng nhập danh mục chi tiêu")
        elif transaction_type == "💸 Chi" and not purchase_item.strip():
            st.error("⚠️ Vui lòng nhập thông tin 'Chi mua gì?'")
        else:
            transactions = load_transactions()
            
            # Xử lý upload ảnh
            image_path = ""
            if uploaded_image is not None:
                # Tạo tên file duy nhất
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                file_extension = Path(uploaded_image.name).suffix
                image_filename = f"{timestamp}{file_extension}"
                image_path = str(IMAGES_DIR / image_filename)
                
                # Lưu ảnh
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
                
                # Lưu đường dẫn tương đối
                image_path = f"images/{image_filename}"
            
            # Xác định type cho database
            if transaction_type == "💰 Thu":
                db_type = "thu"
            elif transaction_type == "💸 Chi":
                db_type = "chi"
            elif transaction_type == "💵 TIP":
                db_type = "tip"
            elif transaction_type == "🏦 CHI HỘ":
                db_type = "chi_ho"
            else:
                db_type = "thu"
            
            new_transaction = {
                "id": len(transactions) + 1,
                "type": db_type,
                "category": category.strip() if category else category,
                "amount": amount,
                "description": description,
                "payment_method": payment_method if payment_method else "",
                "invoice_count": invoice_count if transaction_type == "💰 Thu" else 0,
                "staff_name": staff_name.strip(),
                "purchase_item": purchase_item.strip() if purchase_item else "",
                "boss_order": boss_order if transaction_type == "💸 Chi" else False,
                "image_path": image_path,
                "debt_amount": debt_amount if transaction_type == "💰 Thu" and category == "Công nợ" else 0,
                "date": transaction_date.strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            transactions.append(new_transaction)
            save_transactions(transactions)
            
            # Tự động xuất Excel
            try:
                excel_file = export_to_excel(transactions)
                st.success(f"✅ Đã lưu {transaction_type} {format_currency(amount)} VNĐ và xuất Excel")
            except Exception as e:
                st.success(f"✅ Đã lưu {transaction_type} {format_currency(amount)} VNĐ")
                st.warning(f"⚠️ Lưu Excel gặp lỗi: {str(e)}")
            
            st.rerun()

def summary_page():
    st.header("📊 Tổng kết")
    
    transactions = load_transactions()
    
    if not transactions:
        st.info("Chưa có dữ liệu. Vui lòng nhập liệu trước.")
        return
    
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    # Chọn ngày
    selected_date = st.date_input(
        "Chọn ngày để xem tổng kết",
        value=date.today()
    )
    
    # Lọc theo ngày
    df_date = df[df['date'].dt.date == selected_date]
    
    if df_date.empty:
        st.warning(f"Không có dữ liệu cho ngày {selected_date.strftime('%d/%m/%Y')}")
        return
    
    # Tính toán
    thu_df = df_date[df_date['type'] == 'thu'].copy()
    chi_df = df_date[df_date['type'] == 'chi'].copy()
    
    # Kiểm tra và thêm các cột mới nếu chưa có (cho dữ liệu cũ)
    if 'invoice_count' not in thu_df.columns:
        thu_df['invoice_count'] = 0
    if 'staff_name' not in thu_df.columns:
        thu_df['staff_name'] = ''
    if 'staff_name' not in chi_df.columns:
        chi_df['staff_name'] = ''
    if 'purchase_item' not in chi_df.columns:
        chi_df['purchase_item'] = ''
    if 'boss_order' not in chi_df.columns:
        chi_df['boss_order'] = False
    if 'image_path' not in chi_df.columns:
        chi_df['image_path'] = ''
    
    tong_thu = thu_df['amount'].sum()
    tong_chi = chi_df['amount'].sum()
    so_du = tong_thu - tong_chi
    tong_hoa_don = thu_df['invoice_count'].sum() if not thu_df.empty else 0
    
    # Hiển thị tổng kết
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Tổng Thu", f"{format_currency(tong_thu)} VNĐ")
    
    with col2:
        st.metric("💸 Tổng Chi", f"{format_currency(tong_chi)} VNĐ")
    
    with col3:
        st.metric("💵 Số dư", f"{format_currency(so_du)} VNĐ", 
                 delta=f"{format_currency(so_du)} VNĐ" if so_du >= 0 else None)
    
    with col4:
        st.metric("📋 Tổng HĐ", f"{int(tong_hoa_don)} hóa đơn")
    
    st.divider()
    
    # Chi tiết thu nhập
    if not thu_df.empty:
        st.subheader("💰 Chi tiết Thu nhập")
        
        # Tổng theo phương thức thanh toán
        if 'payment_method' in thu_df.columns:
            payment_summary = thu_df.groupby('payment_method')['amount'].sum().reset_index()
            payment_summary.columns = ['Phương thức', 'Tổng tiền']
            payment_summary['Tổng tiền'] = payment_summary['Tổng tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
            st.dataframe(payment_summary, use_container_width=True, hide_index=True)
        
        # Bảng chi tiết
        thu_detail = thu_df[['category', 'amount', 'invoice_count', 'staff_name', 'description', 'payment_method']].copy()
        thu_detail.columns = ['Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Ghi chú', 'Phương thức']
        thu_detail['Số tiền'] = thu_detail['Số tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
        thu_detail['Số HĐ'] = thu_detail['Số HĐ'].astype(int)
        st.dataframe(thu_detail, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Chi tiết chi tiêu
    if not chi_df.empty:
        st.subheader("💸 Chi tiết Chi tiêu")
        
        # Tổng theo danh mục
        category_summary = chi_df.groupby('category')['amount'].sum().reset_index()
        category_summary.columns = ['Danh mục', 'Tổng tiền']
        category_summary['Tổng tiền'] = category_summary['Tổng tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
        st.dataframe(category_summary, use_container_width=True, hide_index=True)
        
        # Bảng chi tiết
        chi_detail = chi_df[['category', 'amount', 'purchase_item', 'staff_name', 'boss_order', 'description', 'payment_method']].copy()
        chi_detail.columns = ['Danh mục', 'Số tiền', 'Chi mua gì', 'Nhân viên', 'Lệnh sếp', 'Ghi chú', 'Phương thức']
        chi_detail['Số tiền'] = chi_detail['Số tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
        chi_detail['Lệnh sếp'] = chi_detail['Lệnh sếp'].apply(lambda x: "✅ Có" if x else "❌ Không")
        st.dataframe(chi_detail, use_container_width=True, hide_index=True)
        
        # Hiển thị ảnh nếu có
        chi_with_images = chi_df[chi_df['image_path'].notna() & (chi_df['image_path'] != '')]
        if not chi_with_images.empty:
            st.subheader("📷 Hình ảnh đính kèm")
            for idx, row in chi_with_images.iterrows():
                image_file = DATA_DIR / row['image_path']
                if image_file.exists():
                    col_img1, col_img2 = st.columns([1, 3])
                    with col_img1:
                        st.image(str(image_file), width=200, caption=f"{row['category']} - {format_currency(row['amount'])} VNĐ")
                    with col_img2:
                        st.write(f"**Danh mục:** {row['category']}")
                        st.write(f"**Số tiền:** {format_currency(row['amount'])} VNĐ")
                        st.write(f"**Chi mua gì:** {row['purchase_item']}")
                        st.write(f"**Nhân viên:** {row['staff_name']}")
                        if row.get('description'):
                            st.write(f"**Ghi chú:** {row['description']}")
                    st.divider()
        
        # Tổng theo phương thức thanh toán
        if 'payment_method' in chi_df.columns:
            payment_summary = chi_df.groupby('payment_method')['amount'].sum().reset_index()
            payment_summary.columns = ['Phương thức', 'Tổng tiền']
            payment_summary['Tổng tiền'] = payment_summary['Tổng tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
            st.dataframe(payment_summary, use_container_width=True, hide_index=True)
    
    # Nút xuất Excel
    st.divider()
    if st.button("📥 Xuất Excel", type="primary", use_container_width=True):
        all_transactions = load_transactions()
        if all_transactions:
            try:
                excel_file = export_to_excel(all_transactions)
                st.success(f"✅ Đã xuất Excel: {excel_file.name}")
                
                # Đọc file và tạo download button
                with open(excel_file, 'rb') as f:
                    st.download_button(
                        label="⬇️ Tải file Excel",
                        data=f.read(),
                        file_name=excel_file.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"❌ Lỗi khi xuất Excel: {str(e)}")
        else:
            st.warning("Chưa có dữ liệu để xuất Excel")

def view_data_page():
    st.header("📋 Xem dữ liệu")
    
    transactions = load_transactions()
    
    if not transactions:
        st.info("Chưa có dữ liệu.")
        return
    
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    # Bộ lọc
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Chọn khoảng thời gian",
            value=(df['date'].min().date(), df['date'].max().date())
        )
    
    with col2:
        filter_type = st.selectbox("Loại", ["Tất cả", "Thu", "Chi"])
    
    with col3:
        if st.button("🔍 Lọc dữ liệu"):
            st.rerun()
    
    # Lọc dữ liệu
    if isinstance(date_range, tuple) and len(date_range) == 2:
        df_filtered = df[
            (df['date'].dt.date >= date_range[0]) &
            (df['date'].dt.date <= date_range[1])
        ]
    else:
        df_filtered = df
    
    if filter_type != "Tất cả":
        df_filtered = df_filtered[df_filtered['type'] == filter_type.lower()]
    
    # Kiểm tra và thêm các cột mới nếu chưa có (cho dữ liệu cũ)
    if 'invoice_count' not in df_filtered.columns:
        df_filtered['invoice_count'] = 0
    if 'staff_name' not in df_filtered.columns:
        df_filtered['staff_name'] = ''
    if 'purchase_item' not in df_filtered.columns:
        df_filtered['purchase_item'] = ''
    if 'boss_order' not in df_filtered.columns:
        df_filtered['boss_order'] = False
    if 'image_path' not in df_filtered.columns:
        df_filtered['image_path'] = ''
    
    # Hiển thị bảng
    display_columns = ['date', 'type', 'category', 'amount', 'invoice_count', 'staff_name', 'purchase_item', 'boss_order', 'description', 'payment_method']
    display_df = df_filtered[display_columns].copy()
    display_df.columns = ['Ngày', 'Loại', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Chi mua gì', 'Lệnh sếp', 'Ghi chú', 'Phương thức']
    display_df['Ngày'] = display_df['Ngày'].dt.strftime('%d/%m/%Y')
    display_df['Loại'] = display_df['Loại'].apply(lambda x: "💰 Thu" if x == "thu" else "💸 Chi")
    display_df['Số tiền'] = display_df['Số tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
    display_df['Số HĐ'] = display_df['Số HĐ'].astype(int)
    display_df['Lệnh sếp'] = display_df['Lệnh sếp'].apply(lambda x: "✅" if x else "")
    # Ẩn cột Số HĐ và Chi mua gì nếu là Chi (vì Chi không có hóa đơn, và Chi mua gì chỉ hiển thị cho Chi)
    display_df.loc[display_df['Loại'] == '💸 Chi', 'Số HĐ'] = ''
    display_df.loc[display_df['Loại'] == '💰 Thu', 'Chi mua gì'] = ''
    display_df.loc[display_df['Loại'] == '💰 Thu', 'Lệnh sếp'] = ''
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Tổng kết
    st.subheader("Tổng kết")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tong_thu = df_filtered[df_filtered['type'] == 'thu']['amount'].sum()
        st.metric("💰 Tổng Thu", f"{format_currency(tong_thu)} VNĐ")
    
    with col2:
        tong_chi = df_filtered[df_filtered['type'] == 'chi']['amount'].sum()
        st.metric("💸 Tổng Chi", f"{format_currency(tong_chi)} VNĐ")
    
    with col3:
        thu_filtered = df_filtered[df_filtered['type'] == 'thu']
        if 'invoice_count' not in thu_filtered.columns:
            thu_filtered['invoice_count'] = 0
        tong_hoa_don = thu_filtered['invoice_count'].sum() if not thu_filtered.empty else 0
        st.metric("📋 Tổng HĐ", f"{int(tong_hoa_don)} hóa đơn")
    
    # Nút xuất Excel
    st.divider()
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if st.button("📥 Xuất Excel (Tất cả)", type="primary", use_container_width=True):
            all_transactions = load_transactions()
            if all_transactions:
                try:
                    excel_file = export_to_excel(all_transactions)
                    st.success(f"✅ Đã xuất Excel: {excel_file.name}")
                    
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="⬇️ Tải file Excel",
                            data=f.read(),
                            file_name=excel_file.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"❌ Lỗi khi xuất Excel: {str(e)}")
            else:
                st.warning("Chưa có dữ liệu để xuất Excel")
    
    with col_export2:
        if st.button("📥 Xuất Excel (Đã lọc)", type="secondary", use_container_width=True):
            if not df_filtered.empty:
                try:
                    # Chuyển DataFrame đã lọc về dạng transactions
                    filtered_transactions = df_filtered.to_dict('records')
                    excel_file = export_to_excel(filtered_transactions, f"so_thu_chi_loc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
                    st.success(f"✅ Đã xuất Excel: {excel_file.name}")
                    
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="⬇️ Tải file Excel",
                            data=f.read(),
                            file_name=excel_file.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"❌ Lỗi khi xuất Excel: {str(e)}")
            else:
                st.warning("Không có dữ liệu sau khi lọc")
    
    # Nút xóa dữ liệu (cẩn thận)
    st.divider()
    if st.button("🗑️ Xóa tất cả dữ liệu", type="secondary"):
        if st.checkbox("Tôi chắc chắn muốn xóa tất cả dữ liệu"):
            save_transactions([])
            st.success("Đã xóa tất cả dữ liệu")
            st.rerun()

if __name__ == "__main__":
    main()

