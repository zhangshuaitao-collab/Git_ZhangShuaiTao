# 🖱️ 快速点击助手 - 桌面版

一个功能强大的桌面自动点击软件，可以点击任何软件窗口中的按钮。

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## ✨ 主要特性

### 🎯 核心功能
- **窗口选择** - 可视化选择任意软件窗口
- **坐标选择** - 精确选择点击位置，支持截图预览
- **自动点击** - 支持左键、右键、中键点击
- **批量操作** - 可以选择多个点击位置
- **定时控制** - 自定义点击间隔和次数

### 🛡️ 安全保护
- **鼠标保护** - 鼠标移动时自动停止
- **快捷键停止** - Ctrl+Shift+Space 紧急停止
- **单实例运行** - 防止多开冲突
- **错误恢复** - 异常情况自动处理

### 📊 统计监控
- **实时统计** - 点击次数、成功率统计
- **历史记录** - 详细的使用历史
- **性能监控** - CPU和内存使用情况
- **详细日志** - 完整的操作日志

### 🎨 现代界面
- **直观操作** - 简洁易用的图形界面
- **选项卡设计** - 功能分区清晰
- **实时反馈** - 操作状态实时显示
- **配置管理** - 支持保存和加载配置

## 🚀 快速开始

### 方法一：自动安装（推荐）

1. **下载源码**：
   ```bash
   git clone <repository-url>
   cd click
   ```

2. **运行安装程序**：
   ```bash
   python install.py
   ```

3. **启动程序**：
   - Windows: 双击 `快速点击助手.bat`
   - Linux/macOS: 运行 `./快速点击助手.sh`
   - 或者: `python main.py`

### 方法二：手动安装

1. **检查Python版本**（需要3.6+）：
   ```bash
   python --version
   ```

2. **安装依赖库**：
   ```bash
   pip install -r requirements.txt
   ```

3. **启动程序**：
   ```bash
   python main.py
   ```

### 方法三：可执行文件（无需Python环境）

1. **运行打包脚本**：
   ```bash
   python build.py
   ```

2. **使用生成的exe文件**（Windows）

## 📖 详细使用说明

### 基础操作流程

1. **🎯 选择目标窗口**
   - 点击"选择窗口"按钮
   - 从窗口列表中选择目标软件
   - 或者直接点击目标窗口

2. **📍 选择点击坐标**
   - 点击"选择坐标"按钮
   - 在窗口截图上点击要自动点击的位置
   - 确认坐标位置

3. **⚙️ 设置点击参数**
   - **点击间隔**: 两次点击间的时间（100-10000毫秒）
   - **点击次数**: 总点击次数（0=无限点击）
   - **鼠标键**: 左键/右键/中键

4. **▶️ 开始自动点击**
   - 点击"开始点击"按钮
   - 或使用快捷键 `Ctrl+Shift+Space`

### 高级功能

#### 批量点击设置
- 在"高级设置"选项卡中启用"多点点击"
- 可以设置多个点击位置
- 支持不同的点击序列

#### 安全设置
- **鼠标保护**: 鼠标移动时自动停止（推荐开启）
- **快捷键停止**: 全局快捷键紧急停止
- **失败重试**: 点击失败时自动重试

#### 配置管理
- **保存配置**: 保存当前设置为配置文件
- **加载配置**: 从配置文件恢复设置
- **导入/导出**: 与其他设备共享配置

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 7+ / macOS 10.12+ / Ubuntu 18.04+
- **Python版本**: Python 3.6 或更高
- **内存**: 128 MB RAM
- **硬盘**: 100 MB 可用空间

### 推荐配置
- **操作系统**: Windows 10+ / macOS 11+ / Ubuntu 20.04+
- **Python版本**: Python 3.8+
- **内存**: 256 MB RAM
- **硬盘**: 500 MB 可用空间

### 依赖库列表
```
pyautogui>=0.9.54      # 鼠标键盘自动化
pywin32>=306           # Windows API（仅Windows）
Pillow>=9.5.0          # 图像处理
psutil>=5.9.5          # 系统信息
numpy>=1.24.3          # 数值计算
```

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+Space` | 开始/停止自动点击 |
| `F1` | 显示帮助信息 |
| `Ctrl+S` | 保存当前配置 |
| `Ctrl+O` | 加载配置文件 |
| `Esc` | 停止所有操作 |

## 🎯 应用场景

### 办公自动化
- **表单填写**: 自动填写重复表单
- **数据录入**: 批量数据录入操作
- **报告生成**: 自动化报告生成流程

### 软件测试
- **UI测试**: 自动化用户界面测试
- **压力测试**: 重复点击压力测试
- **回归测试**: 自动化回归测试

### 游戏辅助
- **重复任务**: 自动完成重复性游戏任务
- **资源收集**: 自动收集游戏资源
- **技能训练**: 自动化技能训练

### 其他用途
- **网页操作**: 自动化网页表单提交
- **软件操作**: 自动化软件界面操作
- **系统维护**: 定时系统维护任务

## 📁 项目结构

```
click/
├── main.py                 # 主程序入口
├── gui.py                  # 图形用户界面
├── clicker.py              # 自动点击引擎
├── window_manager.py       # 窗口管理器
├── config.py               # 配置管理器
├── utils.py                # 工具函数
├── install.py              # 自动安装脚本
├── build.py                # 打包脚本
├── requirements.txt        # 依赖库列表
├── README_DESKTOP.md       # 说明文档
└── 快速点击助手.bat         # Windows启动脚本
```

## 🔧 开发说明

### 开发环境搭建

1. **克隆项目**:
   ```bash
   git clone <repository-url>
   cd click
   ```

2. **创建虚拟环境**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**:
   ```bash
   python main.py
   ```

### 代码结构说明

- **main.py**: 应用程序主入口，负责初始化和启动
- **gui.py**: 基于tkinter的图形用户界面
- **clicker.py**: 核心点击引擎，处理鼠标操作
- **window_manager.py**: 窗口选择和坐标获取
- **config.py**: 配置文件管理和设置保存
- **utils.py**: 通用工具函数和辅助功能

### 打包发布

1. **安装打包工具**:
   ```bash
   pip install pyinstaller
   ```

2. **运行打包脚本**:
   ```bash
   python build.py
   ```

3. **生成的文件**:
   - `dist/快速点击助手/` - 可执行文件目录
   - `快速点击助手.exe` - 主程序文件

## ⚠️ 注意事项

### 使用限制
1. **合法使用**: 请确保在合法范围内使用本软件
2. **目标软件**: 某些软件可能有反自动化保护
3. **系统兼容**: 主要针对Windows系统优化
4. **权限要求**: 可能需要管理员权限

### 安全建议
1. **备份数据**: 使用前请备份重要数据
2. **测试环境**: 建议先在测试环境中使用
3. **适量使用**: 避免过度频繁的点击操作
4. **监控运行**: 运行时请注意监控程序状态

### 故障排除

#### 常见问题

**Q: 程序启动失败？**
A: 
1. 检查Python版本是否为3.6+
2. 确认所有依赖库已安装
3. 运行 `python install.py` 重新安装

**Q: 无法选择窗口？**
A:
1. 确认目标窗口可见且未最小化
2. 尝试以管理员权限运行
3. 检查防病毒软件是否阻止

**Q: 点击不生效？**
A:
1. 确认选择的坐标位置正确
2. 检查目标窗口是否仍然活跃
3. 尝试不同的点击类型

**Q: 程序运行缓慢？**
A:
1. 调整点击间隔时间
2. 关闭不必要的后台程序
3. 检查系统资源使用情况

## 📄 更新日志

### v1.0.0 (2024-12-XX)
- ✅ 初始版本发布
- ✅ 基础点击功能实现
- ✅ 窗口选择和坐标获取
- ✅ 图形用户界面设计
- ✅ 配置管理系统
- ✅ 自动安装脚本
- ✅ 打包发布脚本

### 未来计划
- [ ] 图像识别点击
- [ ] 宏录制和回放
- [ ] 云端配置同步
- [ ] 移动设备支持
- [ ] 更多语言支持

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 技术支持

- **问题反馈**: 请通过Issue报告问题
- **功能建议**: 欢迎提出功能改进建议
- **技术讨论**: 欢迎参与技术讨论

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⭐ 致谢

感谢以下开源项目：
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - 自动化库
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI框架
- [Pillow](https://pillow.readthedocs.io/) - 图像处理
- [psutil](https://psutil.readthedocs.io/) - 系统信息

---

**如果这个项目对你有帮助，请给个 ⭐ Star！**

**Enjoy efficient desktop automation! 🚀**
