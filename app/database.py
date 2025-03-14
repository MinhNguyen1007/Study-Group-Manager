import sqlite3
from sqlite3 import Error
from datetime import datetime
import os
from werkzeug.security import generate_password_hash

class Database:
    def __init__(self):
        # Tạo thư mục data nếu chưa tồn tại
        data_dir = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(data_dir, 'data')
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        self.db_file = os.path.join(data_path, 'tasks.db')
        
        # Chỉ tạo database và admin nếu chưa tồn tại
        if not os.path.exists(self.db_file):
            self.create_tables()
            self.ensure_admin_exists()
        else:
            # Nếu database đã tồn tại, chỉ đảm bảo admin tồn tại
            self.ensure_admin_exists()

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except Error as e:
            print(f"Error connecting to database: {e}")
            return None

    def create_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_tasks_table = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """

        conn = self.get_connection()
        if conn:
            try:
                conn.execute(create_users_table)
                conn.execute(create_tasks_table)
                conn.commit()
            except Error as e:
                print(f"Error creating tables: {e}")
            finally:
                conn.close()

    def ensure_admin_exists(self):
        """Đảm bảo tài khoản admin luôn tồn tại với mật khẩu mặc định"""
        admin = self.get_user_by_username('admin')
        admin_password = generate_password_hash('admin')
        
        if admin:
            # Cập nhật lại mật khẩu và trạng thái của admin
            self.reset_user_password(admin['id'], admin_password)
            self.update_user_status(admin['id'], 'active')
        else:
            # Tạo mới tài khoản admin
            self.create_user('admin', admin_password, is_admin=1)

    def create_user(self, username, password, is_admin=0):
        """Tạo user mới"""
        # Không cho phép tạo user với username là 'admin'
        if username.lower() == 'admin' and not is_admin:
            print("Cannot create user with username 'admin'")
            return None
            
        sql = """INSERT INTO users (username, password, is_admin, status) 
                VALUES (?, ?, ?, 'active')"""
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (username, password, is_admin))
                conn.commit()
                return cur.lastrowid
            except Error as e:
                print(f"Error creating user: {e}")
                return None
            finally:
                conn.close()

    def get_user_by_username(self, username):
        sql = "SELECT * FROM users WHERE username = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (username,))
                return cur.fetchone()
            except Error as e:
                print(f"Error getting user: {e}")
                return None
            finally:
                conn.close()

    def get_user_by_id(self, user_id):
        sql = "SELECT * FROM users WHERE id = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (user_id,))
                return cur.fetchone()
            except Error as e:
                print(f"Error getting user: {e}")
                return None
            finally:
                conn.close()

    def get_all_users(self, exclude_admin=False):
        """Lấy danh sách tất cả users với thông tin về nhiệm vụ"""
        if exclude_admin:
            sql = """
            SELECT u.*,
                   COUNT(t.id) as task_count,
                   SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
            FROM users u
            LEFT JOIN tasks t ON u.id = t.user_id
            WHERE u.username != 'admin'
            GROUP BY u.id
            ORDER BY u.created_at DESC
            """
        else:
            sql = """
            SELECT u.*,
                   COUNT(t.id) as task_count,
                   SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
            FROM users u
            LEFT JOIN tasks t ON u.id = t.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
            """
        
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql)
                return cur.fetchall()
            except Error as e:
                print(f"Error getting users: {e}")
                return []
            finally:
                conn.close()

    def create_task(self, title, description, due_date, user_id):
        sql = """
        INSERT INTO tasks (title, description, due_date, user_id)
        VALUES (?, ?, ?, ?)
        """
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (title, description, due_date, user_id))
                conn.commit()
                return cur.lastrowid
            except Error as e:
                print(f"Error creating task: {e}")
                return None
            finally:
                conn.close()

    def get_user_tasks(self, user_id):
        """Lấy danh sách task của user, sắp xếp theo trạng thái và hạn"""
        sql = """
        SELECT * FROM tasks 
        WHERE user_id = ? 
        ORDER BY 
            CASE 
                WHEN status = 'completed' THEN 1 
                ELSE 0 
            END,
            due_date ASC
        """
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (user_id,))
                return cur.fetchall()
            except Error as e:
                print(f"Error getting tasks: {e}")
                return []
            finally:
                conn.close()

    def get_all_tasks(self):
        sql = """
        SELECT t.*, u.username 
        FROM tasks t 
        JOIN users u ON t.user_id = u.id 
        ORDER BY t.due_date
        """
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql)
                return cur.fetchall()
            except Error as e:
                print(f"Error getting tasks: {e}")
                return []
            finally:
                conn.close()

    def update_task_status(self, task_id, status):
        sql = "UPDATE tasks SET status = ? WHERE id = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (status, task_id))
                conn.commit()
                return True
            except Error as e:
                print(f"Error updating task: {e}")
                return False
            finally:
                conn.close()

    def delete_task(self, task_id):
        sql = "DELETE FROM tasks WHERE id = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (task_id,))
                conn.commit()
                return True
            except Error as e:
                print(f"Error deleting task: {e}")
                return False
            finally:
                conn.close()

    def get_task_statistics(self, user_id=None):
        """Lấy thống kê về tasks"""
        if user_id:
            sql = """
            SELECT 
                status,
                COUNT(*) as count
            FROM task 
            WHERE user_id = ?
            GROUP BY status
            """
            params = (user_id,)
        else:
            sql = """
            SELECT 
                status,
                COUNT(*) as count
            FROM task 
            GROUP BY status
            """
            params = ()

        conn = self.get_connection()
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute(sql, params)
                return cur.fetchall()
            except Error as e:
                print(f"Error getting statistics: {e}")
            finally:
                conn.close()
        return []

    def update_user_status(self, user_id, status):
        """Cập nhật trạng thái của user (active/locked)"""
        # Kiểm tra xem có phải admin không
        user = self.get_user_by_id(user_id)
        if user and user['username'].lower() == 'admin':
            print("Cannot lock admin account")
            return False
        
        sql = "UPDATE users SET status = ? WHERE id = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (status, user_id))
                conn.commit()
                return True
            except Error as e:
                print(f"Error updating user status: {e}")
                return False
            finally:
                conn.close()

    def reset_user_password(self, user_id, new_password):
        """Reset mật khẩu của user"""
        # Kiểm tra xem có phải admin không
        user = self.get_user_by_id(user_id)
        if user and user['username'].lower() == 'admin':
            new_password = generate_password_hash('admin')
        
        sql = "UPDATE users SET password = ? WHERE id = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (new_password, user_id))
                conn.commit()
                return True
            except Error as e:
                print(f"Error resetting password: {e}")
                return False
            finally:
                conn.close()

    def get_user_details(self, user_id):
        """Lấy thông tin chi tiết của user"""
        sql = """
        SELECT u.*, 
               COUNT(t.id) as task_count,
               SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        WHERE u.id = ?
        GROUP BY u.id
        """
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (user_id,))
                return cur.fetchone()
            except Error as e:
                print(f"Error getting user details: {e}")
                return None
            finally:
                conn.close()

    def create_task_for_users(self, title, description, due_date, user_ids):
        """Tạo cùng một nhiệm vụ cho nhiều user"""
        sql = """
        INSERT INTO tasks (title, description, due_date, user_id)
        VALUES (?, ?, ?, ?)
        """
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                for user_id in user_ids:
                    cur.execute(sql, (title, description, due_date, user_id))
                conn.commit()
                return True
            except Error as e:
                print(f"Error creating tasks: {e}")
                return False
            finally:
                conn.close()

    def get_non_admin_users(self):
        """Lấy danh sách user không phải admin"""
        sql = "SELECT * FROM users WHERE username != 'admin' ORDER BY username"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql)
                return cur.fetchall()
            except Error as e:
                print(f"Error getting users: {e}")
                return []
            finally:
                conn.close()

    def complete_task(self, task_id, user_id):
        """Đánh dấu task là đã hoàn thành"""
        # Kiểm tra xem task có thuộc về user không
        sql_check = "SELECT * FROM tasks WHERE id = ? AND user_id = ?"
        sql_update = "UPDATE tasks SET status = 'completed' WHERE id = ? AND user_id = ?"
        
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                # Kiểm tra quyền sở hữu task
                cur.execute(sql_check, (task_id, user_id))
                task = cur.fetchone()
                
                if task:
                    # Cập nhật trạng thái
                    cur.execute(sql_update, (task_id, user_id))
                    conn.commit()
                    return True
                return False
            except Error as e:
                print(f"Error completing task: {e}")
                return False
            finally:
                conn.close()

    def get_task_by_id(self, task_id):
        """Lấy thông tin của một task cụ thể"""
        sql = "SELECT * FROM tasks WHERE id = ?"
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (task_id,))
                return cur.fetchone()
            except Error as e:
                print(f"Error getting task: {e}")
                return None
            finally:
                conn.close() 