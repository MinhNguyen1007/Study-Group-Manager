@echo off
echo === Starting Study Group Manager ===
echo.

:: Chuyển về thư mục gốc của project
cd /d %~dp0\..

:: Kiểm tra môi trường ảo
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

:: Kích hoạt môi trường ảo
echo Activating virtual environment...
call venv\Scripts\activate

:: Kiểm tra thư mục data
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

:: Chạy ứng dụng
echo Starting application...
echo.
echo Access the application at: http://localhost:5000
echo Default admin account: admin/admin
echo.
echo Press Ctrl+C to stop the server
echo.

:: Chạy main.py từ thư mục gốc
python main.py

pause 