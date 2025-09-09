#!/bin/bash
# 快速点击助手 - 启动脚本 (Linux/macOS)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 清屏
clear

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🖱️  快速点击助手 - 桌面版 v1.0.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ 错误: 未检测到Python环境${NC}"
    echo
    echo -e "${YELLOW}💡 解决方案:${NC}"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-tk"
    echo "   CentOS/RHEL:   sudo yum install python3 python3-pip tkinter"
    echo "   macOS:         brew install python-tk"
    echo "   或访问 https://python.org 下载安装"
    echo
    read -p "按Enter键退出..."
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ 无法确定Python命令${NC}"
    exit 1
fi

# 检查Python版本
echo -e "${GREEN}🐍 检测到Python环境:${NC}"
$PYTHON_CMD --version
echo

# 检查主程序文件
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ 错误: 找不到main.py主程序文件${NC}"
    echo -e "${YELLOW}💡 请确保在正确的程序目录中运行此脚本${NC}"
    echo
    read -p "按Enter键退出..."
    exit 1
fi

# 检查依赖库
echo -e "${BLUE}🔍 正在检查依赖库...${NC}"

# 创建临时Python脚本来检查依赖
cat << 'EOF' > /tmp/check_deps.py
import sys
import importlib

required_modules = ['tkinter', 'PIL', 'psutil']
missing_modules = []

for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f"缺少依赖: {', '.join(missing_modules)}")
    sys.exit(1)
else:
    print("所有依赖库已安装")
    sys.exit(0)
EOF

# 运行依赖检查
if ! $PYTHON_CMD /tmp/check_deps.py 2>/dev/null; then
    echo -e "${YELLOW}⚠️  检测到缺失的依赖库${NC}"
    echo
    
    if [ -f "install.py" ]; then
        echo -e "${BLUE}🔧 尝试运行自动安装程序...${NC}"
        if $PYTHON_CMD install.py; then
            echo -e "${GREEN}✅ 依赖安装成功${NC}"
        else
            echo -e "${RED}❌ 自动安装失败${NC}"
            echo -e "${YELLOW}💡 请手动安装依赖库:${NC}"
            echo "   $PYTHON_CMD -m pip install -r requirements.txt"
            echo "   或者: $PYTHON_CMD -m pip install pyautogui Pillow psutil"
            echo
            read -p "按Enter键退出..."
            exit 1
        fi
    else
        echo -e "${YELLOW}💡 请手动安装依赖库:${NC}"
        echo "   $PYTHON_CMD -m pip install pyautogui Pillow psutil"
        
        # 针对不同系统的额外说明
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "   Ubuntu/Debian还需要: sudo apt install python3-tk python3-dev"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "   macOS还需要: brew install python-tk"
        fi
        
        echo
        read -p "按Enter键退出..."
        exit 1
    fi
else
    echo -e "${GREEN}✅ 所有依赖库已安装${NC}"
fi

# 清理临时文件
rm -f /tmp/check_deps.py

echo
echo -e "${GREEN}🚀 正在启动快速点击助手...${NC}"
echo -e "${YELLOW}⚠️  提示: 可以按Ctrl+C来退出程序${NC}"
echo

# 设置错误处理
trap 'echo -e "\n${YELLOW}⚠️  程序被用户中断${NC}"; exit 130' INT

# 启动主程序
if $PYTHON_CMD main.py; then
    echo
    echo -e "${GREEN}✅ 程序正常退出${NC}"
    echo -e "${BLUE}💖 感谢使用快速点击助手！${NC}"
    echo
    sleep 2
else
    exit_code=$?
    echo
    echo -e "${RED}❌ 程序异常退出 (退出代码: $exit_code)${NC}"
    echo
    echo -e "${YELLOW}🔍 故障排除建议:${NC}"
    echo "   1. 检查上述错误消息并记录"
    echo "   2. 确认所有依赖库正确安装"
    echo "   3. 检查系统权限设置"
    echo "   4. 查看日志文件获取详细信息"
    echo "   5. 尝试在终端中直接运行: $PYTHON_CMD main.py"
    echo
    echo -e "${BLUE}📞 如需帮助，请提供上述错误信息${NC}"
    echo
    read -p "按Enter键退出..."
    exit $exit_code
fi

exit 0
