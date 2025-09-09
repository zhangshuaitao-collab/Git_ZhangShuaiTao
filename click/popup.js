// popup.js - 弹出窗口逻辑
class ClickHelper {
    constructor() {
        this.isClicking = false;
        this.selectedElements = [];
        this.clickCount = 0;
        this.intervalId = null;
        this.statusTimeout = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
    }
    
    initializeElements() {
        this.selectBtn = document.getElementById('selectBtn');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.intervalInput = document.getElementById('intervalInput');
        this.clickCountInput = document.getElementById('clickCount');
        this.clickTypeSelect = document.getElementById('clickType');
        this.statusDiv = document.getElementById('status');
        this.clickCounterDiv = document.getElementById('clickCounter');
        this.selectedElementDiv = document.getElementById('selectedElement');
        this.batchSelectBtn = document.getElementById('batchSelectBtn');
        this.saveConfigBtn = document.getElementById('saveConfigBtn');
        this.loadConfigBtn = document.getElementById('loadConfigBtn');
    }
    
    bindEvents() {
        this.selectBtn.addEventListener('click', () => this.selectElement());
        this.startBtn.addEventListener('click', () => this.startClicking());
        this.stopBtn.addEventListener('click', () => this.stopClicking());
        this.batchSelectBtn.addEventListener('click', () => this.batchSelectElements());
        this.saveConfigBtn.addEventListener('click', () => this.saveConfiguration());
        this.loadConfigBtn.addEventListener('click', () => this.loadConfiguration());
        
        // 实时保存设置
        this.intervalInput.addEventListener('change', () => this.saveSettings());
        this.clickCountInput.addEventListener('change', () => this.saveSettings());
        this.clickTypeSelect.addEventListener('change', () => this.saveSettings());
    }
    
    async selectElement() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // 检查页面是否支持内容脚本
            if (!this.isValidPage(tab.url)) {
                this.updateStatus('当前页面不支持元素选择，请切换到普通网页', 'warning');
                return;
            }
            
            this.updateStatus('正在准备选择模式...', 'info');
            
            // 确保内容脚本已准备就绪
            const isReady = await this.ensureContentScriptReady(tab.id);
            if (!isReady) {
                this.updateStatus('无法在当前页面启用选择功能，请刷新页面重试', 'error');
                return;
            }
            
            this.updateStatus('请在网页中点击要自动点击的按钮...', 'info');
            
            // 注入选择模式到内容脚本
            await chrome.tabs.sendMessage(tab.id, {
                action: 'startElementSelection',
                mode: 'single'
            });
            
            // 关闭弹出窗口，让用户选择元素
            window.close();
            
        } catch (error) {
            console.error('选择元素错误:', error);
            this.updateStatus('选择元素时出错，请刷新页面重试', 'error');
        }
    }
    
    async batchSelectElements() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // 检查页面是否支持内容脚本
            if (!this.isValidPage(tab.url)) {
                this.updateStatus('当前页面不支持元素选择，请切换到普通网页', 'warning');
                return;
            }
            
            this.updateStatus('正在准备批量选择模式...', 'info');
            
            // 确保内容脚本已准备就绪
            const isReady = await this.ensureContentScriptReady(tab.id);
            if (!isReady) {
                this.updateStatus('无法在当前页面启用选择功能，请刷新页面重试', 'error');
                return;
            }
            
            this.updateStatus('请在网页中点击多个要自动点击的按钮...', 'info');
            
            await chrome.tabs.sendMessage(tab.id, {
                action: 'startElementSelection',
                mode: 'batch'
            });
            
            window.close();
            
        } catch (error) {
            console.error('批量选择错误:', error);
            this.updateStatus('批量选择元素时出错，请刷新页面重试', 'error');
        }
    }
    
    async startClicking() {
        if (this.selectedElements.length === 0) {
            this.updateStatus('请先选择要点击的元素', 'warning');
            return;
        }
        
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // 检查页面是否支持内容脚本
            if (!this.isValidPage(tab.url)) {
                this.updateStatus('当前页面不支持自动点击功能', 'warning');
                return;
            }
            
            // 确保内容脚本已准备就绪
            const isReady = await this.ensureContentScriptReady(tab.id);
            if (!isReady) {
                this.updateStatus('无法在当前页面启用点击功能，请刷新页面重试', 'error');
                return;
            }
            
            this.isClicking = true;
            this.clickCount = 0;
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            
            const interval = parseInt(this.intervalInput.value);
            const maxClicks = parseInt(this.clickCountInput.value);
            const clickType = this.clickTypeSelect.value;
            
            this.updateStatus(`开始自动点击 (间隔: ${interval}ms)`, 'success');
            
            // 发送开始点击消息到内容脚本
            await chrome.tabs.sendMessage(tab.id, {
                action: 'startAutoClick',
                config: {
                    interval: interval,
                    maxClicks: maxClicks,
                    clickType: clickType,
                    elements: this.selectedElements
                }
            });
            
        } catch (error) {
            console.error('开始点击错误:', error);
            this.updateStatus('开始点击时出错，请刷新页面重试', 'error');
            this.stopClicking();
        }
    }
    
    async stopClicking() {
        this.isClicking = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        
        this.updateStatus('已停止自动点击', 'info');
        
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            await chrome.tabs.sendMessage(tab.id, {
                action: 'stopAutoClick'
            });
            
        } catch (error) {
            console.error('停止点击时出错:', error);
        }
    }
    
    updateStatus(message, type = 'info') {
        // 清除之前的定时器以防止冲突
        if (this.statusTimeout) {
            clearTimeout(this.statusTimeout);
        }
        
        this.statusDiv.textContent = message;
        this.statusDiv.className = `status ${type}`;
        
        // 3秒后恢复默认状态
        this.statusTimeout = setTimeout(() => {
            if (this.statusDiv.textContent === message) {
                this.statusDiv.textContent = '准备就绪';
                this.statusDiv.className = 'status';
            }
        }, 3000);
    }
    
    updateSelectedElements(elements) {
        this.selectedElements = elements;
        
        if (elements.length === 0) {
            this.selectedElementDiv.innerHTML = '未选择任何元素';
        } else if (elements.length === 1) {
            this.selectedElementDiv.innerHTML = `已选择: <code>${elements[0].selector}</code>`;
        } else {
            this.selectedElementDiv.innerHTML = `已选择 ${elements.length} 个元素`;
        }
    }
    
    updateClickCounter(count) {
        this.clickCount = count;
        this.clickCounterDiv.textContent = `已点击: ${count} 次`;
    }
    
    async saveSettings() {
        const settings = {
            interval: this.intervalInput.value,
            clickCount: this.clickCountInput.value,
            clickType: this.clickTypeSelect.value
        };
        
        await chrome.storage.sync.set({ clickHelperSettings: settings });
    }
    
    async loadSettings() {
        const result = await chrome.storage.sync.get('clickHelperSettings');
        const settings = result.clickHelperSettings || {};
        
        this.intervalInput.value = settings.interval || '1000';
        this.clickCountInput.value = settings.clickCount || '0';
        this.clickTypeSelect.value = settings.clickType || 'click';
    }
    
    async saveConfiguration() {
        const config = {
            settings: {
                interval: this.intervalInput.value,
                clickCount: this.clickCountInput.value,
                clickType: this.clickTypeSelect.value
            },
            elements: this.selectedElements
        };
        
        await chrome.storage.sync.set({ savedConfiguration: config });
        this.updateStatus('配置已保存', 'success');
    }
    
    async loadConfiguration() {
        const result = await chrome.storage.sync.get('savedConfiguration');
        const config = result.savedConfiguration;
        
        if (!config) {
            this.updateStatus('没有找到保存的配置', 'warning');
            return;
        }
        
        // 加载设置
        this.intervalInput.value = config.settings.interval;
        this.clickCountInput.value = config.settings.clickCount;
        this.clickTypeSelect.value = config.settings.clickType;
        
        // 加载元素
        this.selectedElements = config.elements || [];
        this.updateSelectedElements(this.selectedElements);
        
        this.updateStatus('配置已加载', 'success');
    }
    
    // 检查页面是否支持内容脚本
    isValidPage(url) {
        if (!url) return false;
        
        // 不支持的页面类型
        const unsupportedPages = [
            'chrome://',
            'chrome-extension://',
            'moz-extension://',
            'about:',
            'edge://',
            'opera://'
        ];
        
        return !unsupportedPages.some(prefix => url.startsWith(prefix));
    }
    
    // 确保内容脚本已准备就绪
    async ensureContentScriptReady(tabId) {
        try {
            // 尝试ping内容脚本
            const response = await chrome.tabs.sendMessage(tabId, { 
                action: 'ping'
            });
            return response && response.ready;
        } catch (error) {
            console.log('内容脚本未准备就绪:', error);
            
            // 尝试注入内容脚本
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content.js']
                });
                
                // 等待一下让脚本初始化
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // 再次尝试ping
                const retryResponse = await chrome.tabs.sendMessage(tabId, { 
                    action: 'ping'
                });
                return retryResponse && retryResponse.ready;
            } catch (injectError) {
                console.error('无法注入内容脚本:', injectError);
                return false;
            }
        }
    }
    
    async initialize() {
        // 监听来自内容脚本的消息
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.action === 'elementSelected') {
                this.updateSelectedElements(message.elements);
            } else if (message.action === 'clickCountUpdate') {
                this.updateClickCounter(message.count);
            } else if (message.action === 'autoClickStopped') {
                this.stopClicking();
                this.updateStatus(message.reason || '自动点击已停止', 'info');
            }
        });
        
        // 检查当前页面是否已有选择的元素
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (this.isValidPage(tab.url)) {
                const isReady = await this.ensureContentScriptReady(tab.id);
                if (isReady) {
                    const response = await chrome.tabs.sendMessage(tab.id, { action: 'getSelectedElements' });
                    if (response && response.elements) {
                        this.updateSelectedElements(response.elements);
                    }
                }
            }
        } catch (error) {
            console.log('无法获取当前选择的元素:', error);
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    const clickHelper = new ClickHelper();
    clickHelper.initialize();
});
