#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 窗口管理器
负责窗口选择和坐标获取功能
"""

import time
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import logging
from typing import List, Dict, Optional, Tuple, Any
import subprocess
import psutil

try:
    import win32gui
    import win32process
    import win32con
    import win32api
    import win32ui
    from PIL import Image, ImageTk
    import pyautogui
except ImportError as e:
    logging.error(f"导入窗口管理依赖库失败: {e}")
    raise ImportError(f"请安装必需的依赖库: {e}")


class WindowManager:
    """窗口管理器"""
    
    def __init__(self):
        """初始化窗口管理器"""
        self.windows = []
        self.selected_window = None
        self.coordinate_picker = None
        
        logging.info("窗口管理器初始化完成")
    
    def get_all_windows(self) -> List[Dict[str, Any]]:
        """获取所有可见窗口列表"""
        windows = []
        
        def enum_windows_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                try:
                    # 获取窗口信息
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # 获取窗口位置和大小
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    
                    # 过滤掉太小的窗口
                    if width < 50 or height < 50:
                        return True
                    
                    # 获取进程信息
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name()
                        process_path = process.exe()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                        process_name = "Unknown"
                        process_path = ""
                    
                    window_info = {
                        'hwnd': hwnd,
                        'title': title,
                        'class_name': class_name,
                        'rect': rect,
                        'width': width,
                        'height': height,
                        'process_name': process_name,
                        'process_path': process_path,
                        'pid': pid if 'pid' in locals() else 0
                    }
                    
                    windows_list.append(window_info)
                    
                except Exception as e:
                    logging.debug(f"获取窗口信息失败 {hwnd}: {e}")
            
            return True
        
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            logging.error(f"枚举窗口失败: {e}")
        
        # 按标题排序
        windows.sort(key=lambda w: w['title'].lower())
        self.windows = windows
        
        logging.info(f"找到 {len(windows)} 个可见窗口")
        return windows
    
    def select_window(self) -> Optional[Dict[str, Any]]:
        """显示窗口选择对话框"""
        try:
            # 获取所有窗口
            windows = self.get_all_windows()
            
            if not windows:
                messagebox.showwarning("警告", "没有找到可选择的窗口")
                return None
            
            # 创建选择对话框
            return self._show_window_selector(windows)
            
        except Exception as e:
            logging.error(f"选择窗口失败: {e}")
            messagebox.showerror("错误", f"选择窗口失败:\n{e}")
            return None
    
    def _show_window_selector(self, windows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """显示窗口选择对话框"""
        selected_window = None
        
        def on_select():
            nonlocal selected_window
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                hwnd = item['values'][0] if item['values'] else None
                if hwnd:
                    # 查找对应的窗口信息
                    for window in windows:
                        if window['hwnd'] == int(hwnd):
                            selected_window = window
                            break
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "请选择一个窗口")
        
        def on_cancel():
            dialog.destroy()
        
        def on_refresh():
            # 刷新窗口列表
            new_windows = self.get_all_windows()
            tree.delete(*tree.get_children())
            for window in new_windows:
                tree.insert('', 'end', values=(
                    window['hwnd'],
                    window['title'][:50] + ('...' if len(window['title']) > 50 else ''),
                    window['process_name'],
                    f"{window['width']}x{window['height']}"
                ))
        
        def on_highlight():
            """高亮选中的窗口"""
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                hwnd = item['values'][0] if item['values'] else None
                if hwnd:
                    try:
                        self._highlight_window(int(hwnd))
                    except Exception as e:
                        logging.error(f"高亮窗口失败: {e}")
        
        # 创建对话框
        dialog = tk.Toplevel()
        dialog.title("选择目标窗口")
        dialog.geometry("700x500")
        dialog.resizable(True, True)
        dialog.grab_set()  # 模态对话框
        
        # 工具栏
        toolbar = ttk.Frame(dialog)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="刷新列表", command=on_refresh).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="高亮窗口", command=on_highlight).pack(side=tk.LEFT, padx=(10,0))
        
        # 创建树形视图
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 设置列
        columns = ('hwnd', 'title', 'process', 'size')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        tree.heading('hwnd', text='句柄')
        tree.heading('title', text='窗口标题')
        tree.heading('process', text='进程名')
        tree.heading('size', text='大小')
        
        tree.column('hwnd', width=80, anchor=tk.CENTER)
        tree.column('title', width=350)
        tree.column('process', width=120)
        tree.column('size', width=80, anchor=tk.CENTER)
        
        # 添加数据
        for window in windows:
            tree.insert('', 'end', values=(
                window['hwnd'],
                window['title'][:50] + ('...' if len(window['title']) > 50 else ''),
                window['process_name'],
                f"{window['width']}x{window['height']}"
            ))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击选择
        tree.bind('<Double-1>', lambda e: on_select())
        
        # 按钮框
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="选择", command=on_select).pack(side=tk.RIGHT, padx=(5,0))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)
        
        # 等待对话框关闭
        dialog.wait_window()
        
        return selected_window
    
    def _highlight_window(self, hwnd: int, duration: float = 2.0):
        """高亮显示指定窗口"""
        try:
            # 获取窗口位置
            rect = win32gui.GetWindowRect(hwnd)
            
            # 创建高亮效果（闪烁窗口）
            for _ in range(3):
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                time.sleep(0.2)
            
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(hwnd)
            
        except Exception as e:
            logging.error(f"高亮窗口失败: {e}")
    
    def select_coordinates(self, window: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """选择点击坐标"""
        try:
            if not window:
                messagebox.showwarning("警告", "请先选择目标窗口")
                return None
            
            # 激活目标窗口
            self._activate_window(window)
            time.sleep(0.5)  # 等待窗口激活
            
            # 启动坐标选择器
            picker = CoordinatePicker(window)
            return picker.get_coordinates()
            
        except Exception as e:
            logging.error(f"选择坐标失败: {e}")
            messagebox.showerror("错误", f"选择坐标失败:\n{e}")
            return None
    
    def _activate_window(self, window: Dict[str, Any]):
        """激活指定窗口"""
        try:
            hwnd = window['hwnd']
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
        except Exception as e:
            logging.error(f"激活窗口失败: {e}")
    
    def capture_window_screenshot(self, window: Dict[str, Any]) -> Optional[Image.Image]:
        """截取指定窗口的屏幕截图"""
        try:
            hwnd = window['hwnd']
            
            # 获取窗口位置和大小
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # 创建设备上下文
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # 创建位图对象
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # 截图
            result = win32gui.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
            
            if result == 1:
                # 获取位图数据
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                
                # 转换为PIL图像
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                # 清理资源
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return img
            else:
                logging.warning("PrintWindow失败，使用屏幕截图")
                # 使用pyautogui截取区域
                screenshot = pyautogui.screenshot(region=(rect[0], rect[1], width, height))
                return screenshot
                
        except Exception as e:
            logging.error(f"截取窗口截图失败: {e}")
            return None


class CoordinatePicker:
    """坐标选择器"""
    
    def __init__(self, window: Dict[str, Any]):
        """初始化坐标选择器"""
        self.window = window
        self.selected_coordinates = None
        self.root = None
        self.canvas = None
        self.screenshot = None
        
    def get_coordinates(self) -> Optional[Dict[str, int]]:
        """获取选择的坐标"""
        try:
            # 截取窗口截图
            window_manager = WindowManager()
            self.screenshot = window_manager.capture_window_screenshot(self.window)
            
            if not self.screenshot:
                messagebox.showerror("错误", "无法截取窗口截图")
                return None
            
            # 创建选择界面
            self._create_picker_window()
            
            # 等待选择完成
            self.root.wait_window()
            
            return self.selected_coordinates
            
        except Exception as e:
            logging.error(f"坐标选择失败: {e}")
            return None
    
    def _create_picker_window(self):
        """创建坐标选择窗口"""
        self.root = tk.Toplevel()
        self.root.title(f"选择点击坐标 - {self.window['title'][:30]}...")
        self.root.attributes('-topmost', True)
        
        # 设置窗口大小
        img_width, img_height = self.screenshot.size
        max_width, max_height = 800, 600
        
        # 计算缩放比例
        scale_x = max_width / img_width if img_width > max_width else 1
        scale_y = max_height / img_height if img_height > max_height else 1
        scale = min(scale_x, scale_y)
        
        display_width = int(img_width * scale)
        display_height = int(img_height * scale)
        
        self.root.geometry(f"{display_width + 20}x{display_height + 80}")
        
        # 指示标签
        instruction = ttk.Label(
            self.root, 
            text="请点击要自动点击的位置。点击后按'确认'按钮完成选择。",
            font=('Arial', 10)
        )
        instruction.pack(pady=10)
        
        # 创建画布
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=display_width,
            height=display_height,
            cursor="cross"
        )
        
        # 缩放截图并显示
        if scale != 1:
            resized_screenshot = self.screenshot.resize(
                (display_width, display_height), 
                Image.Resampling.LANCZOS
            )
        else:
            resized_screenshot = self.screenshot
        
        # 转换为tkinter可用的图片
        self.tk_image = ImageTk.PhotoImage(resized_screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.pack()
        
        # 绑定点击事件
        self.canvas.bind('<Button-1>', lambda e: self._on_canvas_click(e, scale))
        
        # 按钮框
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.coord_label = ttk.Label(button_frame, text="坐标: 未选择")
        self.coord_label.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="取消", command=self._on_cancel).pack(side=tk.RIGHT)
        self.confirm_btn = ttk.Button(
            button_frame, 
            text="确认", 
            command=self._on_confirm, 
            state='disabled'
        )
        self.confirm_btn.pack(side=tk.RIGHT, padx=(0,10))
    
    def _on_canvas_click(self, event, scale):
        """处理画布点击事件"""
        try:
            # 计算实际坐标（考虑缩放）
            actual_x = int(event.x / scale)
            actual_y = int(event.y / scale)
            
            # 确保坐标在图片范围内
            img_width, img_height = self.screenshot.size
            actual_x = max(0, min(actual_x, img_width - 1))
            actual_y = max(0, min(actual_y, img_height - 1))
            
            # 保存坐标
            self.selected_coordinates = {'x': actual_x, 'y': actual_y}
            
            # 清除之前的标记
            self.canvas.delete('crosshair')
            
            # 在点击位置画十字标记
            size = 10
            self.canvas.create_line(
                event.x - size, event.y, event.x + size, event.y,
                fill='red', width=2, tags='crosshair'
            )
            self.canvas.create_line(
                event.x, event.y - size, event.x, event.y + size,
                fill='red', width=2, tags='crosshair'
            )
            
            # 画一个小圆圈
            self.canvas.create_oval(
                event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                outline='red', width=2, tags='crosshair'
            )
            
            # 更新标签和按钮状态
            self.coord_label.config(text=f"坐标: ({actual_x}, {actual_y})")
            self.confirm_btn.config(state='normal')
            
            logging.debug(f"选择坐标: ({actual_x}, {actual_y})")
            
        except Exception as e:
            logging.error(f"处理画布点击失败: {e}")
    
    def _on_confirm(self):
        """确认选择"""
        self.root.destroy()
    
    def _on_cancel(self):
        """取消选择"""
        self.selected_coordinates = None
        self.root.destroy()


class WindowMonitor:
    """窗口监视器 - 监控目标窗口状态"""
    
    def __init__(self, window: Dict[str, Any], callback=None):
        """初始化窗口监视器"""
        self.window = window
        self.callback = callback
        self.monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
    
    def start_monitoring(self):
        """开始监控窗口"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.stop_event.clear()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_worker,
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控窗口"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
    
    def _monitor_worker(self):
        """监控工作线程"""
        last_state = self._get_window_state()
        
        while not self.stop_event.is_set():
            try:
                current_state = self._get_window_state()
                
                # 检查状态变化
                if current_state != last_state:
                    if self.callback:
                        self.callback('window_state_changed', {
                            'previous': last_state,
                            'current': current_state
                        })
                    last_state = current_state
                
                # 等待间隔
                if self.stop_event.wait(1.0):
                    break
                    
            except Exception as e:
                logging.error(f"窗口监控出错: {e}")
                if self.callback:
                    self.callback('monitor_error', {'error': str(e)})
                break
    
    def _get_window_state(self) -> Dict[str, Any]:
        """获取窗口当前状态"""
        try:
            hwnd = self.window['hwnd']
            
            state = {
                'exists': win32gui.IsWindow(hwnd),
                'visible': win32gui.IsWindowVisible(hwnd),
                'rect': win32gui.GetWindowRect(hwnd) if win32gui.IsWindow(hwnd) else None,
                'title': win32gui.GetWindowText(hwnd) if win32gui.IsWindow(hwnd) else "",
                'minimized': win32gui.IsIconic(hwnd) if win32gui.IsWindow(hwnd) else False
            }
            
            return state
            
        except Exception as e:
            logging.error(f"获取窗口状态失败: {e}")
            return {
                'exists': False,
                'visible': False,
                'rect': None,
                'title': "",
                'minimized': True
            }
