#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 工具函数
提供各种实用工具函数
"""

import os
import sys
import time
import logging
import platform
from pathlib import Path
from typing import Any, Optional, Tuple
from datetime import datetime, timedelta
import threading
import subprocess


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """设置日志系统"""
    try:
        # 创建日志目录
        if log_file is None:
            log_dir = Path.home() / '.click_helper'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'app.log'
        
        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 设置日志级别
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 配置root logger
        logging.basicConfig(
            level=level,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # 设置外部库的日志级别
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('pyautogui').setLevel(logging.WARNING)
        
        logging.info(f"日志系统初始化成功，日志文件: {log_file}")
        
    except Exception as e:
        print(f"设置日志系统失败: {e}")


def format_time(seconds: float) -> str:
    """格式化时间（秒）为可读格式"""
    try:
        if seconds < 60:
            return f"{seconds:.1f} 秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} 分 {secs} 秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours} 小时 {minutes} 分 {secs} 秒"
    except Exception:
        return "未知"


def format_datetime(dt_str: str, format_type: str = 'full') -> str:
    """格式化日期时间字符串"""
    try:
        dt = datetime.fromisoformat(dt_str)
        
        if format_type == 'full':
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date':
            return dt.strftime('%Y-%m-%d')
        elif format_type == 'time':
            return dt.strftime('%H:%M:%S')
        elif format_type == 'relative':
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} 天前"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} 小时前"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} 分钟前"
            else:
                return "刚刚"
        else:
            return dt_str
    except Exception:
        return dt_str


def validate_number(value: str, min_val: int = 0, max_val: int = 999999) -> Tuple[bool, int]:
    """验证数字输入"""
    try:
        num = int(value)
        if min_val <= num <= max_val:
            return True, num
        else:
            return False, 0
    except ValueError:
        return False, 0


def get_system_info() -> dict:
    """获取系统信息"""
    try:
        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'platform_release': platform.release(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'username': os.getlogin() if hasattr(os, 'getlogin') else 'Unknown'
        }
        return info
    except Exception as e:
        logging.error(f"获取系统信息失败: {e}")
        return {}


def check_dependencies() -> dict:
    """检查依赖库是否安装"""
    dependencies = {
        'pyautogui': False,
        'pywin32': False,
        'Pillow': False,
        'psutil': False,
        'tkinter': False
    }
    
    # 检查pyautogui
    try:
        import pyautogui
        dependencies['pyautogui'] = True
    except ImportError:
        pass
    
    # 检查pywin32
    try:
        import win32gui
        dependencies['pywin32'] = True
    except ImportError:
        pass
    
    # 检查Pillow
    try:
        from PIL import Image
        dependencies['Pillow'] = True
    except ImportError:
        pass
    
    # 检查psutil
    try:
        import psutil
        dependencies['psutil'] = True
    except ImportError:
        pass
    
    # 检查tkinter
    try:
        import tkinter
        dependencies['tkinter'] = True
    except ImportError:
        pass
    
    return dependencies


def install_dependencies():
    """安装缺失的依赖"""
    missing_deps = []
    deps = check_dependencies()
    
    for dep, installed in deps.items():
        if not installed:
            if dep == 'pywin32':
                missing_deps.append('pywin32')
            elif dep == 'Pillow':
                missing_deps.append('Pillow')
            else:
                missing_deps.append(dep)
    
    if missing_deps:
        print(f"缺少依赖: {', '.join(missing_deps)}")
        print("正在安装缺失的依赖...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_deps)
            print("依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"依赖安装失败: {e}")
            return False
    else:
        print("所有依赖已安装")
        return True


class SingleInstance:
    """单实例运行控制"""
    
    def __init__(self, app_name: str = "ClickHelper"):
        self.app_name = app_name
        self.lock_file = None
        self.is_running = False
        
        if platform.system() == "Windows":
            import tempfile
            self.lock_file = Path(tempfile.gettempdir()) / f"{app_name}.lock"
        else:
            self.lock_file = Path(f"/tmp/{app_name}.lock")
    
    def __enter__(self):
        try:
            if self.lock_file.exists():
                # 检查进程是否真的在运行
                try:
                    with open(self.lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    if self._is_process_running(pid):
                        self.is_running = True
                        return False
                    else:
                        # 进程已停止，删除锁文件
                        self.lock_file.unlink()
                except (ValueError, FileNotFoundError):
                    # 锁文件无效，删除它
                    try:
                        self.lock_file.unlink()
                    except FileNotFoundError:
                        pass
            
            # 创建新的锁文件
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            
            return True
            
        except Exception as e:
            logging.error(f"单实例检查失败: {e}")
            return True  # 出错时允许运行
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.lock_file and self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            logging.error(f"清理锁文件失败: {e}")
    
    def _is_process_running(self, pid: int) -> bool:
        """检查进程是否在运行"""
        try:
            if platform.system() == "Windows":
                import psutil
                return psutil.pid_exists(pid)
            else:
                os.kill(pid, 0)
                return True
        except (OSError, ImportError):
            return False


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """开始性能监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_worker(self):
        """监控工作线程"""
        try:
            import psutil
            current_process = psutil.Process()
            
            while self.monitoring:
                try:
                    # 获取CPU和内存使用情况
                    cpu_percent = current_process.cpu_percent()
                    memory_info = current_process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    
                    self.cpu_samples.append(cpu_percent)
                    self.memory_samples.append(memory_mb)
                    
                    # 保持最近100个样本
                    if len(self.cpu_samples) > 100:
                        self.cpu_samples = self.cpu_samples[-100:]
                    if len(self.memory_samples) > 100:
                        self.memory_samples = self.memory_samples[-100:]
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"性能监控采样失败: {e}")
                    time.sleep(5)
                    
        except ImportError:
            logging.warning("psutil未安装，无法进行性能监控")
    
    def get_stats(self) -> dict:
        """获取性能统计"""
        try:
            stats = {
                'uptime': time.time() - self.start_time,
                'cpu_avg': 0,
                'cpu_current': 0,
                'memory_avg': 0,
                'memory_current': 0
            }
            
            if self.cpu_samples:
                stats['cpu_avg'] = sum(self.cpu_samples) / len(self.cpu_samples)
                stats['cpu_current'] = self.cpu_samples[-1]
            
            if self.memory_samples:
                stats['memory_avg'] = sum(self.memory_samples) / len(self.memory_samples)
                stats['memory_current'] = self.memory_samples[-1]
            
            return stats
        except Exception as e:
            logging.error(f"获取性能统计失败: {e}")
            return {}


def create_desktop_shortcut(app_path: str, shortcut_name: str = "快速点击助手") -> bool:
    """创建桌面快捷方式（Windows）"""
    try:
        if platform.system() != "Windows":
            return False
        
        import win32com.client
        
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = app_path
        shortcut.WorkingDirectory = os.path.dirname(app_path)
        shortcut.IconLocation = app_path
        shortcut.save()
        
        logging.info(f"桌面快捷方式创建成功: {shortcut_path}")
        return True
        
    except Exception as e:
        logging.error(f"创建桌面快捷方式失败: {e}")
        return False


def open_file_location(file_path: str):
    """在文件管理器中打开文件位置"""
    try:
        if platform.system() == "Windows":
            subprocess.run(['explorer', '/select,', file_path], check=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', '-R', file_path], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', os.path.dirname(file_path)], check=True)
    except Exception as e:
        logging.error(f"打开文件位置失败: {e}")


def get_file_size_str(file_path: str) -> str:
    """获取文件大小的字符串表示"""
    try:
        size = os.path.getsize(file_path)
        
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    except Exception:
        return "未知"


def cleanup_old_files(directory: Path, pattern: str, days: int = 7):
    """清理旧文件"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    logging.info(f"清理旧文件: {file_path}")
                    
    except Exception as e:
        logging.error(f"清理旧文件失败: {e}")


def safe_divide(a: float, b: float, default: float = 0) -> float:
    """安全除法，避免除零错误"""
    try:
        return a / b if b != 0 else default
    except Exception:
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """将值限制在指定范围内"""
    return max(min_val, min(value, max_val))


def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logging.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
                        time.sleep(delay)
                    else:
                        logging.error(f"函数 {func.__name__} 所有尝试都失败")
            
            raise last_exception
        return wrapper
    return decorator
