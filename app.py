import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import os
from pathlib import Path
import shutil

# Google Sheets (optional)
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

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
STAFF_FILE = DATA_DIR / "staff.json"
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

# Quản lý nhân viên
def init_staff():
    if not STAFF_FILE.exists():
        with open(STAFF_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_staff():
    init_staff()
    with open(STAFF_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_staff(staff_list):
    with open(STAFF_FILE, 'w', encoding='utf-8') as f:
        json.dump(staff_list, f, ensure_ascii=False, indent=2)

def add_staff(name):
    staff_list = load_staff()
    name = name.strip()
    if name and name not in staff_list:
        staff_list.append(name)
        staff_list.sort()  # Sắp xếp theo thứ tự ABC
        save_staff(staff_list)
        return True
    return False

def delete_staff(name):
    staff_list = load_staff()
    if name in staff_list:
        staff_list.remove(name)
        save_staff(staff_list)
        return True
    return False

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
        chi_df['boss_order'] = ''
    if 'image_path' not in chi_df.columns:
        chi_df['image_path'] = ''
    
    thu_columns = ['date', 'category', 'amount', 'invoice_count', 'staff_name', 'description', 'payment_method', 'created_at']
    thu_export = thu_df[thu_columns].copy()
    thu_export.columns = ['Ngày', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Ghi chú', 'Phương thức', 'Thời gian tạo']
    thu_export['Ngày'] = thu_export['Ngày'].dt.strftime('%d/%m/%Y')
    thu_export['Số tiền'] = thu_export['Số tiền'].astype(int)
    thu_export['Số HĐ'] = thu_export['Số HĐ'].astype(int)
    
    chi_columns = ['date', 'category', 'amount', 'purchase_item', 'staff_name', 'boss_order', 'description', 'payment_method', 'image_path', 'created_at']
    chi_export = chi_df[chi_columns].copy()
    chi_export.columns = ['Ngày', 'Danh mục', 'Số tiền', 'Chi mua gì', 'Nhân viên', 'Lệnh sếp', 'Ghi chú', 'Phương thức', 'Hình ảnh', 'Thời gian tạo']
    chi_export['Ngày'] = chi_export['Ngày'].dt.strftime('%d/%m/%Y')
    chi_export['Số tiền'] = chi_export['Số tiền'].astype(int)
    # Lệnh sếp giờ là text, không cần convert
    # Hiển thị đường dẫn ảnh hoặc tên file
    chi_export['Hình ảnh'] = chi_export['Hình ảnh'].apply(lambda x: x if x and str(x).strip() else "Không có")
    
    # Tạo file Excel với nhiều sheet
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet Tổng hợp
        if 'invoice_count' not in thu_df.columns:
            thu_df['invoice_count'] = 0
        
        # Tính số hóa đơn riêng cho từng loại
        hoa_don_dich_vu = int(thu_df[thu_df['category'] == 'Doanh thu dịch vụ']['invoice_count'].sum()) if not thu_df.empty else 0
        hoa_don_san_pham = int(thu_df[thu_df['category'] == 'Doanh thu sản phẩm']['invoice_count'].sum()) if not thu_df.empty else 0
        tong_hoa_don = hoa_don_dich_vu + hoa_don_san_pham
        
        summary_data = {
            'Loại': ['Tổng Thu', 'Tổng Chi', 'Số dư', 'HĐ Dịch vụ', 'HĐ Sản phẩm', 'Tổng HĐ'],
            'Số tiền': [
                int(thu_df['amount'].sum()),
                int(chi_df['amount'].sum()),
                int(thu_df['amount'].sum() - chi_df['amount'].sum()),
                hoa_don_dich_vu,
                hoa_don_san_pham,
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
            df['boss_order'] = ''
        if 'image_path' not in df.columns:
            df['image_path'] = ''
        
        all_columns = ['date', 'type', 'category', 'amount', 'invoice_count', 'staff_name', 'purchase_item', 'boss_order', 'description', 'payment_method', 'image_path', 'created_at']
        all_export = df[all_columns].copy()
        all_export.columns = ['Ngày', 'Loại', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Chi mua gì', 'Lệnh sếp', 'Ghi chú', 'Phương thức', 'Hình ảnh', 'Thời gian tạo']
        all_export['Ngày'] = all_export['Ngày'].dt.strftime('%d/%m/%Y')
        all_export['Loại'] = all_export['Loại'].apply(lambda x: "Thu" if x == "thu" else "Chi")
        all_export['Số tiền'] = all_export['Số tiền'].astype(int)
        all_export['Số HĐ'] = all_export['Số HĐ'].astype(int)
        # Lệnh sếp giờ là text, không cần convert
        # Hiển thị đường dẫn ảnh hoặc tên file
        all_export['Hình ảnh'] = all_export['Hình ảnh'].apply(lambda x: x if x and str(x).strip() else "Không có")
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

# Xuất lên Google Sheets
def export_to_google_sheets(transactions, sheet_url=None, credentials_file=None):
    """
    Xuất dữ liệu lên Google Sheets
    Cần: 
    - Google Sheet URL (share với service account email)
    - Service account JSON credentials file
    """
    if not GOOGLE_SHEETS_AVAILABLE:
        raise Exception("Thư viện gspread chưa được cài đặt. Chạy: pip install gspread google-auth")
    
    if not transactions:
        raise Exception("Không có dữ liệu để xuất")
    
    if not sheet_url:
        raise Exception("Vui lòng cung cấp Google Sheet URL")
    
    if not credentials_file:
        raise Exception("Vui lòng cung cấp đường dẫn đến file credentials JSON")
    
    # Đọc credentials
    if not os.path.exists(credentials_file):
        raise Exception(f"Không tìm thấy file credentials: {credentials_file}")
    
    try:
        # Authenticate
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        client = gspread.authorize(creds)
        
        # Mở Google Sheet
        sheet = client.open_by_url(sheet_url)
        
        # Chuẩn bị dữ liệu
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Tách các loại giao dịch
        thu_df = df[df['type'] == 'thu'].copy()
        chi_df = df[df['type'] == 'chi'].copy()
        tip_df = df[df['type'] == 'tip'].copy()
        chi_ho_df = df[df['type'] == 'chi_ho'].copy()
        
        # Kiểm tra và thêm các cột mới nếu chưa có
        if 'invoice_count' not in thu_df.columns:
            thu_df['invoice_count'] = 0
        if 'staff_name' not in thu_df.columns:
            thu_df['staff_name'] = ''
        if 'staff_name' not in chi_df.columns:
            chi_df['staff_name'] = ''
        if 'purchase_item' not in chi_df.columns:
            chi_df['purchase_item'] = ''
        if 'boss_order' not in chi_df.columns:
            chi_df['boss_order'] = ''
        if 'image_path' not in chi_df.columns:
            chi_df['image_path'] = ''
        
        # Sheet 1: Tổng hợp
        try:
            worksheet = sheet.worksheet("Tổng hợp")
        except:
            worksheet = sheet.add_worksheet(title="Tổng hợp", rows=100, cols=10)
        
        hoa_don_dich_vu = int(thu_df[thu_df['category'] == 'Doanh thu dịch vụ']['invoice_count'].sum()) if not thu_df.empty else 0
        hoa_don_san_pham = int(thu_df[thu_df['category'] == 'Doanh thu sản phẩm']['invoice_count'].sum()) if not thu_df.empty else 0
        tong_hoa_don = hoa_don_dich_vu + hoa_don_san_pham
        
        summary_data = [
            ['Loại', 'Số tiền'],
            ['Tổng Thu', int(thu_df['amount'].sum())],
            ['Tổng Chi', int(chi_df['amount'].sum())],
            ['Số dư', int(thu_df['amount'].sum() - chi_df['amount'].sum())],
            ['HĐ Dịch vụ', hoa_don_dich_vu],
            ['HĐ Sản phẩm', hoa_don_san_pham],
            ['Tổng HĐ', tong_hoa_don]
        ]
        worksheet.clear()
        worksheet.update('A1', summary_data)
        
        # Sheet 2: Thu
        try:
            worksheet = sheet.worksheet("Thu")
        except:
            worksheet = sheet.add_worksheet(title="Thu", rows=1000, cols=10)
        
        thu_columns = ['date', 'category', 'amount', 'invoice_count', 'staff_name', 'description', 'payment_method', 'created_at']
        thu_export = thu_df[thu_columns].copy()
        thu_export['date'] = thu_export['date'].dt.strftime('%d/%m/%Y')
        thu_export['amount'] = thu_export['amount'].astype(int)
        thu_export['invoice_count'] = thu_export['invoice_count'].astype(int)
        
        headers = ['Ngày', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Ghi chú', 'Phương thức', 'Thời gian tạo']
        data = [headers] + thu_export.values.tolist()
        worksheet.clear()
        if data:
            worksheet.update('A1', data)
        
        # Sheet 3: Chi
        try:
            worksheet = sheet.worksheet("Chi")
        except:
            worksheet = sheet.add_worksheet(title="Chi", rows=1000, cols=10)
        
        chi_columns = ['date', 'category', 'amount', 'purchase_item', 'staff_name', 'boss_order', 'description', 'payment_method', 'image_path', 'created_at']
        chi_export = chi_df[chi_columns].copy()
        chi_export['date'] = chi_export['date'].dt.strftime('%d/%m/%Y')
        chi_export['amount'] = chi_export['amount'].astype(int)
        
        # Xử lý hình ảnh - tạo link nếu có
        def format_image_path(img_path):
            if not img_path or str(img_path).strip() == '':
                return "Không có"
            # Nếu là đường dẫn local, chỉ hiển thị tên file
            # Người dùng có thể upload lên Google Drive và cập nhật link sau
            if isinstance(img_path, str) and ('images/' in img_path or 'data/images/' in img_path):
                filename = img_path.split('/')[-1] if '/' in img_path else img_path
                return f"📷 {filename} (cần upload lên Drive)"
            return str(img_path)
        
        chi_export['image_path'] = chi_export['image_path'].apply(format_image_path)
        
        headers = ['Ngày', 'Danh mục', 'Số tiền', 'Chi mua gì', 'Nhân viên', 'Lệnh sếp', 'Ghi chú', 'Phương thức', 'Hình ảnh', 'Thời gian tạo']
        data = [headers] + chi_export.values.tolist()
        worksheet.clear()
        if data:
            worksheet.update('A1', data)
        
        # Sheet 4: Tất cả
        try:
            worksheet = sheet.worksheet("Tất cả")
        except:
            worksheet = sheet.add_worksheet(title="Tất cả", rows=1000, cols=15)
        
        all_columns = ['date', 'type', 'category', 'amount', 'invoice_count', 'staff_name', 'purchase_item', 'boss_order', 'description', 'payment_method', 'image_path', 'created_at']
        all_export = df[all_columns].copy()
        all_export['date'] = all_export['date'].dt.strftime('%d/%m/%Y')
        all_export['type'] = all_export['type'].apply(lambda x: "Thu" if x == "thu" else "Chi" if x == "chi" else "TIP" if x == "tip" else "CHI HỘ")
        all_export['amount'] = all_export['amount'].astype(int)
        all_export['invoice_count'] = all_export['invoice_count'].astype(int)
        all_export['image_path'] = all_export['image_path'].apply(lambda x: x if x and str(x).strip() else "Không có")
        
        headers = ['Ngày', 'Loại', 'Danh mục', 'Số tiền', 'Số HĐ', 'Nhân viên', 'Chi mua gì', 'Lệnh sếp', 'Ghi chú', 'Phương thức', 'Hình ảnh', 'Thời gian tạo']
        data = [headers] + all_export.values.tolist()
        worksheet.clear()
        if data:
            worksheet.update('A1', data)
        
        return True
        
    except Exception as e:
        raise Exception(f"Lỗi khi xuất lên Google Sheets: {str(e)}")

# Main App
def main():
    st.title("💰 SỔ THU CHI SALON")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Chọn trang",
        ["📝 Nhập liệu", "📊 Tổng kết", "📋 Xem dữ liệu", "✏️ Chỉnh sửa/Xóa", "☁️ Google Sheets", "👥 Quản lý nhân viên"]
    )
    
    if page == "📝 Nhập liệu":
        input_page()
    elif page == "📊 Tổng kết":
        summary_page()
    elif page == "📋 Xem dữ liệu":
        view_data_page()
    elif page == "✏️ Chỉnh sửa/Xóa":
        edit_delete_page()
    elif page == "☁️ Google Sheets":
        google_sheets_page()
    elif page == "👥 Quản lý nhân viên":
        manage_staff_page()

def input_page():
    st.header("📝 Nhập liệu hàng ngày")
    
    # Khởi tạo session state để reset form
    if 'form_reset_key' not in st.session_state:
        st.session_state.form_reset_key = 0
    if 'last_transaction_type' not in st.session_state:
        st.session_state.last_transaction_type = "💰 Thu"
    
    # Chọn loại giao dịch (giữ nguyên khi reset form)
    try:
        default_index = SPECIAL_TRANSACTION_TYPES.index(st.session_state.last_transaction_type) if st.session_state.last_transaction_type in SPECIAL_TRANSACTION_TYPES else 0
    except:
        default_index = 0
    
    transaction_type = st.radio(
        "Loại giao dịch",
        SPECIAL_TRANSACTION_TYPES,
        horizontal=True,
        key="transaction_type_main",
        index=default_index
    )
    st.session_state.last_transaction_type = transaction_type
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Form nhập liệu với key để reset
        form_key = st.session_state.form_reset_key
        
        if transaction_type == "💰 Thu":
            category = st.selectbox("Danh mục", INCOME_CATEGORIES, key=f"category_{form_key}")
            payment_method = st.selectbox("Phương thức thanh toán", PAYMENT_METHODS, key=f"payment_{form_key}")
            
            # Chỉ hiển thị số lượng hóa đơn cho "Doanh thu dịch vụ" và "Doanh thu sản phẩm"
            # Với "Công nợ" và "Khác" không cần nhập số lượng hóa đơn (tự động = 0)
            if category in ["Doanh thu dịch vụ", "Doanh thu sản phẩm"]:
                invoice_count = st.number_input(
                    "Số lượng hóa đơn (Số khách)",
                    min_value=0,
                    step=1,
                    format="%d",
                    value=1,
                    help="1 hóa đơn = 1 khách",
                    key=f"invoice_{form_key}"
                )
            else:
                # Với "Công nợ" và "Khác", không hiển thị trường này và tự động = 0
                invoice_count = 0
                st.info("ℹ️ Danh mục này không tính số lượng hóa đơn (tự động = 0)")
            
            purchase_item = ""
            boss_order = ""
            uploaded_image = None
        elif transaction_type == "💸 Chi":
            category = st.text_input("Danh mục (tự điền)", placeholder="Nhập danh mục chi tiêu...", key=f"category_{form_key}")
            payment_method = st.selectbox("Phương thức thanh toán", PAYMENT_METHODS, key=f"payment_{form_key}")
            invoice_count = 0
            purchase_item = st.text_input("Chi mua gì?", placeholder="Nhập món hàng/dịch vụ...", key=f"purchase_{form_key}")
            boss_order = st.text_input("Lệnh từ sếp/bộ phận", placeholder="Nhập tên sếp hoặc bộ phận yêu cầu...", 
                                      help="Nhập tên sếp hoặc bộ phận yêu cầu mua hàng (tùy chọn)", key=f"boss_{form_key}")
            uploaded_image = st.file_uploader(
                "Hình chụp (tùy chọn)",
                type=['png', 'jpg', 'jpeg'],
                help="Upload hình ảnh liên quan đến khoản chi",
                key=f"image_{form_key}"
            )
        elif transaction_type == "💵 TIP":
            category = "TIP"
            payment_method = ""  # TIP không có phương thức thanh toán
            invoice_count = 0
            purchase_item = ""
            boss_order = ""
            uploaded_image = None
        elif transaction_type == "🏦 CHI HỘ":
            category = "CHI HỘ"
            payment_method = ""  # CHI HỘ không có phương thức thanh toán
            invoice_count = 0
            purchase_item = ""
            boss_order = ""
            uploaded_image = None
        
        amount = st.number_input(
            "Số tiền (VNĐ)",
            min_value=0,
            step=1000,
            format="%d",
            key=f"amount_{form_key}"
        )
        
        # Nhân viên (bắt buộc cho tất cả) - Chọn từ danh sách hoặc thêm mới
        staff_list = load_staff()
        staff_options = ["➕ Thêm nhân viên mới..."] + staff_list
        
        selected_staff_option = st.selectbox(
            "Nhân viên *",
            staff_options,
            help="Chọn nhân viên từ danh sách hoặc thêm mới",
            key=f"staff_select_{form_key}"
        )
        
        # Nếu chọn "Thêm nhân viên mới..."
        if selected_staff_option == "➕ Thêm nhân viên mới...":
            new_staff_name = st.text_input(
                "Nhập tên nhân viên mới",
                placeholder="Nhập tên nhân viên...",
                key=f"new_staff_{form_key}"
            )
            # Nếu có nút "Thêm" riêng (sẽ xử lý ở trang quản lý)
            # Ở đây chỉ lấy giá trị để dùng khi lưu giao dịch
            staff_name = new_staff_name.strip() if new_staff_name else ""
        else:
            staff_name = selected_staff_option
        
        # NỢ (chỉ cho Thu - Công nợ)
        debt_amount = 0
        if transaction_type == "💰 Thu" and category == "Công nợ":
            debt_amount = st.number_input(
                "Số tiền nợ (VNĐ)",
                min_value=0,
                step=1000,
                format="%d",
                help="Số tiền khách nợ",
                key=f"debt_{form_key}"
            )
        
        description = st.text_input("Ghi chú (tùy chọn)", key=f"desc_{form_key}")
        
        transaction_date = st.date_input(
            "Ngày",
            value=date.today(),
            key=f"date_{form_key}"
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
        elif not staff_name or not staff_name.strip():
            st.error("⚠️ Vui lòng chọn hoặc nhập tên nhân viên")
        elif transaction_type == "💸 Chi" and not category.strip():
            st.error("⚠️ Vui lòng nhập danh mục chi tiêu")
        elif transaction_type == "💸 Chi" and not purchase_item.strip():
            st.error("⚠️ Vui lòng nhập thông tin 'Chi mua gì?'")
        else:
            # Nếu nhân viên mới được nhập (chọn "Thêm nhân viên mới..."), tự động thêm vào danh sách
            if selected_staff_option == "➕ Thêm nhân viên mới..." and staff_name and staff_name.strip():
                add_staff(staff_name.strip())  # Tự động thêm vào danh sách nếu chưa có
            
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
                "boss_order": boss_order.strip() if transaction_type == "💸 Chi" and boss_order else "",
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
            
            # Reset form bằng cách tăng counter
            st.session_state.form_reset_key += 1
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
        chi_df['boss_order'] = ''
    if 'image_path' not in chi_df.columns:
        chi_df['image_path'] = ''
    
    tong_thu = thu_df['amount'].sum()
    tong_chi = chi_df['amount'].sum()
    so_du = tong_thu - tong_chi
    
    # Tính số hóa đơn riêng cho từng loại
    hoa_don_dich_vu = int(thu_df[thu_df['category'] == 'Doanh thu dịch vụ']['invoice_count'].sum()) if not thu_df.empty else 0
    hoa_don_san_pham = int(thu_df[thu_df['category'] == 'Doanh thu sản phẩm']['invoice_count'].sum()) if not thu_df.empty else 0
    tong_hoa_don = hoa_don_dich_vu + hoa_don_san_pham
    
    # Hiển thị tổng kết
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Tổng Thu", f"{format_currency(tong_thu)} VNĐ")
    
    with col2:
        st.metric("💸 Tổng Chi", f"{format_currency(tong_chi)} VNĐ")
    
    with col3:
        st.metric("💵 Số dư", f"{format_currency(so_du)} VNĐ", 
                 delta=f"{format_currency(so_du)} VNĐ" if so_du >= 0 else None)
    
    st.divider()
    
    # Hiển thị số hóa đơn chi tiết
    st.subheader("📋 Số lượng hóa đơn")
    col_hd1, col_hd2, col_hd3 = st.columns(3)
    
    with col_hd1:
        st.metric("🛍️ HĐ Dịch vụ", f"{hoa_don_dich_vu} hóa đơn")
    
    with col_hd2:
        st.metric("📦 HĐ Sản phẩm", f"{hoa_don_san_pham} hóa đơn")
    
    with col_hd3:
        st.metric("📋 Tổng HĐ", f"{tong_hoa_don} hóa đơn")
    
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
        
        # Tổng kết số HĐ theo danh mục
        st.info(f"📊 **Tổng hợp:** HĐ Dịch vụ: {hoa_don_dich_vu} | HĐ Sản phẩm: {hoa_don_san_pham} | Tổng: {tong_hoa_don}")
        
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
        # Lệnh sếp giờ là text, hiển thị trực tiếp
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
        df_filtered['boss_order'] = ''
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
    # Lệnh sếp giờ là text, hiển thị trực tiếp
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
        # Tính số hóa đơn riêng
        hoa_don_dich_vu = int(thu_filtered[thu_filtered['category'] == 'Doanh thu dịch vụ']['invoice_count'].sum()) if not thu_filtered.empty else 0
        hoa_don_san_pham = int(thu_filtered[thu_filtered['category'] == 'Doanh thu sản phẩm']['invoice_count'].sum()) if not thu_filtered.empty else 0
        tong_hoa_don = hoa_don_dich_vu + hoa_don_san_pham
        st.metric("📋 Tổng HĐ", f"{int(tong_hoa_don)} hóa đơn")
        st.caption(f"DV: {hoa_don_dich_vu} | SP: {hoa_don_san_pham}")
    
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

def edit_delete_page():
    st.header("✏️ Chỉnh sửa/Xóa giao dịch")
    
    transactions = load_transactions()
    
    if not transactions:
        st.info("Chưa có dữ liệu.")
        return
    
    # Chọn giao dịch để chỉnh sửa/xóa
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Tạo danh sách để chọn
    transaction_options = []
    for idx, row in df.iterrows():
        trans_id = row.get('id', idx)
        trans_type = "💰 Thu" if row['type'] == 'thu' else "💸 Chi" if row['type'] == 'chi' else "💵 TIP" if row['type'] == 'tip' else "🏦 CHI HỘ"
        date_str = row['date'].strftime('%d/%m/%Y')
        amount = format_currency(row['amount'])
        category = row.get('category', '')
        display_text = f"ID {trans_id} - {trans_type} - {date_str} - {amount} VNĐ - {category}"
        transaction_options.append((trans_id, display_text))
    
    if not transaction_options:
        st.info("Chưa có giao dịch nào.")
        return
    
    # Chọn giao dịch
    selected_option = st.selectbox(
        "Chọn giao dịch cần chỉnh sửa/xóa",
        options=[opt[1] for opt in transaction_options],
        key="select_transaction"
    )
    
    # Tìm giao dịch được chọn
    selected_id = None
    for trans_id, display_text in transaction_options:
        if display_text == selected_option:
            selected_id = trans_id
            break
    
    if selected_id is None:
        return
    
    # Tìm giao dịch trong danh sách
    selected_transaction = None
    for trans in transactions:
        if trans.get('id') == selected_id:
            selected_transaction = trans
            break
    
    if not selected_transaction:
        st.error("Không tìm thấy giao dịch.")
        return
    
    st.divider()
    
    # Hiển thị thông tin hiện tại
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Chỉnh sửa giao dịch")
        
        # Xác định loại giao dịch
        trans_type = selected_transaction.get('type', 'thu')
        if trans_type == 'thu':
            display_type = "💰 Thu"
        elif trans_type == 'chi':
            display_type = "💸 Chi"
        elif trans_type == 'tip':
            display_type = "💵 TIP"
        elif trans_type == 'chi_ho':
            display_type = "🏦 CHI HỘ"
        else:
            display_type = "💰 Thu"
        
        # Hiển thị thông tin cơ bản
        current_date = pd.to_datetime(selected_transaction.get('date', date.today())).strftime('%d/%m/%Y')
        current_amount = format_currency(selected_transaction.get('amount', 0))
        st.info(f"**Loại:** {display_type} | **Ngày hiện tại:** {current_date} | **Số tiền:** {current_amount} VNĐ")
        
        # Ngày - đặt ở đầu để dễ thấy
        st.markdown("### 📅 Chỉnh sửa ngày")
        transaction_date = st.date_input(
            "Ngày giao dịch",
            value=pd.to_datetime(selected_transaction.get('date', date.today())).date(),
            help="Nếu ghi nhầm ngày, hãy chọn lại ngày đúng ở đây",
            key="edit_date"
        )
        
        st.divider()
        st.markdown("### ✏️ Chỉnh sửa thông tin khác")
        
        # Form chỉnh sửa
        if trans_type == 'thu':
            category = st.selectbox(
                "Danh mục",
                INCOME_CATEGORIES,
                index=INCOME_CATEGORIES.index(selected_transaction.get('category', 'Doanh thu dịch vụ')) if selected_transaction.get('category') in INCOME_CATEGORIES else 0,
                key="edit_category"
            )
            payment_method = st.selectbox(
                "Phương thức thanh toán",
                PAYMENT_METHODS,
                index=PAYMENT_METHODS.index(selected_transaction.get('payment_method', 'Tiền mặt')) if selected_transaction.get('payment_method') in PAYMENT_METHODS else 0,
                key="edit_payment"
            )
            
            if category in ["Doanh thu dịch vụ", "Doanh thu sản phẩm"]:
                invoice_count = st.number_input(
                    "Số lượng hóa đơn",
                    min_value=0,
                    step=1,
                    format="%d",
                    value=int(selected_transaction.get('invoice_count', 0)),
                    key="edit_invoice"
                )
            else:
                invoice_count = 0
                st.info("ℹ️ Danh mục này không tính số lượng hóa đơn")
            
            purchase_item = ""
            boss_order = ""
            
            if category == "Công nợ":
                debt_amount = st.number_input(
                    "Số tiền nợ (VNĐ)",
                    min_value=0,
                    step=1000,
                    format="%d",
                    value=int(selected_transaction.get('debt_amount', 0)),
                    key="edit_debt"
                )
            else:
                debt_amount = 0
        elif trans_type == 'chi':
            category = st.text_input(
                "Danh mục",
                value=selected_transaction.get('category', ''),
                key="edit_category"
            )
            payment_method = st.selectbox(
                "Phương thức thanh toán",
                PAYMENT_METHODS,
                index=PAYMENT_METHODS.index(selected_transaction.get('payment_method', 'Tiền mặt')) if selected_transaction.get('payment_method') in PAYMENT_METHODS else 0,
                key="edit_payment"
            )
            invoice_count = 0
            purchase_item = st.text_input(
                "Chi mua gì?",
                value=selected_transaction.get('purchase_item', ''),
                key="edit_purchase"
            )
            boss_order = st.text_input(
                "Lệnh từ sếp/bộ phận",
                value=selected_transaction.get('boss_order', ''),
                key="edit_boss"
            )
            debt_amount = 0
        else:  # TIP hoặc CHI HỘ
            category = selected_transaction.get('category', '')
            payment_method = ""
            invoice_count = 0
            purchase_item = ""
            boss_order = ""
            debt_amount = 0
        
        amount = st.number_input(
            "Số tiền (VNĐ)",
            min_value=0,
            step=1000,
            format="%d",
            value=int(selected_transaction.get('amount', 0)),
            key="edit_amount"
        )
        
        # Nhân viên
        staff_list = load_staff()
        current_staff = selected_transaction.get('staff_name', '')
        if current_staff and current_staff not in staff_list:
            staff_list.append(current_staff)
            staff_list.sort()
        
        staff_options = staff_list if staff_list else []
        if current_staff and current_staff not in staff_options:
            staff_options = [current_staff] + staff_options
        
        if staff_options:
            try:
                staff_index = staff_options.index(current_staff) if current_staff in staff_options else 0
            except:
                staff_index = 0
            staff_name = st.selectbox(
                "Nhân viên",
                staff_options,
                index=staff_index,
                key="edit_staff"
            )
        else:
            staff_name = st.text_input(
                "Nhân viên",
                value=current_staff,
                key="edit_staff"
            )
        
        description = st.text_input(
            "Ghi chú",
            value=selected_transaction.get('description', ''),
            key="edit_description"
        )
        
        st.divider()
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("💾 Lưu thay đổi", type="primary", use_container_width=True):
                # Validation
                if amount <= 0:
                    st.error("⚠️ Vui lòng nhập số tiền lớn hơn 0")
                elif not staff_name.strip():
                    st.error("⚠️ Vui lòng nhập tên nhân viên")
                elif trans_type == 'chi' and not category.strip():
                    st.error("⚠️ Vui lòng nhập danh mục chi tiêu")
                elif trans_type == 'chi' and not purchase_item.strip():
                    st.error("⚠️ Vui lòng nhập thông tin 'Chi mua gì?'")
                else:
                    # Cập nhật giao dịch
                    selected_transaction['category'] = category.strip() if category else category
                    selected_transaction['amount'] = amount
                    selected_transaction['description'] = description
                    selected_transaction['payment_method'] = payment_method if payment_method else ""
                    selected_transaction['invoice_count'] = invoice_count if trans_type == 'thu' else 0
                    selected_transaction['staff_name'] = staff_name.strip()
                    selected_transaction['purchase_item'] = purchase_item.strip() if purchase_item else ""
                    selected_transaction['boss_order'] = boss_order.strip() if trans_type == 'chi' and boss_order else ""
                    selected_transaction['debt_amount'] = debt_amount if trans_type == 'thu' and category == "Công nợ" else 0
                    selected_transaction['date'] = transaction_date.strftime("%Y-%m-%d")
                    selected_transaction['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Lưu lại
                    save_transactions(transactions)
                    
                    # Tự động xuất Excel
                    try:
                        excel_file = export_to_excel(transactions)
                        st.success(f"✅ Đã cập nhật giao dịch ID {selected_id} và xuất Excel")
                    except Exception as e:
                        st.success(f"✅ Đã cập nhật giao dịch ID {selected_id}")
                        st.warning(f"⚠️ Lưu Excel gặp lỗi: {str(e)}")
                    
                    st.rerun()
        
        with col_btn2:
            if st.button("🗑️ Xóa giao dịch", type="secondary", use_container_width=True):
                st.warning("⚠️ Bạn có chắc chắn muốn xóa giao dịch này?")
                if st.button("✅ Xác nhận xóa", type="primary", key="confirm_delete"):
                    transactions = [t for t in transactions if t.get('id') != selected_id]
                    save_transactions(transactions)
                    
                    # Tự động xuất Excel
                    try:
                        excel_file = export_to_excel(transactions)
                        st.success(f"✅ Đã xóa giao dịch ID {selected_id} và xuất Excel")
                    except Exception as e:
                        st.success(f"✅ Đã xóa giao dịch ID {selected_id}")
                        st.warning(f"⚠️ Lưu Excel gặp lỗi: {str(e)}")
                    
                    st.rerun()
    
    with col2:
        st.subheader("📋 Thông tin hiện tại")
        
        # Hiển thị thông tin dễ đọc hơn
        st.markdown("**ID:** " + str(selected_transaction.get('id', 'N/A')))
        st.markdown("**Loại:** " + display_type)
        st.markdown("**Ngày:** " + current_date)
        st.markdown("**Danh mục:** " + str(selected_transaction.get('category', '')))
        st.markdown("**Số tiền:** " + current_amount + " VNĐ")
        st.markdown("**Nhân viên:** " + str(selected_transaction.get('staff_name', '')))
        st.markdown("**Phương thức:** " + str(selected_transaction.get('payment_method', '')))
        if selected_transaction.get('invoice_count', 0) > 0:
            st.markdown("**Số HĐ:** " + str(int(selected_transaction.get('invoice_count', 0))))
        if selected_transaction.get('purchase_item'):
            st.markdown("**Chi mua gì:** " + str(selected_transaction.get('purchase_item', '')))
        if selected_transaction.get('boss_order'):
            st.markdown("**Lệnh sếp:** " + str(selected_transaction.get('boss_order', '')))
        if selected_transaction.get('description'):
            st.markdown("**Ghi chú:** " + str(selected_transaction.get('description', '')))
        if selected_transaction.get('debt_amount', 0) > 0:
            st.markdown("**Số tiền nợ:** " + format_currency(selected_transaction.get('debt_amount', 0)) + " VNĐ")
        
        st.divider()
        st.markdown("**Thời gian tạo:** " + str(selected_transaction.get('created_at', 'N/A')))
        if selected_transaction.get('updated_at'):
            st.markdown("**Cập nhật lần cuối:** " + str(selected_transaction.get('updated_at', 'N/A')))
        
        st.divider()
        with st.expander("📄 Xem dữ liệu JSON đầy đủ"):
            st.json(selected_transaction)

def google_sheets_page():
    st.header("☁️ Xuất dữ liệu lên Google Sheets")
    
    if not GOOGLE_SHEETS_AVAILABLE:
        st.warning("⚠️ Thư viện Google Sheets chưa được cài đặt.")
        st.info("""
        **Để sử dụng tính năng này, bạn cần:**
        
        1. Cài đặt thư viện:
        ```bash
        pip install gspread google-auth
        ```
        
        2. Tạo Google Service Account:
        - Vào https://console.cloud.google.com/
        - Tạo project mới (hoặc chọn project có sẵn)
        - Bật Google Sheets API và Google Drive API
        - Tạo Service Account và tải file JSON credentials
        
        3. Share Google Sheet với email của Service Account
        """)
        return
    
    transactions = load_transactions()
    
    if not transactions:
        st.info("Chưa có dữ liệu để xuất.")
        return
    
    st.info("""
    **Hướng dẫn sử dụng:**
    
    1. Tạo Google Sheet mới (hoặc dùng sheet có sẵn)
    2. Share sheet với email của Service Account (xem trong file credentials JSON, field "client_email")
    3. Copy URL của Google Sheet và dán vào ô bên dưới
    4. Upload file credentials JSON (service account key)
    5. Nhấn nút "📤 Xuất lên Google Sheets"
    """)
    
    st.divider()
    
    # Nhập Google Sheet URL
    sheet_url = st.text_input(
        "🔗 Google Sheet URL",
        placeholder="https://docs.google.com/spreadsheets/d/...",
        help="Copy URL từ Google Sheet và dán vào đây"
    )
    
    # Upload credentials file
    credentials_file = st.file_uploader(
        "🔑 Upload file Credentials JSON",
        type=['json'],
        help="Upload file service account credentials JSON"
    )
    
    # Lưu credentials file tạm thời
    credentials_path = None
    if credentials_file is not None:
        # Lưu file tạm
        credentials_dir = DATA_DIR / "credentials"
        credentials_dir.mkdir(exist_ok=True)
        credentials_path = credentials_dir / "google_credentials.json"
        
        with open(credentials_path, 'wb') as f:
            f.write(credentials_file.getbuffer())
        
        st.success(f"✅ Đã tải file credentials: {credentials_file.name}")
        
        # Hiển thị service account email
        try:
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
                service_email = creds_data.get('client_email', 'N/A')
                st.info(f"📧 **Service Account Email:** {service_email}\n\n⚠️ **Quan trọng:** Bạn phải share Google Sheet với email này!")
        except:
            st.warning("⚠️ Không thể đọc file credentials")
    
    st.divider()
    
    # Nút xuất
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("📤 Xuất lên Google Sheets", type="primary", use_container_width=True):
            if not sheet_url:
                st.error("⚠️ Vui lòng nhập Google Sheet URL")
            elif not credentials_path or not os.path.exists(credentials_path):
                st.error("⚠️ Vui lòng upload file credentials JSON")
            else:
                try:
                    with st.spinner("Đang xuất dữ liệu lên Google Sheets..."):
                        export_to_google_sheets(transactions, sheet_url, str(credentials_path))
                        st.success("✅ Đã xuất dữ liệu lên Google Sheets thành công!")
                        st.balloons()
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
                    st.info("""
                    **Các lỗi thường gặp:**
                    - Chưa share Google Sheet với Service Account email
                    - File credentials không đúng
                    - Google Sheet URL không hợp lệ
                    - Chưa bật Google Sheets API trong Google Cloud Console
                    """)
    
    with col2:
        st.write("")  # Spacing
    
    st.divider()
    
    # Thông tin thêm
    with st.expander("📖 Hướng dẫn chi tiết tạo Service Account"):
        st.markdown("""
        ### Bước 1: Tạo Google Cloud Project
        1. Vào https://console.cloud.google.com/
        2. Tạo project mới hoặc chọn project có sẵn
        
        ### Bước 2: Bật APIs
        1. Vào "APIs & Services" > "Library"
        2. Tìm và bật "Google Sheets API"
        3. Tìm và bật "Google Drive API"
        
        ### Bước 3: Tạo Service Account
        1. Vào "APIs & Services" > "Credentials"
        2. Click "Create Credentials" > "Service Account"
        3. Điền tên và tạo
        4. Click vào Service Account vừa tạo
        5. Vào tab "Keys" > "Add Key" > "Create new key"
        6. Chọn JSON và tải về
        
        ### Bước 4: Share Google Sheet
        1. Mở Google Sheet của bạn
        2. Click "Share" (Chia sẻ)
        3. Dán email của Service Account (tìm trong file JSON, field "client_email")
        4. Chọn quyền "Editor" (Chỉnh sửa)
        5. Click "Send"
        
        ### Bước 5: Sử dụng trong app
        1. Upload file JSON credentials vào app
        2. Dán URL của Google Sheet
        3. Click "Xuất lên Google Sheets"
        """)

def manage_staff_page():
    st.header("👥 Quản lý nhân viên")
    
    staff_list = load_staff()
    
    # Thêm nhân viên mới
    st.subheader("➕ Thêm nhân viên mới")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_staff_name = st.text_input(
            "Tên nhân viên",
            placeholder="Nhập tên nhân viên...",
            key="new_staff_input"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("➕ Thêm", type="primary", use_container_width=True):
            if new_staff_name and new_staff_name.strip():
                if add_staff(new_staff_name.strip()):
                    st.success(f"✅ Đã thêm nhân viên: {new_staff_name.strip()}")
                    st.rerun()
                else:
                    st.warning("⚠️ Nhân viên đã tồn tại hoặc tên không hợp lệ")
            else:
                st.warning("⚠️ Vui lòng nhập tên nhân viên")
    
    st.divider()
    
    # Danh sách nhân viên
    st.subheader(f"📋 Danh sách nhân viên ({len(staff_list)} người)")
    
    if not staff_list:
        st.info("Chưa có nhân viên nào. Hãy thêm nhân viên mới ở trên.")
    else:
        # Hiển thị danh sách với nút xóa
        for idx, staff_name in enumerate(staff_list):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{idx + 1}. {staff_name}**")
            with col2:
                if st.button("🗑️ Xóa", key=f"delete_{staff_name}", type="secondary"):
                    if delete_staff(staff_name):
                        st.success(f"✅ Đã xóa nhân viên: {staff_name}")
                        st.rerun()
        
        # Thống kê theo nhân viên
        st.divider()
        st.subheader("📊 Thống kê theo nhân viên")
        
        transactions = load_transactions()
        if transactions:
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            # Kiểm tra cột staff_name
            if 'staff_name' not in df.columns:
                df['staff_name'] = ''
            
            # Lọc dữ liệu có staff_name
            df_with_staff = df[df['staff_name'].notna() & (df['staff_name'] != '')]
            
            if not df_with_staff.empty:
                # Chọn nhân viên để xem thống kê
                selected_staff = st.selectbox(
                    "Chọn nhân viên để xem thống kê",
                    ["Tất cả"] + staff_list
                )
                
                if selected_staff != "Tất cả":
                    df_staff = df_with_staff[df_with_staff['staff_name'] == selected_staff]
                else:
                    df_staff = df_with_staff
                
                if not df_staff.empty:
                    # Thống kê tổng quan
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        thu_staff = df_staff[df_staff['type'] == 'thu']['amount'].sum()
                        st.metric("💰 Tổng Thu", f"{format_currency(thu_staff)} VNĐ")
                    
                    with col2:
                        chi_staff = df_staff[df_staff['type'] == 'chi']['amount'].sum()
                        st.metric("💸 Tổng Chi", f"{format_currency(chi_staff)} VNĐ")
                    
                    with col3:
                        tip_staff = df_staff[df_staff['type'] == 'tip']['amount'].sum()
                        st.metric("💵 Tổng TIP", f"{format_currency(tip_staff)} VNĐ")
                    
                    with col4:
                        chi_ho_staff = df_staff[df_staff['type'] == 'chi_ho']['amount'].sum()
                        st.metric("🏦 Tổng CHI HỘ", f"{format_currency(chi_ho_staff)} VNĐ")
                    
                    # Bảng chi tiết
                    if selected_staff == "Tất cả":
                        st.subheader("Chi tiết theo nhân viên")
                        staff_summary = df_staff.groupby('staff_name')['amount'].sum().reset_index()
                        staff_summary.columns = ['Nhân viên', 'Tổng tiền']
                        staff_summary['Tổng tiền'] = staff_summary['Tổng tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
                        staff_summary = staff_summary.sort_values('Nhân viên')
                        st.dataframe(staff_summary, use_container_width=True, hide_index=True)
                    else:
                        st.subheader(f"Chi tiết giao dịch của {selected_staff}")
                        display_columns = ['date', 'type', 'category', 'amount', 'description']
                        display_df = df_staff[display_columns].copy()
                        display_df.columns = ['Ngày', 'Loại', 'Danh mục', 'Số tiền', 'Ghi chú']
                        display_df['Ngày'] = display_df['Ngày'].dt.strftime('%d/%m/%Y')
                        display_df['Loại'] = display_df['Loại'].apply(
                            lambda x: "💰 Thu" if x == "thu" else "💸 Chi" if x == "chi" else "💵 TIP" if x == "tip" else "🏦 CHI HỘ"
                        )
                        display_df['Số tiền'] = display_df['Số tiền'].apply(lambda x: f"{format_currency(x)} VNĐ")
                        display_df = display_df.sort_values('Ngày', ascending=False)
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"Không có dữ liệu cho nhân viên: {selected_staff}")
            else:
                st.info("Chưa có dữ liệu giao dịch với thông tin nhân viên.")
        else:
            st.info("Chưa có dữ liệu giao dịch.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Lỗi khi khởi động app: {str(e)}")
        st.info("Vui lòng kiểm tra logs hoặc liên hệ hỗ trợ.")
        import traceback
        with st.expander("Chi tiết lỗi"):
            st.code(traceback.format_exc())

