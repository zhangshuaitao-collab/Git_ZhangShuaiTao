#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 桌面版
一个强大的桌面自动点击软件，可以点击任何软件窗口中的按钮
Author: Assistant
Version: 1.0.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from gui import ClickerGUI
    from config import Config
    from utils import setup_logging
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有必需的文件都存在")
    sys.exit(1)

class ClickerApp:
    """快速点击助手主应用程序"""
    
    def __init__(self):
        """初始化应用程序"""
        self.version = "1.0.0"
        self.app_name = "快速点击助手"
        
        # 设置日志
        self.setup_logging()
        
        # 初始化配置
        self.config = Config()
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title(f"{self.app_name} v{self.version}")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置应用图标（如果存在）
        self.set_app_icon()
        
        # 初始化GUI
        try:
            self.gui = ClickerGUI(self.root, self.config)
        except Exception as e:
            logging.error(f"初始化GUI失败: {e}")
            messagebox.showerror("错误", f"初始化界面失败:\n{e}")
            sys.exit(1)
        
        # 绑定窗口事件
        self.setup_window_events()
        
        logging.info(f"{self.app_name} v{self.version} 启动成功")
    
    def setup_logging(self):
        """设置日志系统"""
        try:
            setup_logging()
            logging.info("日志系统初始化成功")
        except Exception as e:
            print(f"日志系统初始化失败: {e}")
    
    def set_app_icon(self):
        """设置应用图标"""
        icon_paths = [
            "icon.ico",
            "assets/icon.ico", 
            "images/icon.ico"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                    logging.info(f"应用图标设置成功: {icon_path}")
                    break
                except Exception as e:
                    logging.warning(f"设置图标失败 {icon_path}: {e}")
    
    def setup_window_events(self):
        """设置窗口事件"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 窗口大小改变事件
        self.root.bind("<Configure>", self.on_window_configure)
        
        # 快捷键绑定
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """设置全局快捷键"""
        try:
            # Ctrl+Shift+Space: 快速开始/停止点击
            self.root.bind("<Control-Shift-space>", self.gui.toggle_clicking)
            
            # F1: 显示帮助
            self.root.bind("<F1>", self.show_help)
            
            # Ctrl+S: 保存配置
            self.root.bind("<Control-s>", lambda e: self.gui.save_config())
            
            # Ctrl+O: 加载配置  
            self.root.bind("<Control-o>", lambda e: self.gui.load_config())
            
            # Esc: 停止所有操作
            self.root.bind("<Escape>", lambda e: self.gui.stop_all())
            
            logging.info("快捷键绑定成功")
        except Exception as e:
            logging.error(f"快捷键绑定失败: {e}")
    
    def on_window_configure(self, event):
        """窗口配置改变事件"""
        if event.widget == self.root:
            # 保存窗口位置和大小
            geometry = self.root.geometry()
            self.config.set('window', 'geometry', geometry)
    
    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 停止所有点击操作
            if hasattr(self.gui, 'stop_all'):
                self.gui.stop_all()
            
            # 保存配置
            self.config.save()
            
            # 等待后台线程结束
            self.wait_for_threads()
            
            logging.info(f"{self.app_name} 正常退出")
            
        except Exception as e:
            logging.error(f"退出时发生错误: {e}")
        finally:
            self.root.quit()
            self.root.destroy()
    
    def wait_for_threads(self, timeout=3):
        """等待后台线程结束"""
        try:
            # 获取所有活动线程
            active_threads = [t for t in threading.enumerate() if t != threading.current_thread()]
            
            for thread in active_threads:
                if thread.is_alive():
                    thread.join(timeout=timeout)
                    
        except Exception as e:
            logging.error(f"等待线程结束时出错: {e}")
    
    def show_help(self, event=None):
        """显示帮助信息"""
        help_text = f"""
{self.app_name} v{self.version} 使用帮助

🎯 主要功能：
• 选择任意软件窗口中的按钮进行自动点击
• 支持单点和连续点击模式  
• 可设置点击间隔和次数
• 支持配置保存和加载

⌨️ 快捷键：
• Ctrl+Shift+Space: 开始/停止点击
• F1: 显示此帮助
• Ctrl+S: 保存配置
• Ctrl+O: 加载配置  
• Esc: 停止所有操作

📖 使用步骤：
1. 点击"选择窗口"选择目标软件
2. 点击"选择坐标"选择要点击的位置
3. 设置点击参数（间隔、次数等）
4. 点击"开始点击"启动自动点击

💡 提示：
• 请确保目标软件窗口保持可见
• 建议先进行测试点击确认位置正确
• 可以随时按Esc键停止所有操作

技术支持: 如有问题请查看日志文件
        """
        
        messagebox.showinfo("使用帮助", help_text)
    
    def run(self):
        """运行应用程序"""
        try:
            # 恢复窗口位置和大小
            saved_geometry = self.config.get('window', 'geometry', fallback='800x600+100+100')
            self.root.geometry(saved_geometry)
            
            # 启动主循环
            self.root.mainloop()
            
        except KeyboardInterrupt:
            logging.info("用户中断程序")
            self.on_closing()
        except Exception as e:
            logging.error(f"程序运行时发生错误: {e}")
            messagebox.showerror("严重错误", f"程序运行失败:\n{e}")
        finally:
            sys.exit(0)

def main():
    """主函数"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 6):
            print("错误: 需要Python 3.6或更高版本")
            sys.exit(1)
        
        # 创建并运行应用程序
        app = ClickerApp()
        app.run()
        
    except ImportError as e:
        print(f"缺少必需的模块: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
