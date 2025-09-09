// 游戏数据和状态
const gameData = {
    currentLevel: 1,
    totalLevels: 10,
    startTime: null,
    endTime: null,
    isGameActive: false,
    timerInterval: null,
    
    // 关卡数据 - 包含原句、分词、目标描述和正确答案
    levels: [
        {
            id: 1,
            original: "我昨天在图书馆看了一本书",
            words: ["我", "昨天", "在图书馆", "看了", "一本书"],
            target: "将时间状语'昨天'置于句首，强调时间",
            correctOrder: ["昨天", "我", "在图书馆", "看了", "一本书"]
        },
        {
            id: 2,
            original: "小明在公园里快乐地踢足球",
            words: ["小明", "在公园里", "快乐地", "踢足球"],
            target: "将地点状语'在公园里'置于句首，强调地点",
            correctOrder: ["在公园里", "小明", "快乐地", "踢足球"]
        },
        {
            id: 3,
            original: "老师因为下雨取消了户外活动",
            words: ["老师", "因为下雨", "取消了", "户外活动"],
            target: "将原因状语'因为下雨'置于句首，强调原因",
            correctOrder: ["因为下雨", "老师", "取消了", "户外活动"]
        },
        {
            id: 4,
            original: "学生们为了准备考试努力学习",
            words: ["学生们", "为了准备考试", "努力", "学习"],
            target: "将目的状语'为了准备考试'置于句首，强调目的",
            correctOrder: ["为了准备考试", "学生们", "努力", "学习"]
        },
        {
            id: 5,
            original: "妈妈如果有时间会陪我去逛街",
            words: ["妈妈", "如果有时间", "会", "陪我", "去逛街"],
            target: "将条件状语'如果有时间'置于句首，强调条件",
            correctOrder: ["如果有时间", "妈妈", "会", "陪我", "去逛街"]
        },
        {
            id: 6,
            original: "孩子们虽然很累但仍然坚持训练",
            words: ["孩子们", "虽然很累", "但", "仍然", "坚持训练"],
            target: "将让步状语'虽然很累'置于句首，强调转折",
            correctOrder: ["虽然很累", "孩子们", "但", "仍然", "坚持训练"]
        },
        {
            id: 7,
            original: "爷爷无论刮风下雨都坚持晨练",
            words: ["爷爷", "无论", "刮风下雨", "都", "坚持晨练"],
            target: "将让步状语'无论刮风下雨'置于句首，强调条件的普遍性",
            correctOrder: ["无论", "刮风下雨", "爷爷", "都", "坚持晨练"]
        },
        {
            id: 8,
            original: "她只要努力学习就能取得好成绩",
            words: ["她", "只要", "努力学习", "就", "能取得", "好成绩"],
            target: "将条件状语'只要努力学习'置于句首，强调充分条件",
            correctOrder: ["只要", "努力学习", "她", "就", "能取得", "好成绩"]
        },
        {
            id: 9,
            original: "同学们按照老师的要求完成了作业",
            words: ["同学们", "按照", "老师的要求", "完成了", "作业"],
            target: "将方式状语'按照老师的要求'置于句首，强调方式",
            correctOrder: ["按照", "老师的要求", "同学们", "完成了", "作业"]
        },
        {
            id: 10,
            original: "大家通过共同努力终于解决了难题",
            words: ["大家", "通过", "共同努力", "终于", "解决了", "难题"],
            target: "将方式状语'通过共同努力'置于句首，强调解决方式",
            correctOrder: ["通过", "共同努力", "大家", "终于", "解决了", "难题"]
        }
    ]
};

// DOM元素
const elements = {
    currentLevel: document.getElementById('current-level'),
    totalLevels: document.getElementById('total-levels'),
    timerDisplay: document.getElementById('timer-display'),
    originalText: document.getElementById('original-text'),
    targetDescription: document.getElementById('target-description'),
    dragContainer: document.getElementById('drag-container'),
    dropZone: document.getElementById('drop-zone'),
    checkAnswerBtn: document.getElementById('check-answer'),
    resetLevelBtn: document.getElementById('reset-level'),
    restartGameBtn: document.getElementById('restart-game'),
    leaderboardList: document.getElementById('leaderboard-list'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalMessage: document.getElementById('modal-message'),
    modalButtons: document.getElementById('modal-buttons'),
    closeModal: document.querySelector('.close')
};

// 游戏初始化
function initGame() {
    elements.totalLevels.textContent = gameData.totalLevels;
    audioManager.init();
    loadLeaderboard();
    loadLevel(gameData.currentLevel);
    setupEventListeners();
}

// 设置事件监听器
function setupEventListeners() {
    elements.checkAnswerBtn.addEventListener('click', checkAnswer);
    elements.resetLevelBtn.addEventListener('click', resetCurrentLevel);
    elements.restartGameBtn.addEventListener('click', restartGame);
    elements.closeModal.addEventListener('click', closeModal);
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) closeModal();
    });
}

// 加载关卡
function loadLevel(levelNumber) {
    const level = gameData.levels[levelNumber - 1];
    if (!level) return;
    
    // 添加关卡切换动画
    elements.originalText.parentElement.classList.add('level-title-enter');
    
    // 更新界面信息
    elements.currentLevel.textContent = levelNumber;
    elements.originalText.textContent = level.original;
    elements.targetDescription.textContent = level.target;
    
    // 清空容器
    elements.dragContainer.innerHTML = '';
    elements.dropZone.innerHTML = '<div class="placeholder">拖动文字到这里</div>';
    
    // 创建可拖拽的文字块（带动画）
    level.words.forEach((word, index) => {
        setTimeout(() => {
            const wordElement = createDraggableWord(word, index);
            wordElement.classList.add('word-fly-in');
            elements.dragContainer.appendChild(wordElement);
            
            setTimeout(() => {
                wordElement.classList.remove('word-fly-in');
            }, 500);
        }, index * 100);
    });
    
    // 重置按钮状态
    elements.checkAnswerBtn.disabled = true;
    
    // 移除动画类
    setTimeout(() => {
        elements.originalText.parentElement.classList.remove('level-title-enter');
    }, 500);
    
    // 如果是第一关且游戏未开始，开始计时
    if (levelNumber === 1 && !gameData.isGameActive) {
        startTimer();
    }
}

// 创建可拖拽的文字元素
function createDraggableWord(text, index) {
    const wordElement = document.createElement('div');
    wordElement.className = 'draggable-word';
    wordElement.textContent = text;
    wordElement.draggable = true;
    wordElement.dataset.word = text;
    wordElement.dataset.index = index;
    
    // 拖拽事件
    wordElement.addEventListener('dragstart', handleDragStart);
    wordElement.addEventListener('dragend', handleDragEnd);
    
    return wordElement;
}

// 拖拽开始
function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.word);
    e.dataTransfer.setData('text/index', e.target.dataset.index);
    e.target.classList.add('dragging');
    
    // 设置拖拽效果
    e.dataTransfer.effectAllowed = 'move';
}

// 拖拽结束
function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

// 设置放置区域事件
function setupDropZone() {
    const dropZone = elements.dropZone;
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        if (!dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drag-over');
        }
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const word = e.dataTransfer.getData('text/plain');
        const index = e.dataTransfer.getData('text/index');
        
        // 创建新的文字元素放在drop zone中（带动画）
        const newWordElement = createDraggableWord(word, index);
        newWordElement.classList.add('drop-enter');
        
        // 移除placeholder
        const placeholder = dropZone.querySelector('.placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        dropZone.appendChild(newWordElement);
        audioManager.play('drop');
        
        setTimeout(() => {
            newWordElement.classList.remove('drop-enter');
        }, 300);
        
        // 从原容器中移除元素
        const originalElement = elements.dragContainer.querySelector(`[data-index="${index}"]`);
        if (originalElement) {
            originalElement.remove();
        }
        
        // 检查是否可以检查答案
        updateCheckButtonState();
    });
}

// 设置原始拖拽容器的放置事件
function setupDragContainer() {
    const dragContainer = elements.dragContainer;
    
    dragContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    
    dragContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        
        const word = e.dataTransfer.getData('text/plain');
        const index = e.dataTransfer.getData('text/index');
        
        // 从drop zone移除元素
        const dropZoneElement = elements.dropZone.querySelector(`[data-index="${index}"]`);
        if (dropZoneElement) {
            dropZoneElement.remove();
        }
        
        // 添加到原始容器（带动画）
        const newWordElement = createDraggableWord(word, index);
        newWordElement.classList.add('drop-enter');
        dragContainer.appendChild(newWordElement);
        
        setTimeout(() => {
            newWordElement.classList.remove('drop-enter');
        }, 300);
        
        // 如果drop zone为空，显示placeholder
        if (elements.dropZone.children.length === 0) {
            elements.dropZone.innerHTML = '<div class="placeholder">拖动文字到这里</div>';
        }
        
        // 更新按钮状态
        updateCheckButtonState();
    });
}

// 更新检查按钮状态
function updateCheckButtonState() {
    const wordsInDropZone = elements.dropZone.querySelectorAll('.draggable-word');
    const totalWords = gameData.levels[gameData.currentLevel - 1].words.length;
    elements.checkAnswerBtn.disabled = wordsInDropZone.length !== totalWords;
}

// 检查答案
function checkAnswer() {
    const wordsInDropZone = Array.from(elements.dropZone.querySelectorAll('.draggable-word'));
    const userOrder = wordsInDropZone.map(el => el.textContent);
    const correctOrder = gameData.levels[gameData.currentLevel - 1].correctOrder;
    
    const isCorrect = JSON.stringify(userOrder) === JSON.stringify(correctOrder);
    
    if (isCorrect) {
        // 答案正确
        showSuccessAnimation();
        
        if (gameData.currentLevel < gameData.totalLevels) {
            // 进入下一关
            setTimeout(() => {
                gameData.currentLevel++;
                loadLevel(gameData.currentLevel);
            }, 1000);
        } else {
            // 游戏完成
            setTimeout(() => {
                completeGame();
            }, 1000);
        }
    } else {
        // 答案错误
        showErrorAnimation();
        showModal(
            '答案不正确',
            '请重新排列文字顺序，注意要达到倒装句的效果。',
            [
                { text: '继续尝试', action: closeModal, isPrimary: true }
            ]
        );
    }
}

// 音效管理
const audioManager = {
    sounds: {
        drop: null,
        success: null,
        error: null,
        complete: null,
        tick: null
    },
    
    init() {
        // 这里可以加载音频文件
        // this.sounds.drop = new Audio('sounds/drop.mp3');
        // this.sounds.success = new Audio('sounds/success.mp3');
        // this.sounds.error = new Audio('sounds/error.mp3');
        // this.sounds.complete = new Audio('sounds/complete.mp3');
        // this.sounds.tick = new Audio('sounds/tick.mp3');
    },
    
    play(soundName) {
        if (this.sounds[soundName]) {
            this.sounds[soundName].currentTime = 0;
            this.sounds[soundName].play().catch(() => {
                // 忽略音频播放错误
            });
        }
    }
};

// 显示成功动画
function showSuccessAnimation() {
    elements.dropZone.classList.add('success-animation');
    audioManager.play('success');
    
    // 添加关卡完成动画
    if (gameData.currentLevel < gameData.totalLevels) {
        elements.currentLevel.parentElement.classList.add('level-complete');
        setTimeout(() => {
            elements.currentLevel.parentElement.classList.remove('level-complete');
        }, 1000);
    }
    
    setTimeout(() => {
        elements.dropZone.classList.remove('success-animation');
    }, 800);
}

// 显示错误动画
function showErrorAnimation() {
    elements.dropZone.classList.add('error-animation');
    audioManager.play('error');
    
    setTimeout(() => {
        elements.dropZone.classList.remove('error-animation');
    }, 600);
}

// 创建彩带效果
function createConfetti() {
    const colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6'];
    
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            
            document.body.appendChild(confetti);
            
            setTimeout(() => {
                confetti.remove();
            }, 4000);
        }, i * 100);
    }
}

// 重置当前关卡
function resetCurrentLevel() {
    loadLevel(gameData.currentLevel);
}

// 重新开始游戏
function restartGame() {
    showModal(
        '重新开始',
        '确定要重新开始游戏吗？当前进度将丢失。',
        [
            { text: '取消', action: closeModal },
            { text: '确定', action: () => {
                gameData.currentLevel = 1;
                stopTimer();
                loadLevel(1);
                closeModal();
            }, isPrimary: true }
        ]
    );
}

// 完成游戏
function completeGame() {
    stopTimer();
    const finalTime = formatTime(gameData.endTime - gameData.startTime);
    
    // 播放完成音效和彩带动画
    audioManager.play('complete');
    createConfetti();
    
    // 保存成绩
    saveScore(finalTime);
    
    showModal(
        '🎉 恭喜通关！',
        `您成功完成了所有关卡！\n总用时：${finalTime}`,
        [
            { text: '查看排行榜', action: () => {
                closeModal();
                scrollToLeaderboard();
            }},
            { text: '再来一次', action: () => {
                gameData.currentLevel = 1;
                loadLevel(1);
                closeModal();
            }, isPrimary: true }
        ]
    );
}

// 计时器功能
function startTimer() {
    gameData.startTime = Date.now();
    gameData.isGameActive = true;
    
    gameData.timerInterval = setInterval(() => {
        const elapsed = Date.now() - gameData.startTime;
        elements.timerDisplay.textContent = formatTime(elapsed);
        
        // 如果时间超过5分钟，添加警告效果
        if (elapsed > 300000) { // 5分钟
            elements.timerDisplay.parentElement.classList.add('timer-warning');
        }
    }, 100);
}

function stopTimer() {
    gameData.endTime = Date.now();
    gameData.isGameActive = false;
    
    if (gameData.timerInterval) {
        clearInterval(gameData.timerInterval);
        gameData.timerInterval = null;
    }
}

function formatTime(milliseconds) {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const ms = Math.floor((milliseconds % 1000) / 10);
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
}

// 排行榜功能
function saveScore(time) {
    const scores = getScores();
    const newScore = {
        time: time,
        timestamp: Date.now(),
        date: new Date().toLocaleDateString('zh-CN')
    };
    
    scores.push(newScore);
    scores.sort((a, b) => parseTime(a.time) - parseTime(b.time));
    scores.splice(10); // 只保留前10名
    
    localStorage.setItem('wordGameScores', JSON.stringify(scores));
    loadLeaderboard();
}

function getScores() {
    const scores = localStorage.getItem('wordGameScores');
    return scores ? JSON.parse(scores) : [];
}

function parseTime(timeStr) {
    const [minutes, secondsAndMs] = timeStr.split(':');
    const [seconds, ms] = secondsAndMs.split('.');
    return parseInt(minutes) * 60000 + parseInt(seconds) * 1000 + parseInt(ms) * 10;
}

function loadLeaderboard() {
    const scores = getScores();
    
    if (scores.length === 0) {
        elements.leaderboardList.innerHTML = '<div class="leaderboard-item">暂无记录</div>';
        return;
    }
    
    elements.leaderboardList.innerHTML = scores.map((score, index) => `
        <div class="leaderboard-item ${index === 0 ? 'highlight' : ''}">
            <span class="rank">#${index + 1}</span>
            <span class="time">${score.time}</span>
            <span class="date">${score.date}</span>
        </div>
    `).join('');
}

function scrollToLeaderboard() {
    document.querySelector('.leaderboard').scrollIntoView({
        behavior: 'smooth'
    });
}

// 模态框功能
function showModal(title, message, buttons = []) {
    elements.modalTitle.textContent = title;
    elements.modalMessage.textContent = message;
    
    elements.modalButtons.innerHTML = buttons.map(button => 
        `<button class="btn ${button.isPrimary ? 'btn-primary' : 'btn-secondary'}" 
                onclick="(${button.action.toString()})()">${button.text}</button>`
    ).join('');
    
    elements.modal.style.display = 'block';
}

function closeModal() {
    elements.modal.style.display = 'none';
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initGame();
    setupDropZone();
    setupDragContainer();
});

// 阻止页面的默认拖拽行为
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
});
