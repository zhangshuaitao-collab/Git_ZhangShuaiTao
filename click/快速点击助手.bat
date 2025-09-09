@echo off
chcp 65001 > nul
title 快速点击助手 v1.0.0
cd /d "%~dp0"

echo.
echo ========================================
echo 🖱️  快速点击助手 - 桌面版 v1.0.0
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到Python环境
    echo.
    echo 💡 解决方案:
    echo    1. 安装Python 3.6或更高版本
    echo    2. 确保Python已添加到系统PATH
    echo    3. 重新打开命令行窗口
    echo.
    pause
    exit /b 1
)

:: 显示Python版本
echo 🐍 检测到Python环境:
python --version
echo.

:: 检查主程序文件
if not exist "main.py" (
    echo ❌ 错误: 找不到main.py主程序文件
    echo 💡 请确保在正确的程序目录中运行此脚本
    echo.
    pause
    exit /b 1
)

:: 检查依赖库
echo 🔍 正在检查依赖库...
python -c "import sys, pkgutil; missing = []; required = ['tkinter', 'pyautogui', 'win32gui', 'PIL', 'psutil']; [missing.append(pkg) for pkg in required if not pkgutil.find_loader(pkg)]; print('✅ 所有依赖库已安装') if not missing else (print(f'❌ 缺少依赖: {missing}'), sys.exit(1))" 2>nul
if errorlevel 1 (
    echo.
    echo ⚠️  检测到缺失的依赖库，正在尝试自动安装...
    echo.
    
    if exist "install.py" (
        echo 🔧 运行自动安装程序...
        python install.py
        if errorlevel 1 (
            echo.
            echo ❌ 自动安装失败
            echo 💡 请手动运行: pip install -r requirements.txt
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo 💡 请手动安装依赖库:
        echo    pip install pyautogui pywin32 Pillow psutil
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 🚀 正在启动快速点击助手...
echo ⚠️  提示: 可以按Ctrl+C或关闭窗口来退出程序
echo.

:: 启动主程序
python main.py

:: 检查程序退出状态
if errorlevel 1 (
    echo.
    echo ❌ 程序异常退出
    echo.
    echo 🔍 故障排除建议:
    echo    1. 检查错误消息并记录
    echo    2. 确认所有依赖库正确安装
    echo    3. 尝试以管理员权限运行
    echo    4. 检查防病毒软件是否阻止
    echo    5. 查看日志文件获取详细信息
    echo.
    echo 📞 如需帮助，请提供上述错误信息
    echo.
    pause
) else (
    echo.
    echo ✅ 程序正常退出
    echo 💖 感谢使用快速点击助手！
    echo.
    timeout /t 3 /nobreak >nul
)

exit /b 0
