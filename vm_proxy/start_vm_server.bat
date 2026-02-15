@echo off
REM ========================================
REM 虚拟机端 - 启动游戏代理服务器
REM ========================================

echo 正在启动虚拟机游戏代理服务器...
echo.

REM 激活虚拟环境（如果使用）
REM call .venv\Scripts\activate.bat

REM 安装依赖
echo 检查依赖...
pip show websockets >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install websockets numpy opencv-python pillow pyautogui
)

REM 启动服务器
echo 启动服务器...
python remote_server.py

pause
