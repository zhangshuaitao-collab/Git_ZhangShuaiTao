#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 图形用户界面
基于tkinter的现代化GUI界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from datetime import datetime
import os

try:
    from clicker import AutoClicker
    from window_manager import WindowManager
    from utils import format_time, validate_number
except ImportError as e:
    logging.error(f"导入GUI依赖模块失败: {e}")

class ClickerGUI:
    """点击器图形用户界面"""
    
    def __init__(self, root, config):
        """初始化GUI"""
        self.root = root
        self.config = config
        
        # 初始化组件
        self.clicker = AutoClicker()
        self.window_manager = WindowManager()
        
        # 状态变量
        self.is_clicking = False
        self.click_count = 0
        self.selected_window = None
        self.selected_coordinates = None
        
        # GUI变量
        self.setup_variables()
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_settings()
        
        logging.info("GUI初始化完成")
    
    def setup_variables(self):
        """设置GUI变量"""
        self.var_interval = tk.StringVar(value="1000")
        self.var_click_count = tk.StringVar(value="0")
        self.var_click_type = tk.StringVar(value="left")
        self.var_window_title = tk.StringVar(value="未选择窗口")
        self.var_coordinates = tk.StringVar(value="未选择坐标")
        self.var_status = tk.StringVar(value="就绪")
        self.var_total_clicks = tk.StringVar(value="总点击数: 0")
    
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        self.create_main_frame()
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主要内容区域
        self.create_content_area()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_main_frame(self):
        """创建主框架"""
        # 主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_menu(self):
        """创建菜单栏"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置", command=self.save_config, accelerator="Ctrl+S")
        file_menu.add_command(label="加载配置", command=self.load_config, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="导出日志", command=self.export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Alt+F4")
        
        # 工具菜单
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="窗口列表", command=self.show_window_list)
        tools_menu.add_command(label="坐标获取器", command=self.open_coordinate_picker)
        tools_menu.add_command(label="测试点击", command=self.test_click)
        
        # 帮助菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # 主要操作按钮
        ttk.Button(self.toolbar, text="🎯 选择窗口", 
                  command=self.select_window, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="📍 选择坐标", 
                  command=self.select_coordinates, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="▶️ 开始点击", 
                  command=self.start_clicking, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="⏹️ 停止点击", 
                  command=self.stop_clicking, width=12).pack(side=tk.LEFT, padx=2)
        
        # 右侧按钮
        ttk.Button(self.toolbar, text="💾 保存", 
                  command=self.save_config, width=8).pack(side=tk.RIGHT, padx=2)
        ttk.Button(self.toolbar, text="📁 加载", 
                  command=self.load_config, width=8).pack(side=tk.RIGHT, padx=2)
    
    def create_content_area(self):
        """创建主要内容区域"""
        # 创建笔记本容器（选项卡）
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基础设置选项卡
        self.create_basic_tab()
        
        # 高级设置选项卡
        self.create_advanced_tab()
        
        # 日志查看选项卡
        self.create_log_tab()
        
        # 统计信息选项卡
        self.create_stats_tab()
    
    def create_basic_tab(self):
        """创建基础设置选项卡"""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="基础设置")
        
        # 目标选择区域
        target_frame = ttk.LabelFrame(basic_frame, text="目标选择", padding=10)
        target_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 窗口选择
        ttk.Label(target_frame, text="目标窗口:").pack(anchor=tk.W)
        window_frame = ttk.Frame(target_frame)
        window_frame.pack(fill=tk.X, pady=2)
        ttk.Entry(window_frame, textvariable=self.var_window_title, 
                 state='readonly', width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(window_frame, text="选择", 
                  command=self.select_window, width=8).pack(side=tk.RIGHT, padx=(5,0))
        
        # 坐标选择
        ttk.Label(target_frame, text="点击坐标:").pack(anchor=tk.W, pady=(10,0))
        coord_frame = ttk.Frame(target_frame)
        coord_frame.pack(fill=tk.X, pady=2)
        ttk.Entry(coord_frame, textvariable=self.var_coordinates, 
                 state='readonly', width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(coord_frame, text="选择", 
                  command=self.select_coordinates, width=8).pack(side=tk.RIGHT, padx=(5,0))
        
        # 点击参数设置区域
        params_frame = ttk.LabelFrame(basic_frame, text="点击参数", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 参数行1
        params_row1 = ttk.Frame(params_frame)
        params_row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(params_row1, text="点击间隔(毫秒):").pack(side=tk.LEFT)
        interval_spinbox = ttk.Spinbox(params_row1, from_=100, to=10000, increment=100,
                                      textvariable=self.var_interval, width=10)
        interval_spinbox.pack(side=tk.LEFT, padx=(5,20))
        
        ttk.Label(params_row1, text="点击次数(0=无限):").pack(side=tk.LEFT)
        count_spinbox = ttk.Spinbox(params_row1, from_=0, to=9999, increment=1,
                                   textvariable=self.var_click_count, width=10)
        count_spinbox.pack(side=tk.LEFT, padx=(5,0))
        
        # 参数行2
        params_row2 = ttk.Frame(params_frame)
        params_row2.pack(fill=tk.X, pady=10)
        
        ttk.Label(params_row2, text="鼠标键:").pack(side=tk.LEFT)
        click_type_combo = ttk.Combobox(params_row2, textvariable=self.var_click_type,
                                       values=["left", "right", "middle"], 
                                       state="readonly", width=10)
        click_type_combo.pack(side=tk.LEFT, padx=(5,20))
        
        # 控制按钮区域
        control_frame = ttk.LabelFrame(basic_frame, text="控制操作", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        self.start_btn = ttk.Button(button_frame, text="▶️ 开始点击", 
                                   command=self.start_clicking, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ 停止点击", 
                                  command=self.stop_clicking, width=15, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🧪 测试点击", 
                  command=self.test_click, width=15).pack(side=tk.LEFT, padx=5)
    
    def create_advanced_tab(self):
        """创建高级设置选项卡"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="高级设置")
        
        # 高级点击选项
        click_frame = ttk.LabelFrame(advanced_frame, text="高级点击选项", padding=10)
        click_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 多点点击
        self.var_multi_point = tk.BooleanVar()
        ttk.Checkbutton(click_frame, text="启用多点点击", 
                       variable=self.var_multi_point).pack(anchor=tk.W)
        
        # 随机延迟
        self.var_random_delay = tk.BooleanVar()
        ttk.Checkbutton(click_frame, text="启用随机延迟", 
                       variable=self.var_random_delay).pack(anchor=tk.W, pady=(5,0))
        
        # 失败重试
        self.var_retry_on_fail = tk.BooleanVar()
        ttk.Checkbutton(click_frame, text="点击失败时重试", 
                       variable=self.var_retry_on_fail).pack(anchor=tk.W, pady=(5,0))
        
        # 安全设置
        safety_frame = ttk.LabelFrame(advanced_frame, text="安全设置", padding=10)
        safety_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 鼠标保护
        self.var_mouse_protection = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="启用鼠标移动保护（鼠标移动时自动停止）", 
                       variable=self.var_mouse_protection).pack(anchor=tk.W)
        
        # 快捷键停止
        self.var_hotkey_stop = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="启用快捷键紧急停止 (Ctrl+Shift+Space)", 
                       variable=self.var_hotkey_stop).pack(anchor=tk.W, pady=(5,0))
    
    def create_log_tab(self):
        """创建日志查看选项卡"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="运行日志")
        
        # 工具栏
        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_toolbar, text="刷新", command=self.refresh_logs).pack(side=tk.LEFT)
        ttk.Button(log_toolbar, text="清空", command=self.clear_logs).pack(side=tk.LEFT, padx=(5,0))
        ttk.Button(log_toolbar, text="导出", command=self.export_logs).pack(side=tk.LEFT, padx=(5,0))
        
        # 日志显示区域
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文本框和滚动条
        self.log_text = tk.Text(log_text_frame, wrap=tk.WORD, state='disabled')
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_stats_tab(self):
        """创建统计信息选项卡"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="统计信息")
        
        # 实时统计
        realtime_frame = ttk.LabelFrame(stats_frame, text="实时统计", padding=10)
        realtime_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(realtime_frame, textvariable=self.var_total_clicks, 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        self.var_click_rate = tk.StringVar(value="点击速率: 0 次/分钟")
        ttk.Label(realtime_frame, textvariable=self.var_click_rate).pack(anchor=tk.W, pady=(5,0))
        
        self.var_running_time = tk.StringVar(value="运行时间: 00:00:00")
        ttk.Label(realtime_frame, textvariable=self.var_running_time).pack(anchor=tk.W, pady=(5,0))
        
        # 会话统计
        session_frame = ttk.LabelFrame(stats_frame, text="会话统计", padding=10)
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 统计树形视图
        self.stats_tree = ttk.Treeview(session_frame, columns=('value',), show='tree headings', height=10)
        self.stats_tree.heading('#0', text='项目', anchor=tk.W)
        self.stats_tree.heading('value', text='数值', anchor=tk.W)
        self.stats_tree.pack(fill=tk.BOTH, expand=True)
        
        # 初始化统计数据
        self.init_stats_tree()
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 状态标签
        ttk.Label(self.status_frame, textvariable=self.var_status).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5)
    
    def init_stats_tree(self):
        """初始化统计树"""
        items = [
            ("本次会话", ""),
            ("  点击总数", "0"),
            ("  成功点击", "0"), 
            ("  失败点击", "0"),
            ("  平均间隔", "0ms"),
            ("历史统计", ""),
            ("  总使用次数", "0"),
            ("  总点击次数", "0"),
            ("  最后使用", "从未")
        ]
        
        for item, value in items:
            self.stats_tree.insert('', 'end', text=item, values=(value,))
    
    # ========== 功能方法 ==========
    
    def select_window(self):
        """选择目标窗口"""
        try:
            window = self.window_manager.select_window()
            if window:
                self.selected_window = window
                self.var_window_title.set(f"{window['title'][:50]}...")
                logging.info(f"选择窗口: {window['title']}")
                self.update_status("窗口选择成功")
            else:
                self.update_status("窗口选择取消")
        except Exception as e:
            logging.error(f"选择窗口失败: {e}")
            messagebox.showerror("错误", f"选择窗口失败:\n{e}")
    
    def select_coordinates(self):
        """选择点击坐标"""
        if not self.selected_window:
            messagebox.showwarning("警告", "请先选择目标窗口")
            return
        
        try:
            coords = self.window_manager.select_coordinates(self.selected_window)
            if coords:
                self.selected_coordinates = coords
                self.var_coordinates.set(f"({coords['x']}, {coords['y']})")
                logging.info(f"选择坐标: {coords}")
                self.update_status("坐标选择成功")
            else:
                self.update_status("坐标选择取消")
        except Exception as e:
            logging.error(f"选择坐标失败: {e}")
            messagebox.showerror("错误", f"选择坐标失败:\n{e}")
    
    def start_clicking(self):
        """开始自动点击"""
        if not self.validate_inputs():
            return
        
        try:
            # 设置点击参数
            params = {
                'window': self.selected_window,
                'coordinates': self.selected_coordinates,
                'interval': int(self.var_interval.get()),
                'max_clicks': int(self.var_click_count.get()),
                'click_type': self.var_click_type.get(),
                'random_delay': self.var_random_delay.get(),
                'retry_on_fail': self.var_retry_on_fail.get()
            }
            
            # 开始点击
            self.clicker.start_clicking(params, callback=self.on_click_event)
            
            self.is_clicking = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.progress.start()
            
            self.update_status("正在点击...")
            logging.info("开始自动点击")
            
        except Exception as e:
            logging.error(f"开始点击失败: {e}")
            messagebox.showerror("错误", f"开始点击失败:\n{e}")
    
    def stop_clicking(self):
        """停止自动点击"""
        try:
            self.clicker.stop_clicking()
            self.is_clicking = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.progress.stop()
            
            self.update_status("点击已停止")
            logging.info("停止自动点击")
            
        except Exception as e:
            logging.error(f"停止点击失败: {e}")
    
    def test_click(self):
        """测试点击"""
        if not self.validate_inputs():
            return
        
        try:
            success = self.clicker.test_click(self.selected_window, self.selected_coordinates)
            if success:
                messagebox.showinfo("成功", "测试点击成功！")
            else:
                messagebox.showwarning("失败", "测试点击失败，请检查设置")
        except Exception as e:
            logging.error(f"测试点击失败: {e}")
            messagebox.showerror("错误", f"测试点击失败:\n{e}")
    
    def validate_inputs(self):
        """验证输入参数"""
        if not self.selected_window:
            messagebox.showwarning("警告", "请先选择目标窗口")
            return False
        
        if not self.selected_coordinates:
            messagebox.showwarning("警告", "请先选择点击坐标")
            return False
        
        try:
            interval = int(self.var_interval.get())
            if interval < 100:
                messagebox.showwarning("警告", "点击间隔不能小于100毫秒")
                return False
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的间隔时间")
            return False
        
        try:
            max_clicks = int(self.var_click_count.get())
            if max_clicks < 0:
                messagebox.showwarning("警告", "点击次数不能为负数")
                return False
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的点击次数")
            return False
        
        return True
    
    def on_click_event(self, event_type, data):
        """处理点击事件回调"""
        if event_type == 'click':
            self.click_count += 1
            self.var_total_clicks.set(f"总点击数: {self.click_count}")
        elif event_type == 'complete':
            self.stop_clicking()
            messagebox.showinfo("完成", f"点击完成！共点击 {data.get('total', 0)} 次")
        elif event_type == 'error':
            self.stop_clicking()
            messagebox.showerror("错误", f"点击过程中发生错误:\n{data.get('message', '未知错误')}")
    
    def update_status(self, message):
        """更新状态"""
        self.var_status.set(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.root.update_idletasks()
    
    def toggle_clicking(self, event=None):
        """切换点击状态（快捷键）"""
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def stop_all(self):
        """停止所有操作"""
        self.stop_clicking()
    
    def save_config(self):
        """保存配置"""
        try:
            # TODO: 实现配置保存
            messagebox.showinfo("提示", "配置保存功能正在开发中")
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
            messagebox.showerror("错误", f"保存配置失败:\n{e}")
    
    def load_config(self):
        """加载配置"""
        try:
            # TODO: 实现配置加载
            messagebox.showinfo("提示", "配置加载功能正在开发中")
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            messagebox.showerror("错误", f"加载配置失败:\n{e}")
    
    def load_settings(self):
        """加载设置"""
        try:
            # 从配置文件加载设置
            self.var_interval.set(self.config.get('click', 'interval', fallback='1000'))
            self.var_click_count.set(self.config.get('click', 'count', fallback='0'))
            self.var_click_type.set(self.config.get('click', 'type', fallback='left'))
        except Exception as e:
            logging.error(f"加载设置失败: {e}")
    
    def refresh_logs(self):
        """刷新日志显示"""
        # TODO: 实现日志刷新
        pass
    
    def clear_logs(self):
        """清空日志"""
        # TODO: 实现日志清空
        pass
    
    def export_logs(self):
        """导出日志"""
        # TODO: 实现日志导出
        pass
    
    def show_window_list(self):
        """显示窗口列表"""
        # TODO: 实现窗口列表显示
        pass
    
    def open_coordinate_picker(self):
        """打开坐标选择器"""
        # TODO: 实现独立的坐标选择器
        pass
    
    def show_help(self):
        """显示帮助"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x400")
        
        help_text = """
快速点击助手使用说明

1. 选择目标窗口：
   点击"选择窗口"按钮，然后点击要操作的软件窗口

2. 选择点击位置：
   点击"选择坐标"按钮，在目标窗口中点击要自动点击的位置

3. 设置点击参数：
   - 点击间隔：两次点击之间的时间间隔（毫秒）
   - 点击次数：总共要点击的次数，0表示无限点击
   - 鼠标键：选择左键、右键或中键点击

4. 开始点击：
   点击"开始点击"按钮启动自动点击功能

5. 停止点击：
   点击"停止点击"按钮或按Ctrl+Shift+Space快捷键停止

注意事项：
- 请确保目标软件窗口保持可见状态
- 建议先使用"测试点击"确认设置正确
- 可以随时使用快捷键或按钮停止点击
        """
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state='disabled')
    
    def show_about(self):
        """显示关于信息"""
        about_text = """快速点击助手 v1.0.0

一个强大的桌面自动点击软件

主要特性：
• 支持任意软件窗口的按钮点击
• 灵活的点击参数设置
• 安全保护机制
• 详细的操作日志
• 配置保存和加载

技术支持：
如遇问题请查看运行日志获取详细信息

© 2024 快速点击助手
        """
        messagebox.showinfo("关于", about_text)
