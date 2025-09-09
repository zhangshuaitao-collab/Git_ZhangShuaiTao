#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 自动点击引擎
负责执行实际的鼠标点击操作
"""

import time
import threading
import random
import logging
from datetime import datetime
from typing import Dict, Callable, Optional, Any

try:
    import pyautogui
    import win32gui
    import win32con
    import win32api
except ImportError as e:
    logging.error(f"导入点击引擎依赖库失败: {e}")
    raise ImportError(f"请安装必需的依赖库: {e}")

class AutoClicker:
    """自动点击引擎"""
    
    def __init__(self):
        """初始化点击器"""
        # 设置pyautogui安全参数
        pyautogui.FAILSAFE = True  # 鼠标移到左上角停止
        pyautogui.PAUSE = 0.1      # 每次操作间隔
        
        # 状态变量
        self.is_clicking = False
        self.click_thread = None
        self.stop_event = threading.Event()
        
        # 统计数据
        self.stats = {
            'total_clicks': 0,
            'successful_clicks': 0,
            'failed_clicks': 0,
            'start_time': None,
            'last_click_time': None
        }
        
        # 回调函数
        self.callback = None
        
        logging.info("自动点击引擎初始化完成")
    
    def start_clicking(self, params: Dict[str, Any], callback: Optional[Callable] = None):
        """
        开始自动点击
        
        Args:
            params: 点击参数字典
            callback: 事件回调函数
        """
        if self.is_clicking:
            raise Exception("点击器已在运行中")
        
        # 验证参数
        self._validate_params(params)
        
        # 设置回调
        self.callback = callback
        
        # 重置状态
        self.stop_event.clear()
        self.is_clicking = True
        self.stats['start_time'] = datetime.now()
        
        # 启动点击线程
        self.click_thread = threading.Thread(
            target=self._click_worker,
            args=(params,),
            daemon=True
        )
        self.click_thread.start()
        
        logging.info(f"开始自动点击: {params}")
    
    def stop_clicking(self):
        """停止自动点击"""
        if not self.is_clicking:
            return
        
        self.stop_event.set()
        self.is_clicking = False
        
        # 等待线程结束
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=2)
        
        logging.info("自动点击已停止")
    
    def test_click(self, window: Dict[str, Any], coordinates: Dict[str, int]) -> bool:
        """
        测试点击
        
        Args:
            window: 窗口信息
            coordinates: 坐标信息
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 激活窗口
            self._activate_window(window)
            
            # 计算绝对坐标
            abs_x, abs_y = self._calculate_absolute_coordinates(window, coordinates)
            
            # 执行点击
            pyautogui.click(abs_x, abs_y)
            
            logging.info(f"测试点击成功: ({abs_x}, {abs_y})")
            return True
            
        except Exception as e:
            logging.error(f"测试点击失败: {e}")
            return False
    
    def _validate_params(self, params: Dict[str, Any]):
        """验证点击参数"""
        required_keys = ['window', 'coordinates', 'interval', 'max_clicks', 'click_type']
        
        for key in required_keys:
            if key not in params:
                raise ValueError(f"缺少必需参数: {key}")
        
        # 验证具体参数
        if params['interval'] < 100:
            raise ValueError("点击间隔不能小于100毫秒")
        
        if params['max_clicks'] < 0:
            raise ValueError("点击次数不能为负数")
        
        if params['click_type'] not in ['left', 'right', 'middle']:
            raise ValueError("无效的点击类型")
    
    def _click_worker(self, params: Dict[str, Any]):
        """点击工作线程"""
        try:
            window = params['window']
            coordinates = params['coordinates']
            interval = params['interval'] / 1000.0  # 转换为秒
            max_clicks = params['max_clicks']
            click_type = params['click_type']
            random_delay = params.get('random_delay', False)
            retry_on_fail = params.get('retry_on_fail', False)
            
            click_count = 0
            
            while not self.stop_event.is_set():
                try:
                    # 检查是否达到最大点击次数
                    if max_clicks > 0 and click_count >= max_clicks:
                        break
                    
                    # 执行点击
                    success = self._perform_click(window, coordinates, click_type)
                    
                    if success:
                        click_count += 1
                        self.stats['successful_clicks'] += 1
                        self.stats['total_clicks'] += 1
                        self.stats['last_click_time'] = datetime.now()
                        
                        # 触发回调
                        if self.callback:
                            self.callback('click', {
                                'count': click_count,
                                'coordinates': coordinates,
                                'timestamp': self.stats['last_click_time']
                            })
                        
                        logging.debug(f"点击成功 #{click_count}: {coordinates}")
                    else:
                        self.stats['failed_clicks'] += 1
                        
                        if retry_on_fail:
                            logging.warning("点击失败，将重试")
                            continue
                        else:
                            logging.error("点击失败，停止执行")
                            break
                    
                    # 等待间隔
                    delay = interval
                    if random_delay:
                        # 添加10%-50%的随机延迟
                        delay = interval * (1 + random.uniform(0.1, 0.5))
                    
                    if self.stop_event.wait(delay):
                        break
                        
                except Exception as e:
                    logging.error(f"点击过程中发生错误: {e}")
                    self.stats['failed_clicks'] += 1
                    
                    if not retry_on_fail:
                        break
            
            # 完成回调
            if self.callback:
                self.callback('complete', {
                    'total': click_count,
                    'successful': self.stats['successful_clicks'],
                    'failed': self.stats['failed_clicks'],
                    'duration': (datetime.now() - self.stats['start_time']).total_seconds()
                })
            
            logging.info(f"点击完成: 总计{click_count}次")
            
        except Exception as e:
            logging.error(f"点击线程异常: {e}")
            if self.callback:
                self.callback('error', {'message': str(e)})
        finally:
            self.is_clicking = False
    
    def _perform_click(self, window: Dict[str, Any], coordinates: Dict[str, int], 
                      click_type: str = 'left') -> bool:
        """
        执行单次点击
        
        Args:
            window: 窗口信息
            coordinates: 坐标信息
            click_type: 点击类型
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 检查窗口是否仍然存在
            if not self._is_window_valid(window):
                logging.warning("目标窗口不存在或不可见")
                return False
            
            # 激活窗口
            self._activate_window(window)
            
            # 稍作等待确保窗口激活
            time.sleep(0.1)
            
            # 计算绝对坐标
            abs_x, abs_y = self._calculate_absolute_coordinates(window, coordinates)
            
            # 检查坐标是否在屏幕范围内
            screen_width, screen_height = pyautogui.size()
            if not (0 <= abs_x < screen_width and 0 <= abs_y < screen_height):
                logging.warning(f"坐标超出屏幕范围: ({abs_x}, {abs_y})")
                return False
            
            # 执行点击
            if click_type == 'left':
                pyautogui.click(abs_x, abs_y, button='left')
            elif click_type == 'right':
                pyautogui.click(abs_x, abs_y, button='right')
            elif click_type == 'middle':
                pyautogui.click(abs_x, abs_y, button='middle')
            else:
                logging.error(f"未知的点击类型: {click_type}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"执行点击失败: {e}")
            return False
    
    def _activate_window(self, window: Dict[str, Any]):
        """激活指定窗口"""
        try:
            hwnd = window.get('hwnd')
            if hwnd:
                # 使用Windows API激活窗口
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
            else:
                # 尝试通过标题查找窗口
                title = window.get('title', '')
                hwnd = win32gui.FindWindow(None, title)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                else:
                    logging.warning(f"无法找到窗口: {title}")
                    
        except Exception as e:
            logging.error(f"激活窗口失败: {e}")
    
    def _calculate_absolute_coordinates(self, window: Dict[str, Any], 
                                      coordinates: Dict[str, int]) -> tuple:
        """
        计算绝对屏幕坐标
        
        Args:
            window: 窗口信息
            coordinates: 相对坐标
            
        Returns:
            tuple: (绝对x坐标, 绝对y坐标)
        """
        try:
            hwnd = window.get('hwnd')
            if hwnd:
                # 获取窗口位置
                rect = win32gui.GetWindowRect(hwnd)
                window_x, window_y = rect[0], rect[1]
                
                # 计算绝对坐标
                abs_x = window_x + coordinates['x']
                abs_y = window_y + coordinates['y']
                
                return abs_x, abs_y
            else:
                # 如果没有句柄，直接使用坐标（假设是绝对坐标）
                return coordinates['x'], coordinates['y']
                
        except Exception as e:
            logging.error(f"计算坐标失败: {e}")
            return coordinates['x'], coordinates['y']
    
    def _is_window_valid(self, window: Dict[str, Any]) -> bool:
        """检查窗口是否仍然有效"""
        try:
            hwnd = window.get('hwnd')
            if hwnd:
                # 检查窗口是否存在且可见
                return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)
            else:
                # 尝试通过标题查找窗口
                title = window.get('title', '')
                found_hwnd = win32gui.FindWindow(None, title)
                return found_hwnd != 0
        except Exception as e:
            logging.error(f"检查窗口有效性失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if self.stats['start_time']:
            if self.is_clicking:
                stats['duration'] = (datetime.now() - self.stats['start_time']).total_seconds()
            else:
                stats['duration'] = 0
        
        # 计算点击速率 (次/分钟)
        if stats.get('duration', 0) > 0:
            stats['click_rate'] = (stats['successful_clicks'] / stats['duration']) * 60
        else:
            stats['click_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_clicks': 0,
            'successful_clicks': 0,
            'failed_clicks': 0,
            'start_time': None,
            'last_click_time': None
        }
        logging.info("统计信息已重置")


class ClickPattern:
    """点击模式类 - 支持复杂的点击序列"""
    
    def __init__(self):
        self.patterns = []
    
    def add_click(self, coordinates: Dict[str, int], delay: float = 0, 
                  click_type: str = 'left'):
        """添加点击到模式"""
        self.patterns.append({
            'coordinates': coordinates,
            'delay': delay,
            'click_type': click_type
        })
    
    def execute(self, window: Dict[str, Any], clicker: AutoClicker) -> bool:
        """执行点击模式"""
        try:
            for pattern in self.patterns:
                if pattern['delay'] > 0:
                    time.sleep(pattern['delay'])
                
                success = clicker._perform_click(
                    window, 
                    pattern['coordinates'], 
                    pattern['click_type']
                )
                
                if not success:
                    return False
            
            return True
        except Exception as e:
            logging.error(f"执行点击模式失败: {e}")
            return False


class MouseProtection:
    """鼠标保护类 - 检测鼠标移动并提供保护机制"""
    
    def __init__(self):
        self.last_position = pyautogui.position()
        self.protection_enabled = True
        self.sensitivity = 10  # 移动像素阈值
    
    def check_movement(self) -> bool:
        """检查鼠标是否移动"""
        if not self.protection_enabled:
            return False
        
        current_pos = pyautogui.position()
        moved_distance = abs(current_pos.x - self.last_position.x) + \
                        abs(current_pos.y - self.last_position.y)
        
        if moved_distance > self.sensitivity:
            self.last_position = current_pos
            return True
        
        return False
    
    def update_position(self):
        """更新当前鼠标位置"""
        self.last_position = pyautogui.position()
    
    def enable(self):
        """启用鼠标保护"""
        self.protection_enabled = True
        self.update_position()
    
    def disable(self):
        """禁用鼠标保护"""
        self.protection_enabled = False
