from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database import Database
from app import login_required, admin_required
from datetime import datetime
from werkzeug.security import generate_password_hash
import string
import random

main_bp = Blueprint('main', __name__)
db = Database()

@main_bp.route('/')
@login_required
def dashboard():
    if session.get('is_admin'):
        return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.user_dashboard'))

@main_bp.route('/user-dashboard')
@login_required
def user_dashboard():
    tasks = db.get_user_tasks(session['user_id'])
    return render_template('user_dashboard.html', tasks=tasks)

@main_bp.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    users = db.get_all_users(exclude_admin=True)
    tasks = db.get_all_tasks()
    return render_template('admin/dashboard.html', users=users, tasks=tasks)

@main_bp.route('/add-task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        
        task_id = db.create_task(
            title=title,
            description=description,
            due_date=due_date,
            user_id=session['user_id']
        )
        
        if task_id:
            flash('Thêm nhiệm vụ thành công!')
            return redirect(url_for('main.user_dashboard'))
        
        flash('Có lỗi xảy ra, vui lòng thử lại')
    return render_template('add_task.html')

@main_bp.route('/task/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(task_id):
    status = request.form.get('status')
    if db.update_task_status(task_id, status):
        flash('Cập nhật trạng thái thành công!')
    else:
        flash('Có lỗi xảy ra, vui lòng thử lại')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    if db.delete_task(task_id):
        flash('Xóa nhiệm vụ thành công!')
    else:
        flash('Có lỗi xảy ra, vui lòng thử lại')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    if db.complete_task(task_id, session['user_id']):
        flash('Nhiệm vụ đã được đánh dấu hoàn thành!')
    else:
        flash('Có lỗi xảy ra hoặc bạn không có quyền thực hiện hành động này')
    return redirect(url_for('main.user_dashboard'))

def generate_random_password(length=12):
    """Tạo mật khẩu ngẫu nhiên"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

@main_bp.route('/admin/users')
@admin_required
def manage_users():
    users = db.get_all_users(exclude_admin=True)
    return render_template('admin/manage_users.html', users=users)

@main_bp.route('/admin/user/<int:user_id>')
@admin_required
def user_details(user_id):
    user = db.get_user_details(user_id)
    if user:
        return render_template('admin/user_details.html', user=user)
    flash('Không tìm thấy người dùng')
    return redirect(url_for('main.manage_users'))

@main_bp.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = db.get_user_by_id(user_id)
    if user:
        new_status = 'locked' if user['status'] == 'active' else 'active'
        if db.update_user_status(user_id, new_status):
            flash(f'Đã {"khóa" if new_status == "locked" else "mở khóa"} tài khoản thành công')
        else:
            flash('Có lỗi xảy ra')
    return redirect(url_for('main.user_details', user_id=user_id))

@main_bp.route('/admin/user/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    user = db.get_user_by_id(user_id)
    if user:
        if user['username'].lower() == 'admin':
            # Nếu là admin, mật khẩu luôn reset về 'admin'
            hashed_password = generate_password_hash('admin')
            if db.reset_user_password(user_id, hashed_password):
                flash('Mật khẩu admin đã được reset về mặc định: admin')
            else:
                flash('Có lỗi xảy ra khi reset mật khẩu')
        else:
            # Nếu không phải admin, tạo mật khẩu ngẫu nhiên
            new_password = generate_random_password()
            hashed_password = generate_password_hash(new_password)
            if db.reset_user_password(user_id, hashed_password):
                flash(f'Mật khẩu mới: {new_password}')
            else:
                flash('Có lỗi xảy ra khi reset mật khẩu')
    return redirect(url_for('main.user_details', user_id=user_id))

@main_bp.route('/admin/add-user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if username.lower() == 'admin':
            flash('Không thể tạo user với tên "admin"')
            return redirect(url_for('main.add_user'))
            
        if db.get_user_by_username(username):
            flash('Tên đăng nhập đã tồn tại')
            return redirect(url_for('main.add_user'))
        
        hashed_password = generate_password_hash(password)
        user_id = db.create_user(username, hashed_password, is_admin)
        
        if user_id:
            flash('Tạo user thành công!')
            return redirect(url_for('main.manage_users'))
        
        flash('Có lỗi xảy ra khi tạo user')
    return render_template('admin/add_user.html')

@main_bp.route('/admin/assign-task', methods=['GET', 'POST'])
@admin_required
def assign_task():
    users = db.get_non_admin_users()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        user_ids = request.form.getlist('user_ids')  # Lấy danh sách user được chọn
        
        if not user_ids:
            flash('Vui lòng chọn ít nhất một người dùng')
            return redirect(url_for('main.assign_task'))
            
        if db.create_task_for_users(title, description, due_date, user_ids):
            flash('Đã giao nhiệm vụ thành công!')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Có lỗi xảy ra khi giao nhiệm vụ')
            
    return render_template('admin/assign_task.html', users=users)

@main_bp.before_request
def check_session():
    # Kiểm tra session trong mỗi request đến main blueprint
    if not session.get('user_id'):
        return redirect(url_for('auth.login', next=request.url)) 