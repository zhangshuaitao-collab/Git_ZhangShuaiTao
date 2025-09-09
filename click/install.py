#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 安装脚本
自动检查和安装依赖，配置运行环境
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import urllib.request
import zipfile
import tempfile


class ClickerInstaller:
    """快速点击助手安装器"""
    
    def __init__(self):
        self.app_name = "快速点击助手"
        self.version = "1.0.0"
        self.current_dir = Path(__file__).parent
        self.python_exe = sys.executable
        
        print(f"🚀 {self.app_name} v{self.version} 安装器")
        print(f"📁 安装目录: {self.current_dir}")
        print(f"🐍 Python路径: {self.python_exe}")
        print("-" * 50)
    
    def check_python_version(self):
        """检查Python版本"""
        print("🔍 检查Python版本...")
        
        version = sys.version_info
        if version < (3, 6):
            print("❌ 错误: 需要Python 3.6或更高版本")
            print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_platform(self):
        """检查操作系统平台"""
        print("🔍 检查操作系统...")
        
        system = platform.system()
        print(f"📱 操作系统: {system} {platform.release()}")
        
        if system == "Windows":
            print("✅ Windows系统支持良好")
            return True
        elif system == "Darwin":
            print("⚠️  macOS系统部分功能可能受限")
            return True
        elif system == "Linux":
            print("⚠️  Linux系统部分功能可能受限")
            return True
        else:
            print(f"❌ 不支持的操作系统: {system}")
            return False
    
    def check_dependencies(self):
        """检查依赖库"""
        print("🔍 检查依赖库...")
        
        dependencies = {
            'tkinter': '图形界面库',
            'pyautogui': '鼠标键盘自动化',
            'win32gui': 'Windows API',
            'PIL': '图像处理',
            'psutil': '系统信息'
        }
        
        missing = []
        installed = []
        
        for module, description in dependencies.items():
            try:
                if module == 'tkinter':
                    import tkinter
                elif module == 'pyautogui':
                    import pyautogui
                elif module == 'win32gui':
                    import win32gui
                elif module == 'PIL':
                    from PIL import Image
                elif module == 'psutil':
                    import psutil
                
                installed.append(f"✅ {module}: {description}")
            except ImportError:
                missing.append((module, description))
        
        # 显示已安装的库
        for msg in installed:
            print(msg)
        
        # 显示缺失的库
        if missing:
            print("\n❌ 缺少以下依赖库:")
            for module, description in missing:
                print(f"   - {module}: {description}")
            return False
        else:
            print("✅ 所有依赖库检查通过")
            return True
    
    def install_dependencies(self):
        """安装依赖库"""
        print("📦 开始安装依赖库...")
        
        requirements_file = self.current_dir / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ 找不到requirements.txt文件")
            return False
        
        try:
            # 升级pip
            print("⬆️  升级pip...")
            subprocess.check_call([
                self.python_exe, "-m", "pip", "install", "--upgrade", "pip"
            ], stdout=subprocess.DEVNULL)
            
            # 安装依赖
            print("📦 安装依赖库...")
            cmd = [
                self.python_exe, "-m", "pip", "install", 
                "-r", str(requirements_file), "--upgrade"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 依赖库安装成功")
                return True
            else:
                print("❌ 依赖库安装失败:")
                print(result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖库安装失败: {e}")
            return False
    
    def create_run_script(self):
        """创建运行脚本"""
        print("📝 创建运行脚本...")
        
        try:
            # Windows批处理脚本
            if platform.system() == "Windows":
                bat_content = f'''@echo off
chcp 65001 > nul
title {self.app_name} v{self.version}
cd /d "%~dp0"
echo 🚀 启动{self.app_name}...
"{self.python_exe}" main.py
if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错，请检查错误信息
    echo 💡 提示: 确保所有依赖库已正确安装
    pause
) else (
    echo.
    echo ✅ 程序正常退出
)
'''
                
                bat_file = self.current_dir / f"{self.app_name}.bat"
                with open(bat_file, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                print(f"✅ Windows批处理脚本创建成功: {bat_file}")
            
            # Shell脚本 (Linux/macOS)
            sh_content = f'''#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 启动{self.app_name}..."
"{self.python_exe}" main.py
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "❌ 程序运行出错，退出代码: $exit_code"
    echo "💡 提示: 确保所有依赖库已正确安装"
    read -p "按Enter键退出..."
else
    echo ""
    echo "✅ 程序正常退出"
fi
'''
            
            sh_file = self.current_dir / f"{self.app_name}.sh"
            with open(sh_file, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            
            # 设置执行权限
            try:
                os.chmod(sh_file, 0o755)
                print(f"✅ Shell脚本创建成功: {sh_file}")
            except OSError:
                print(f"⚠️  Shell脚本创建成功但无法设置权限: {sh_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建运行脚本失败: {e}")
            return False
    
    def create_desktop_shortcut(self):
        """创建桌面快捷方式"""
        print("🖥️  创建桌面快捷方式...")
        
        try:
            if platform.system() == "Windows":
                try:
                    import win32com.client
                    
                    desktop = Path.home() / "Desktop"
                    shortcut_path = desktop / f"{self.app_name}.lnk"
                    
                    # 优先使用批处理文件
                    bat_file = self.current_dir / f"{self.app_name}.bat"
                    if bat_file.exists():
                        target_path = str(bat_file)
                    else:
                        target_path = str(self.current_dir / "main.py")
                    
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(str(shortcut_path))
                    shortcut.Targetpath = target_path
                    shortcut.WorkingDirectory = str(self.current_dir)
                    shortcut.Description = f"{self.app_name} v{self.version}"
                    shortcut.save()
                    
                    print(f"✅ 桌面快捷方式创建成功: {shortcut_path}")
                    return True
                    
                except ImportError:
                    print("⚠️  无法创建桌面快捷方式 (需要pywin32)")
                    return False
            else:
                print("⚠️  当前系统不支持自动创建桌面快捷方式")
                return False
                
        except Exception as e:
            print(f"❌ 创建桌面快捷方式失败: {e}")
            return False
    
    def test_installation(self):
        """测试安装"""
        print("🧪 测试安装...")
        
        try:
            # 导入主要模块
            sys.path.insert(0, str(self.current_dir))
            
            print("   - 测试主程序导入...")
            import main
            
            print("   - 测试GUI模块...")
            import gui
            
            print("   - 测试点击引擎...")
            import clicker
            
            print("   - 测试窗口管理器...")
            import window_manager
            
            print("   - 测试配置管理器...")
            import config
            
            print("   - 测试工具函数...")
            import utils
            
            print("✅ 所有模块测试通过")
            return True
            
        except ImportError as e:
            print(f"❌ 模块导入测试失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 安装测试失败: {e}")
            return False
    
    def run(self):
        """运行安装程序"""
        print(f"开始安装 {self.app_name} v{self.version}")
        print("=" * 50)
        
        # 检查Python版本
        if not self.check_python_version():
            self.exit_with_error("Python版本不符合要求")
        
        # 检查操作系统
        if not self.check_platform():
            self.exit_with_error("操作系统不受支持")
        
        # 检查依赖
        deps_ok = self.check_dependencies()
        
        # 如果依赖缺失，尝试安装
        if not deps_ok:
            print("\n🔧 正在尝试自动安装缺失的依赖...")
            if not self.install_dependencies():
                self.exit_with_error("依赖安装失败")
            
            # 重新检查依赖
            print("\n🔍 重新检查依赖...")
            if not self.check_dependencies():
                self.exit_with_error("依赖安装后仍然缺失，请手动安装")
        
        # 创建运行脚本
        if not self.create_run_script():
            print("⚠️  运行脚本创建失败，但不影响正常使用")
        
        # 创建桌面快捷方式
        if not self.create_desktop_shortcut():
            print("⚠️  桌面快捷方式创建失败，但不影响正常使用")
        
        # 测试安装
        if not self.test_installation():
            self.exit_with_error("安装测试失败")
        
        # 安装完成
        self.show_success_message()
    
    def exit_with_error(self, message):
        """错误退出"""
        print(f"\n❌ 安装失败: {message}")
        print("\n💡 解决建议:")
        print("   1. 确保使用Python 3.6+版本")
        print("   2. 手动安装依赖: pip install -r requirements.txt")
        print("   3. 检查网络连接是否正常")
        print("   4. 尝试以管理员权限运行安装脚本")
        input("\n按Enter键退出...")
        sys.exit(1)
    
    def show_success_message(self):
        """显示成功消息"""
        print("\n" + "=" * 50)
        print("🎉 安装完成！")
        print("=" * 50)
        
        print(f"📱 应用程序: {self.app_name} v{self.version}")
        print(f"📁 安装位置: {self.current_dir}")
        
        print("\n🚀 启动方式:")
        if platform.system() == "Windows":
            bat_file = self.current_dir / f"{self.app_name}.bat"
            if bat_file.exists():
                print(f"   双击运行: {bat_file.name}")
            print("   或者双击桌面快捷方式")
        
        print(f"   或者运行: python {self.current_dir / 'main.py'}")
        
        print("\n📖 使用说明:")
        print("   1. 启动程序后点击'选择窗口'选择目标软件")
        print("   2. 点击'选择坐标'选择要点击的位置")
        print("   3. 设置点击参数后点击'开始点击'")
        print("   4. 使用Ctrl+Shift+Space快捷键快速开始/停止")
        
        print("\n⚠️  注意事项:")
        print("   - 请在合法范围内使用本软件")
        print("   - 确保目标软件窗口保持可见")
        print("   - 可以随时按ESC键停止所有操作")
        
        print("\n🆘 如需帮助:")
        print("   - 查看README.md文件")
        print("   - 检查应用程序日志文件")
        
        input("\n✅ 安装成功！按Enter键退出安装程序...")


def main():
    """主函数"""
    try:
        installer = ClickerInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 安装程序出现意外错误: {e}")
        input("按Enter键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
