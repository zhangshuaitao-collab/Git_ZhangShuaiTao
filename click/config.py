#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击助手 - 配置管理器
负责应用配置的保存、加载和管理
"""

import os
import json
import logging
import configparser
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class Config:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """初始化配置管理器"""
        # 设置配置目录
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # 默认配置目录：用户目录下的.click_helper文件夹
            self.config_dir = Path.home() / '.click_helper'
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.config_file = self.config_dir / 'config.ini'
        self.profiles_file = self.config_dir / 'profiles.json'
        self.log_file = self.config_dir / 'app.log'
        
        # 初始化配置解析器
        self.config_parser = configparser.ConfigParser()
        
        # 加载配置
        self.load()
        
        logging.info(f"配置管理器初始化完成，配置目录: {self.config_dir}")
    
    def load(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                self.config_parser.read(self.config_file, encoding='utf-8')
                logging.info("配置文件加载成功")
            else:
                # 创建默认配置
                self._create_default_config()
                logging.info("创建默认配置文件")
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            self._create_default_config()
    
    def save(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config_parser.write(f)
            logging.info("配置文件保存成功")
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def _create_default_config(self):
        """创建默认配置"""
        # 窗口设置
        self.config_parser['window'] = {
            'geometry': '800x600+100+100',
            'theme': 'default'
        }
        
        # 点击设置
        self.config_parser['click'] = {
            'interval': '1000',
            'count': '0',
            'type': 'left',
            'random_delay': 'False',
            'retry_on_fail': 'False'
        }
        
        # 安全设置
        self.config_parser['safety'] = {
            'mouse_protection': 'True',
            'hotkey_stop': 'True',
            'max_clicks_per_session': '10000'
        }
        
        # 日志设置
        self.config_parser['logging'] = {
            'level': 'INFO',
            'max_file_size': '10',  # MB
            'backup_count': '3'
        }
        
        # 高级设置
        self.config_parser['advanced'] = {
            'multi_point': 'False',
            'auto_save': 'True',
            'check_updates': 'True'
        }
        
        # 保存默认配置
        self.save()
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """获取配置值"""
        try:
            return self.config_parser.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """设置配置值"""
        try:
            if not self.config_parser.has_section(section):
                self.config_parser.add_section(section)
            
            self.config_parser.set(section, key, str(value))
        except Exception as e:
            logging.error(f"设置配置值失败: {e}")
    
    def get_boolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """获取布尔型配置值"""
        try:
            return self.config_parser.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """获取整型配置值"""
        try:
            return self.config_parser.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """获取浮点型配置值"""
        try:
            return self.config_parser.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback


class ProfileManager:
    """配置文件管理器"""
    
    def __init__(self, config: Config):
        """初始化配置文件管理器"""
        self.config = config
        self.profiles_file = config.profiles_file
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return {}
    
    def save_profiles(self):
        """保存配置文件"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, ensure_ascii=False, indent=2)
            logging.info("配置文件保存成功")
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def save_profile(self, name: str, profile_data: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            profile_data['created_time'] = datetime.now().isoformat()
            profile_data['last_modified'] = datetime.now().isoformat()
            
            self.profiles[name] = profile_data
            self.save_profiles()
            
            logging.info(f"配置文件保存成功: {name}")
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败 {name}: {e}")
            return False
    
    def load_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            profile = self.profiles.get(name)
            if profile:
                # 更新最后使用时间
                profile['last_used'] = datetime.now().isoformat()
                self.save_profiles()
                logging.info(f"配置文件加载成功: {name}")
            return profile
        except Exception as e:
            logging.error(f"加载配置文件失败 {name}: {e}")
            return None
    
    def delete_profile(self, name: str) -> bool:
        """删除配置文件"""
        try:
            if name in self.profiles:
                del self.profiles[name]
                self.save_profiles()
                logging.info(f"配置文件删除成功: {name}")
                return True
            return False
        except Exception as e:
            logging.error(f"删除配置文件失败 {name}: {e}")
            return False
    
    def get_profile_list(self) -> list:
        """获取配置文件列表"""
        try:
            profiles_list = []
            for name, profile in self.profiles.items():
                profiles_list.append({
                    'name': name,
                    'created_time': profile.get('created_time', ''),
                    'last_modified': profile.get('last_modified', ''),
                    'last_used': profile.get('last_used', ''),
                    'description': profile.get('description', '')
                })
            
            # 按最后使用时间排序
            profiles_list.sort(key=lambda x: x.get('last_used', ''), reverse=True)
            return profiles_list
        except Exception as e:
            logging.error(f"获取配置文件列表失败: {e}")
            return []
    
    def export_profile(self, name: str, file_path: str) -> bool:
        """导出配置文件"""
        try:
            profile = self.profiles.get(name)
            if not profile:
                return False
            
            export_data = {
                'profile_name': name,
                'export_time': datetime.now().isoformat(),
                'version': '1.0',
                'data': profile
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"配置文件导出成功: {name} -> {file_path}")
            return True
        except Exception as e:
            logging.error(f"导出配置文件失败 {name}: {e}")
            return False
    
    def import_profile(self, file_path: str, new_name: Optional[str] = None) -> bool:
        """导入配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'data' not in import_data:
                logging.error("无效的配置文件格式")
                return False
            
            profile_name = new_name or import_data.get('profile_name', 'imported_profile')
            profile_data = import_data['data']
            
            # 更新导入时间
            profile_data['imported_time'] = datetime.now().isoformat()
            
            return self.save_profile(profile_name, profile_data)
        except Exception as e:
            logging.error(f"导入配置文件失败: {e}")
            return False


class SettingsManager:
    """设置管理器"""
    
    def __init__(self, config: Config):
        """初始化设置管理器"""
        self.config = config
    
    def get_click_settings(self) -> Dict[str, Any]:
        """获取点击设置"""
        return {
            'interval': self.config.get_int('click', 'interval', 1000),
            'count': self.config.get_int('click', 'count', 0),
            'type': self.config.get('click', 'type', 'left'),
            'random_delay': self.config.get_boolean('click', 'random_delay', False),
            'retry_on_fail': self.config.get_boolean('click', 'retry_on_fail', False)
        }
    
    def set_click_settings(self, settings: Dict[str, Any]):
        """设置点击设置"""
        for key, value in settings.items():
            self.config.set('click', key, value)
        self.config.save()
    
    def get_safety_settings(self) -> Dict[str, Any]:
        """获取安全设置"""
        return {
            'mouse_protection': self.config.get_boolean('safety', 'mouse_protection', True),
            'hotkey_stop': self.config.get_boolean('safety', 'hotkey_stop', True),
            'max_clicks_per_session': self.config.get_int('safety', 'max_clicks_per_session', 10000)
        }
    
    def set_safety_settings(self, settings: Dict[str, Any]):
        """设置安全设置"""
        for key, value in settings.items():
            self.config.set('safety', key, value)
        self.config.save()
    
    def get_window_settings(self) -> Dict[str, Any]:
        """获取窗口设置"""
        return {
            'geometry': self.config.get('window', 'geometry', '800x600+100+100'),
            'theme': self.config.get('window', 'theme', 'default')
        }
    
    def set_window_settings(self, settings: Dict[str, Any]):
        """设置窗口设置"""
        for key, value in settings.items():
            self.config.set('window', key, value)
        self.config.save()
    
    def get_advanced_settings(self) -> Dict[str, Any]:
        """获取高级设置"""
        return {
            'multi_point': self.config.get_boolean('advanced', 'multi_point', False),
            'auto_save': self.config.get_boolean('advanced', 'auto_save', True),
            'check_updates': self.config.get_boolean('advanced', 'check_updates', True)
        }
    
    def set_advanced_settings(self, settings: Dict[str, Any]):
        """设置高级设置"""
        for key, value in settings.items():
            self.config.set('advanced', key, value)
        self.config.save()
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        try:
            # 备份当前配置
            backup_file = self.config.config_dir / f'config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ini'
            if self.config.config_file.exists():
                import shutil
                shutil.copy2(self.config.config_file, backup_file)
                logging.info(f"配置已备份到: {backup_file}")
            
            # 删除当前配置文件
            if self.config.config_file.exists():
                self.config.config_file.unlink()
            
            # 重新创建默认配置
            self.config._create_default_config()
            self.config.load()
            
            logging.info("设置已重置为默认值")
            return True
        except Exception as e:
            logging.error(f"重置设置失败: {e}")
            return False


class StatisticsManager:
    """统计数据管理器"""
    
    def __init__(self, config: Config):
        """初始化统计管理器"""
        self.config = config
        self.stats_file = config.config_dir / 'statistics.json'
        self.stats = self._load_statistics()
    
    def _load_statistics(self) -> Dict[str, Any]:
        """加载统计数据"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_statistics()
        except Exception as e:
            logging.error(f"加载统计数据失败: {e}")
            return self._create_default_statistics()
    
    def _create_default_statistics(self) -> Dict[str, Any]:
        """创建默认统计数据"""
        return {
            'total_sessions': 0,
            'total_clicks': 0,
            'successful_clicks': 0,
            'failed_clicks': 0,
            'total_runtime': 0,  # 秒
            'first_use_date': datetime.now().isoformat(),
            'last_use_date': '',
            'daily_stats': {},
            'session_history': []
        }
    
    def save_statistics(self):
        """保存统计数据"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存统计数据失败: {e}")
    
    def record_session(self, session_data: Dict[str, Any]):
        """记录会话数据"""
        try:
            today = datetime.now().date().isoformat()
            
            # 更新总体统计
            self.stats['total_sessions'] += 1
            self.stats['total_clicks'] += session_data.get('total_clicks', 0)
            self.stats['successful_clicks'] += session_data.get('successful_clicks', 0)
            self.stats['failed_clicks'] += session_data.get('failed_clicks', 0)
            self.stats['total_runtime'] += session_data.get('runtime', 0)
            self.stats['last_use_date'] = datetime.now().isoformat()
            
            # 更新每日统计
            if today not in self.stats['daily_stats']:
                self.stats['daily_stats'][today] = {
                    'sessions': 0,
                    'clicks': 0,
                    'runtime': 0
                }
            
            daily = self.stats['daily_stats'][today]
            daily['sessions'] += 1
            daily['clicks'] += session_data.get('total_clicks', 0)
            daily['runtime'] += session_data.get('runtime', 0)
            
            # 记录会话历史（保留最近100次）
            session_record = {
                'timestamp': datetime.now().isoformat(),
                'clicks': session_data.get('total_clicks', 0),
                'runtime': session_data.get('runtime', 0),
                'window_title': session_data.get('window_title', '')
            }
            
            self.stats['session_history'].append(session_record)
            if len(self.stats['session_history']) > 100:
                self.stats['session_history'] = self.stats['session_history'][-100:]
            
            self.save_statistics()
            logging.info("会话统计记录成功")
        except Exception as e:
            logging.error(f"记录会话统计失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        return self.stats.copy()
    
    def get_daily_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取指定天数的每日统计"""
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            daily_data = {}
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_str = date.isoformat()
                daily_data[date_str] = self.stats['daily_stats'].get(date_str, {
                    'sessions': 0,
                    'clicks': 0,
                    'runtime': 0
                })
            
            return daily_data
        except Exception as e:
            logging.error(f"获取每日统计失败: {e}")
            return {}
    
    def reset_statistics(self):
        """重置统计数据"""
        try:
            # 备份当前统计
            backup_file = self.config.config_dir / f'stats_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            if self.stats_file.exists():
                import shutil
                shutil.copy2(self.stats_file, backup_file)
                logging.info(f"统计数据已备份到: {backup_file}")
            
            # 重置统计数据
            self.stats = self._create_default_statistics()
            self.save_statistics()
            
            logging.info("统计数据已重置")
            return True
        except Exception as e:
            logging.error(f"重置统计数据失败: {e}")
            return False
