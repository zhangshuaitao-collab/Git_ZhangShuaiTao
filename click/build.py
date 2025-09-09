#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 打包脚本
使用PyInstaller将Python程序打包为独立可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform


class ClickerBuilder:
    """快速点击助手打包器"""
    
    def __init__(self):
        self.app_name = "快速点击助手"
        self.version = "1.0.0"
        self.current_dir = Path(__file__).parent
        self.dist_dir = self.current_dir / "dist"
        self.build_dir = self.current_dir / "build"
        
        print(f"🔨 {self.app_name} v{self.version} 打包器")
        print(f"📁 项目目录: {self.current_dir}")
        print("-" * 50)
    
    def check_pyinstaller(self):
        """检查PyInstaller是否安装"""
        print("🔍 检查PyInstaller...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "PyInstaller", "--version"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ PyInstaller已安装: {version}")
                return True
            else:
                print("❌ PyInstaller未正确安装")
                return False
                
        except FileNotFoundError:
            print("❌ PyInstaller未安装")
            return False
    
    def install_pyinstaller(self):
        """安装PyInstaller"""
        print("📦 正在安装PyInstaller...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pyinstaller"
            ])
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller安装失败: {e}")
            return False
    
    def clean_build(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                print("✅ build目录已清理")
            
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
                print("✅ dist目录已清理")
                
            # 清理.spec文件
            spec_files = list(self.current_dir.glob("*.spec"))
            for spec_file in spec_files:
                spec_file.unlink()
                print(f"✅ 已删除: {spec_file.name}")
                
            return True
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return False
    
    def create_spec_file(self):
        """创建PyInstaller规格文件"""
        print("📝 创建PyInstaller配置...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主程序
a = Analysis(
    ['main.py'],
    pathex=['{self.current_dir}'],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'win32gui',
        'win32api',
        'win32con',
        'win32process',
        'win32ui',
        'pyautogui',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.distutils',
        'tcl',
        'tk',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
    version_file='version.txt' if Path('version.txt').exists() else None,
)
'''
        
        spec_file = self.current_dir / f"{self.app_name}.spec"
        try:
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            print(f"✅ 规格文件创建成功: {spec_file}")
            return spec_file
        except Exception as e:
            print(f"❌ 规格文件创建失败: {e}")
            return None
    
    def create_version_file(self):
        """创建版本信息文件"""
        print("📄 创建版本信息文件...")
        
        version_content = f'''# UTF-8
#
# 版本信息文件
#

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{self.app_name}开发团队'),
            StringStruct(u'FileDescription', u'{self.app_name} - 桌面自动点击软件'),
            StringStruct(u'FileVersion', u'{self.version}'),
            StringStruct(u'InternalName', u'{self.app_name}'),
            StringStruct(u'LegalCopyright', u'© 2024 {self.app_name}开发团队'),
            StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
            StringStruct(u'ProductName', u'{self.app_name}'),
            StringStruct(u'ProductVersion', u'{self.version}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_file = self.current_dir / "version.txt"
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(version_content)
            print(f"✅ 版本文件创建成功: {version_file}")
            return version_file
        except Exception as e:
            print(f"❌ 版本文件创建失败: {e}")
            return None
    
    def build_executable(self, spec_file):
        """构建可执行文件"""
        print("🔨 开始构建可执行文件...")
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            print("执行命令:", " ".join(cmd))
            result = subprocess.run(cmd, cwd=self.current_dir)
            
            if result.returncode == 0:
                print("✅ 可执行文件构建成功")
                return True
            else:
                print("❌ 可执行文件构建失败")
                return False
                
        except Exception as e:
            print(f"❌ 构建过程中出错: {e}")
            return False
    
    def copy_resources(self):
        """复制资源文件到发布目录"""
        print("📁 复制资源文件...")
        
        try:
            exe_dir = self.dist_dir / self.app_name
            if not exe_dir.exists():
                print(f"❌ 找不到可执行文件目录: {exe_dir}")
                return False
            
            # 要复制的文件列表
            resource_files = [
                "README.md",
                "requirements.txt",
                "install_guide.txt",
            ]
            
            # 复制文件
            for file_name in resource_files:
                src_file = self.current_dir / file_name
                if src_file.exists():
                    dst_file = exe_dir / file_name
                    shutil.copy2(src_file, dst_file)
                    print(f"✅ 已复制: {file_name}")
                else:
                    print(f"⚠️  文件不存在: {file_name}")
            
            # 创建启动批处理文件
            if platform.system() == "Windows":
                bat_content = f'''@echo off
chcp 65001 > nul
title {self.app_name} v{self.version}
echo 🚀 启动{self.app_name}...
"%~dp0{self.app_name}.exe"
if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错
    pause
)
'''
                bat_file = exe_dir / "启动程序.bat"
                with open(bat_file, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                print("✅ 启动脚本创建成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 复制资源文件失败: {e}")
            return False
    
    def create_installer(self):
        """创建安装包（可选）"""
        print("📦 检查是否可以创建安装包...")
        
        # 检查是否有NSIS
        try:
            result = subprocess.run(["makensis", "/VERSION"], capture_output=True)
            if result.returncode == 0:
                print("✅ 检测到NSIS，可以创建安装包")
                # 这里可以添加NSIS脚本生成逻辑
                return True
            else:
                print("⚠️  未检测到NSIS，跳过安装包创建")
                return False
        except FileNotFoundError:
            print("⚠️  未安装NSIS，跳过安装包创建")
            return False
    
    def show_build_result(self):
        """显示构建结果"""
        print("\n" + "=" * 50)
        print("🎉 构建完成！")
        print("=" * 50)
        
        exe_dir = self.dist_dir / self.app_name
        if exe_dir.exists():
            exe_file = exe_dir / f"{self.app_name}.exe"
            if exe_file.exists():
                file_size = exe_file.stat().st_size / 1024 / 1024
                print(f"📱 可执行文件: {exe_file}")
                print(f"📏 文件大小: {file_size:.1f} MB")
                
                print(f"\n📁 发布目录: {exe_dir}")
                print("📋 包含文件:")
                for item in sorted(exe_dir.iterdir()):
                    if item.is_file():
                        size = item.stat().st_size
                        if size > 1024 * 1024:
                            size_str = f"{size / 1024 / 1024:.1f} MB"
                        elif size > 1024:
                            size_str = f"{size / 1024:.1f} KB"
                        else:
                            size_str = f"{size} B"
                        print(f"   - {item.name} ({size_str})")
                
                print("\n🚀 测试运行:")
                print(f"   双击运行: {exe_file}")
                print("   或使用启动脚本")
                
                print("\n📦 分发说明:")
                print("   1. 将整个发布目录复制给用户")
                print("   2. 用户直接运行exe文件即可")
                print("   3. 无需安装Python和依赖库")
            else:
                print(f"❌ 未找到可执行文件: {exe_file}")
        else:
            print(f"❌ 未找到发布目录: {exe_dir}")
    
    def run(self):
        """运行打包程序"""
        print(f"开始打包 {self.app_name} v{self.version}")
        print("=" * 50)
        
        # 检查PyInstaller
        if not self.check_pyinstaller():
            if not self.install_pyinstaller():
                print("❌ 无法安装PyInstaller，打包终止")
                return False
        
        # 清理构建目录
        if not self.clean_build():
            print("⚠️  清理构建目录失败，但继续进行")
        
        # 创建版本文件
        self.create_version_file()
        
        # 创建规格文件
        spec_file = self.create_spec_file()
        if not spec_file:
            print("❌ 创建规格文件失败，打包终止")
            return False
        
        # 构建可执行文件
        if not self.build_executable(spec_file):
            print("❌ 构建可执行文件失败")
            return False
        
        # 复制资源文件
        if not self.copy_resources():
            print("⚠️  复制资源文件失败，但不影响程序运行")
        
        # 尝试创建安装包
        self.create_installer()
        
        # 显示构建结果
        self.show_build_result()
        
        return True


def main():
    """主函数"""
    try:
        builder = ClickerBuilder()
        
        # 询问是否继续
        print("⚠️  注意: 打包过程可能需要几分钟时间")
        response = input("是否继续打包? (y/N): ").strip().lower()
        
        if response in ['y', 'yes', '是']:
            success = builder.run()
            if success:
                input("✅ 打包成功！按Enter键退出...")
            else:
                input("❌ 打包失败！按Enter键退出...")
        else:
            print("⚠️  打包已取消")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  打包被用户中断")
    except Exception as e:
        print(f"\n\n❌ 打包程序出现意外错误: {e}")
        input("按Enter键退出...")


if __name__ == "__main__":
    main()
