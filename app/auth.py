from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import Database
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)
db = Database()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Kiểm tra nếu user đã đăng nhập
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            # Thiết lập session
            session.permanent = True  # Sử dụng permanent session lifetime
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            # Kiểm tra next parameter
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):  # Đảm bảo URL là internal
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        
        flash('Tên đăng nhập hoặc mật khẩu không đúng')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if db.get_user_by_username(username):
            flash('Tên đăng nhập đã tồn tại')
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        user_id = db.create_user(username, hashed_password)
        
        if user_id:
            flash('Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect(url_for('auth.login'))
        
        flash('Có lỗi xảy ra, vui lòng thử lại')
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    # Xóa tất cả dữ liệu trong session
    session.clear()
    # Thêm thông báo
    flash('Bạn đã đăng xuất thành công')
    # Chuyển hướng về trang login
    return redirect(url_for('auth.login'))

# Thêm before_request để kiểm tra session trong mỗi request
@auth_bp.before_app_request
def before_request():
    if 'user_id' in session:
        # Kiểm tra các route không cần bảo vệ
        if request.endpoint and request.endpoint.startswith('static'):
            return
        
        # Kiểm tra nếu đang truy cập trang login/register
        if request.endpoint in ['auth.login', 'auth.register']:
            return redirect(url_for('main.dashboard')) 