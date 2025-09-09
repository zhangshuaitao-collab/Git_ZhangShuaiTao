// content.js - 内容脚本，注入到网页中执行点击功能
class AutoClickManager {
    constructor() {
        this.selectedElements = [];
        this.isSelecting = false;
        this.isClicking = false;
        this.clickInterval = null;
        this.clickCount = 0;
        this.maxClicks = 0;
        this.selectionMode = 'single'; // 'single' 或 'batch'
        this.overlay = null;
        this.highlightedElement = null;
        
        // 绑定事件处理器以保持this上下文
        this.boundHandleMouseOver = this.handleMouseOver.bind(this);
        this.boundHandleMouseOut = this.handleMouseOut.bind(this);
        this.boundHandleElementClick = this.handleElementClick.bind(this);
        
        this.initializeEventListeners();
        this.createSelectionOverlay();
    }
    
    initializeEventListeners() {
        // 监听来自弹出窗口的消息
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            switch (message.action) {
                case 'ping':
                    sendResponse({ ready: true });
                    break;
                case 'startElementSelection':
                    this.startElementSelection(message.mode);
                    sendResponse({ success: true });
                    break;
                case 'startAutoClick':
                    this.startAutoClick(message.config);
                    sendResponse({ success: true });
                    break;
                case 'stopAutoClick':
                    this.stopAutoClick();
                    sendResponse({ success: true });
                    break;
                case 'getSelectedElements':
                    sendResponse({ elements: this.selectedElements });
                    break;
                default:
                    sendResponse({ error: 'Unknown action' });
            }
            return true; // 保持消息通道开启
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.code === 'Space') {
                e.preventDefault();
                this.toggleAutoClick();
            } else if (e.key === 'Escape' && this.isSelecting) {
                this.stopElementSelection();
            }
        });
    }
    
    createSelectionOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 123, 255, 0.1);
            z-index: 999999;
            pointer-events: none;
            display: none;
            backdrop-filter: blur(2px);
        `;
        
        // 创建选择提示
        const tooltip = document.createElement('div');
        tooltip.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
            z-index: 1000000;
            display: none;
            pointer-events: none;
            user-select: none;
        `;
        tooltip.innerHTML = `
            <div>🎯 选择要点击的元素</div>
            <div style="font-size: 12px; margin-top: 5px; opacity: 0.9;">
                悬停高亮 → 点击选择 | ESC 取消
            </div>
            <div style="font-size: 11px; margin-top: 3px; opacity: 0.7;">
                现在可以点击页面上的按钮了
            </div>
        `;
        
        this.overlay.appendChild(tooltip);
        this.tooltip = tooltip;
        
        document.body.appendChild(this.overlay);
    }
    
    startElementSelection(mode = 'single') {
        console.log('🚀 开始元素选择模式:', mode);
        
        this.selectionMode = mode;
        this.isSelecting = true;
        this.overlay.style.display = 'block';
        this.tooltip.style.display = 'block';
        
        if (mode === 'batch') {
            this.tooltip.innerHTML = `
                <div>🎯 批量选择元素 (已选择: ${this.selectedElements.length})</div>
                <div style="font-size: 12px; margin-top: 5px; opacity: 0.9;">
                    点击元素添加到列表 | ESC 完成选择
                </div>
            `;
        }
        
        // 检查绑定函数是否存在
        console.log('🔧 检查事件处理器绑定:', {
            boundHandleMouseOver: !!this.boundHandleMouseOver,
            boundHandleMouseOut: !!this.boundHandleMouseOut,
            boundHandleElementClick: !!this.boundHandleElementClick
        });
        
        // 添加鼠标事件监听器
        document.addEventListener('mouseover', this.boundHandleMouseOver, true);
        document.addEventListener('mouseout', this.boundHandleMouseOut, true);
        document.addEventListener('click', this.boundHandleElementClick, true);
        
        console.log('✅ 事件监听器已添加');
        
        // 禁用页面滚动
        document.body.style.overflow = 'hidden';
        
        // 添加测试鼠标移动检测
        this.testMouseEvents();
    }
    
    // 测试鼠标事件是否正常工作
    testMouseEvents() {
        console.log('🧪 开始测试鼠标事件...');
        
        // 添加一个临时的全局鼠标移动监听器来测试
        const testHandler = (e) => {
            console.log('🐭 检测到鼠标移动:', e.target.tagName, e.target.className || '无类名');
        };
        
        document.addEventListener('mousemove', testHandler);
        
        // 5秒后移除测试监听器
        setTimeout(() => {
            document.removeEventListener('mousemove', testHandler);
            console.log('🧪 鼠标事件测试结束');
        }, 5000);
    }
    
    stopElementSelection() {
        this.isSelecting = false;
        this.overlay.style.display = 'none';
        this.tooltip.style.display = 'none';
        
        // 移除事件监听器
        document.removeEventListener('mouseover', this.boundHandleMouseOver, true);
        document.removeEventListener('mouseout', this.boundHandleMouseOut, true);
        document.removeEventListener('click', this.boundHandleElementClick, true);
        
        console.log('🧹 事件监听器已移除');
        
        // 恢复页面滚动
        document.body.style.overflow = '';
        
        // 移除高亮
        if (this.highlightedElement) {
            this.removeHighlight(this.highlightedElement);
            this.highlightedElement = null;
        }
        
        // 通知弹出窗口选择完成
        chrome.runtime.sendMessage({
            action: 'elementSelected',
            elements: this.selectedElements
        });
    }
    
    handleMouseOver(e) {
        console.log('🐭 handleMouseOver 被触发:', e.target.tagName, e.target.className || '无类名');
        
        if (!this.isSelecting) {
            console.log('⚠️ 不在选择模式，跳过');
            return;
        }
        
        const element = e.target;
        
        // 检查是否是遮罩层或提示框
        if (element === this.overlay || element === this.tooltip || element.parentElement === this.tooltip) {
            console.log('📍 鼠标在遮罩层或提示框上，跳过');
            return;
        }
        
        // 跳过不可点击的元素
        if (this.isIgnoredElement(element)) {
            console.log('❌ 元素被忽略:', element.tagName);
            return;
        }
        
        console.log('✅ 开始高亮元素:', element.tagName, element.className || '无类名');
        
        // 移除之前的高亮
        if (this.highlightedElement && this.highlightedElement !== element) {
            console.log('🧹 移除之前的高亮');
            this.removeHighlight(this.highlightedElement);
        }
        
        // 添加新的高亮
        console.log('🎯 添加高亮效果');
        this.addHighlight(element);
        this.highlightedElement = element;
        
        console.log('💡 鼠标悬停处理完成:', element.tagName);
    }
    
    handleMouseOut(e) {
        if (!this.isSelecting) return;
        // 不移除高亮，保持元素高亮直到鼠标移到其他元素
    }
    
    handleElementClick(e) {
        if (!this.isSelecting) return;
        
        console.log('点击事件触发:', e.target.tagName, e.target.className || '无className');
        
        e.preventDefault();
        e.stopPropagation();
        
        const element = e.target;
        if (element === this.overlay || element === this.tooltip || element.parentElement === this.tooltip) return;
        
        // 跳过不可点击的元素
        if (this.isIgnoredElement(element)) {
            console.log('跳过被忽略的元素:', element.tagName);
            return;
        }
        
        console.log('正在选择元素:', element.tagName, element.className || '无className');
        
        const selector = this.generateSelector(element);
        const elementInfo = {
            selector: selector,
            tagName: element.tagName.toLowerCase(),
            className: element.className,
            id: element.id,
            textContent: element.textContent?.trim().substring(0, 50) || '',
            rect: element.getBoundingClientRect()
        };
        
        console.log('生成的选择器:', selector);
        
        if (this.selectionMode === 'single') {
            // 单选模式：替换之前的选择
            this.selectedElements = [elementInfo];
            this.addPermanentHighlight(element, '#28a745');
            this.stopElementSelection();
            console.log('单选模式完成，选择了:', selector);
        } else {
            // 批量模式：添加到列表
            const existingIndex = this.selectedElements.findIndex(el => el.selector === selector);
            if (existingIndex >= 0) {
                // 已存在，移除
                this.selectedElements.splice(existingIndex, 1);
                this.removePermanentHighlight(element);
                console.log('从批量选择中移除:', selector);
            } else {
                // 新元素，添加
                this.selectedElements.push(elementInfo);
                this.addPermanentHighlight(element, '#007bff');
                console.log('添加到批量选择:', selector);
            }
            
            // 更新提示
            this.tooltip.innerHTML = `
                <div>🎯 批量选择元素 (已选择: ${this.selectedElements.length})</div>
                <div style="font-size: 12px; margin-top: 5px; opacity: 0.9;">
                    点击元素添加/移除 | ESC 完成选择
                </div>
            `;
        }
    }
    
    // 检查是否应该忽略某些元素
    isIgnoredElement(element) {
        const ignoredTags = ['SCRIPT', 'STYLE', 'HEAD', 'META', 'TITLE', 'LINK', 'NOSCRIPT'];
        
        // 检查标签名
        if (ignoredTags.includes(element.tagName.toUpperCase())) {
            console.log('🚫 忽略系统标签:', element.tagName);
            return true;
        }
        
        // 检查是否是我们扩展创建的元素
        if (element.hasAttribute('data-click-helper-selected') || 
            element.classList.toString().includes('click-helper')) {
            console.log('🚫 忽略扩展创建的元素');
            return true;
        }
        
        try {
            // 检查是否是不可见元素（简化检查）
            const style = window.getComputedStyle(element);
            if (style.display === 'none' || style.visibility === 'hidden') {
                console.log('🚫 忽略不可见元素:', element.tagName, 'display:', style.display, 'visibility:', style.visibility);
                return true;
            }
        } catch (error) {
            console.warn('⚠️ 获取元素样式失败，但继续处理:', error);
        }
        
        console.log('✅ 元素可以被选择:', element.tagName, element.className || '无类名');
        return false;
    }
    
    generateSelector(element) {
        // 尝试生成唯一的CSS选择器
        if (element.id) {
            return `#${element.id}`;
        }
        
        const path = [];
        let current = element;
        
        while (current && current.nodeType === Node.ELEMENT_NODE) {
            let selector = current.nodeName.toLowerCase();
            
            if (current.className) {
                selector += '.' + current.className.trim().split(/\s+/).join('.');
            }
            
            // 如果有兄弟元素，添加nth-child
            const siblings = Array.from(current.parentNode?.children || []);
            const sameTagSiblings = siblings.filter(s => s.nodeName === current.nodeName);
            if (sameTagSiblings.length > 1) {
                const index = sameTagSiblings.indexOf(current) + 1;
                selector += `:nth-child(${index})`;
            }
            
            path.unshift(selector);
            
            // 如果选择器已经足够独特，停止
            if (document.querySelectorAll(path.join(' > ')).length === 1) {
                break;
            }
            
            current = current.parentElement;
            
            // 防止选择器过长
            if (path.length > 5) break;
        }
        
        return path.join(' > ');
    }
    
    addHighlight(element) {
        console.log('🎨 添加高亮效果到:', element.tagName, element.className || '无类名');
        
        try {
            // 保存原始样式以便恢复
            if (!element.dataset.originalOutline) {
                element.dataset.originalOutline = element.style.outline || '';
                element.dataset.originalOutlineOffset = element.style.outlineOffset || '';
                element.dataset.originalBackgroundColor = element.style.backgroundColor || '';
                element.dataset.originalCursor = element.style.cursor || '';
            }
            
            element.style.outline = '3px solid #007bff !important';
            element.style.outlineOffset = '2px';
            element.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
            element.style.cursor = 'pointer';
            element.style.zIndex = '999998';
            
            console.log('✅ 高亮效果已应用');
        } catch (error) {
            console.error('❌ 添加高亮效果失败:', error);
        }
    }
    
    removeHighlight(element) {
        console.log('🧹 移除高亮效果:', element.tagName, element.className || '无类名');
        
        try {
            // 恢复原始样式
            element.style.outline = element.dataset.originalOutline || '';
            element.style.outlineOffset = element.dataset.originalOutlineOffset || '';
            element.style.backgroundColor = element.dataset.originalBackgroundColor || '';
            element.style.cursor = element.dataset.originalCursor || '';
            element.style.zIndex = '';
            
            // 清除保存的原始样式
            delete element.dataset.originalOutline;
            delete element.dataset.originalOutlineOffset;
            delete element.dataset.originalBackgroundColor;
            delete element.dataset.originalCursor;
            
            console.log('✅ 高亮效果已移除');
        } catch (error) {
            console.error('❌ 移除高亮效果失败:', error);
        }
    }
    
    addPermanentHighlight(element, color) {
        element.style.outline = `2px solid ${color}`;
        element.style.outlineOffset = '1px';
        element.setAttribute('data-click-helper-selected', 'true');
    }
    
    removePermanentHighlight(element) {
        element.style.outline = '';
        element.style.outlineOffset = '';
        element.removeAttribute('data-click-helper-selected');
    }
    
    async startAutoClick(config) {
        if (this.selectedElements.length === 0) {
            chrome.runtime.sendMessage({
                action: 'autoClickStopped',
                reason: '没有选择任何元素'
            });
            return;
        }
        
        this.isClicking = true;
        this.clickCount = 0;
        this.maxClicks = config.maxClicks;
        
        const clickElements = () => {
            if (!this.isClicking) return;
            
            // 检查是否达到最大点击次数
            if (this.maxClicks > 0 && this.clickCount >= this.maxClicks) {
                this.stopAutoClick();
                chrome.runtime.sendMessage({
                    action: 'autoClickStopped',
                    reason: `已达到最大点击次数: ${this.maxClicks}`
                });
                return;
            }
            
            // 点击所有选择的元素
            let clickedCount = 0;
            for (const elementInfo of this.selectedElements) {
                const element = document.querySelector(elementInfo.selector);
                if (element) {
                    this.simulateClick(element, config.clickType);
                    clickedCount++;
                    
                    // 添加点击视觉反馈
                    this.showClickEffect(element);
                }
            }
            
            if (clickedCount === 0) {
                this.stopAutoClick();
                chrome.runtime.sendMessage({
                    action: 'autoClickStopped',
                    reason: '找不到选择的元素'
                });
                return;
            }
            
            this.clickCount++;
            
            // 通知弹出窗口更新点击计数
            chrome.runtime.sendMessage({
                action: 'clickCountUpdate',
                count: this.clickCount
            });
        };
        
        // 立即执行第一次点击
        clickElements();
        
        // 设置定时器
        this.clickInterval = setInterval(clickElements, config.interval);
    }
    
    stopAutoClick() {
        this.isClicking = false;
        if (this.clickInterval) {
            clearInterval(this.clickInterval);
            this.clickInterval = null;
        }
    }
    
    simulateClick(element, clickType = 'click') {
        const rect = element.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        
        const eventOptions = {
            bubbles: true,
            cancelable: true,
            clientX: x,
            clientY: y,
            button: 0
        };
        
        switch (clickType) {
            case 'click':
                element.dispatchEvent(new MouseEvent('mousedown', eventOptions));
                element.dispatchEvent(new MouseEvent('mouseup', eventOptions));
                element.dispatchEvent(new MouseEvent('click', eventOptions));
                break;
            case 'doubleclick':
                element.dispatchEvent(new MouseEvent('click', eventOptions));
                element.dispatchEvent(new MouseEvent('dblclick', eventOptions));
                break;
            case 'mousedown':
                element.dispatchEvent(new MouseEvent('mousedown', eventOptions));
                break;
            case 'mouseup':
                element.dispatchEvent(new MouseEvent('mouseup', eventOptions));
                break;
        }
        
        // 如果是按钮或链接，也尝试触发原生点击
        if (element.tagName === 'BUTTON' || element.tagName === 'A') {
            element.click();
        }
    }
    
    showClickEffect(element) {
        const effect = document.createElement('div');
        const rect = element.getBoundingClientRect();
        
        effect.style.cssText = `
            position: fixed;
            left: ${rect.left + rect.width / 2 - 15}px;
            top: ${rect.top + rect.height / 2 - 15}px;
            width: 30px;
            height: 30px;
            background: radial-gradient(circle, rgba(40, 167, 69, 0.8) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 999999;
            animation: clickEffect 0.6s ease-out;
        `;
        
        // 添加CSS动画
        if (!document.querySelector('#click-helper-styles')) {
            const styles = document.createElement('style');
            styles.id = 'click-helper-styles';
            styles.textContent = `
                @keyframes clickEffect {
                    0% {
                        transform: scale(0);
                        opacity: 1;
                    }
                    100% {
                        transform: scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(effect);
        
        setTimeout(() => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        }, 600);
    }
    
    toggleAutoClick() {
        if (this.isClicking) {
            this.stopAutoClick();
            chrome.runtime.sendMessage({
                action: 'autoClickStopped',
                reason: '通过快捷键停止'
            });
        } else if (this.selectedElements.length > 0) {
            this.startAutoClick({
                interval: 1000,
                maxClicks: 0,
                clickType: 'click'
            });
        }
    }
}

// 初始化自动点击管理器
let autoClickManager;

// 等待页面加载完成
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        autoClickManager = new AutoClickManager();
    });
} else {
    autoClickManager = new AutoClickManager();
}

// 防止重复初始化
window.clickHelperInitialized = true;
