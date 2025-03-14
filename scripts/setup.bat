@echo off
echo === Study Group Manager Setup ===
echo.

:: Chuyển về thư mục gốc của project
cd /d %~dp0\..

:: Kiểm tra Python đã được cài đặt chưa
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chưa được cài đặt!
    echo Vui lòng cài đặt Python từ: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Kiểm tra và tạo thư mục data
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

:: Kiểm tra và tạo môi trường ảo
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Kích hoạt môi trường ảo và cài đặt các thư viện
echo Activating virtual environment...
call venv\Scripts\activate

echo Installing required packages...
pip install -r requirements.txt

echo.
echo === Setup completed successfully! ===
echo To run the application, use: scripts\run.bat
echo.

pause 