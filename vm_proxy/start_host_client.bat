@echo off
REM ========================================
REM 主机端 - 启动远程自动化GUI
REM ========================================

echo 正在启动主机远程自动化GUI...
echo.

REM 激活虚拟环境（如果使用）
REM call .venv\Scripts\activate.bat

REM 安装依赖
echo 检查依赖...
pip show websockets >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install websockets numpy opencv-python pillow
)

REM 启动远程GUI
python remote_gui_script.py

pause
