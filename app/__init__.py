from flask import Flask, session, redirect, url_for, request
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra session và thời gian session
        if 'user_id' not in session:
            # Lưu URL hiện tại để redirect sau khi đăng nhập
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            # Nếu không phải admin hoặc chưa đăng nhập, chuyển về trang login
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Cấu hình session
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 phút
    app.config['SESSION_COOKIE_SECURE'] = True  # Chỉ gửi cookie qua HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Không cho phép JS truy cập cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Bảo vệ CSRF

    # Đăng ký blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app 