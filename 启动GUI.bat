@echo off
chcp 65001 >nul
echo ========================================
echo 游戏自动化GUI启动器
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境
    echo 请先运行: python -m venv .venv
    pause
    exit /b 1
)

REM 检查是否需要安装依赖
echo [1/2] 检查依赖...
.venv\Scripts\python.exe -c "import keyboard" 2>nul
if errorlevel 1 (
    echo [提示] 需要安装依赖包
    echo.
    .venv\Scripts\python.exe install_gui_deps.py
    echo.
    pause
)

REM 启动GUI
echo [2/2] 启动GUI...
echo.
echo ========================================
echo 提示:
echo   - F10 = 启动脚本
echo   - F11 = 暂停/恢复
echo   - F12 = 停止脚本
echo ========================================
echo.

.venv\Scripts\python.exe gui_script.py

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)
