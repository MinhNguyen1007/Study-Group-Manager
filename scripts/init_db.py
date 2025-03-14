import os
import sys
from werkzeug.security import generate_password_hash

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database

def init_database():
    # Tạo thư mục data nếu chưa tồn tại
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db_file = os.path.join(data_dir, 'tasks.db')
    
    # Hỏi người dùng nếu muốn tạo mới database
    if os.path.exists(db_file):
        response = input("Database đã tồn tại. Bạn có muốn tạo mới không? (y/n): ")
        if response.lower() == 'y':
            os.remove(db_file)
            print("Đã xóa database cũ.")
        else:
            print("Giữ nguyên database cũ.")
            return

    # Khởi tạo database
    db = Database()
    
    # Tạo hoặc cập nhật tài khoản admin
    admin_password = generate_password_hash('admin')
    admin_user = db.get_user_by_username('admin')
    
    if admin_user:
        # Nếu tài khoản admin đã tồn tại, cập nhật lại mật khẩu và quyền
        db.reset_user_password(admin_user['id'], admin_password)
        db.update_user_status(admin_user['id'], 'active')  # Đảm bảo admin không bị khóa
    else:
        # Tạo mới tài khoản admin
        db.create_user('admin', admin_password, is_admin=1)
    
    print("Database initialized successfully!")
    print("Admin account:")
    print("Username: admin")
    print("Password: admin")

if __name__ == '__main__':
    init_database() 