/**
 * 赛博算命 - 前端交互脚本
 * 处理表单验证、AJAX请求、结果动态渲染
 */

// API 配置
const API_CONFIG = {
    baseUrl: 'http://localhost:5000',
    endpoints: {
        query: '/api/query',
        fortune: '/api/fortune',
        shensha: '/api/shensha'
    }
};

// DOM 元素引用
let elements = {};

/**
 * 初始化函数
 */
document.addEventListener('DOMContentLoaded', function() {
    initElements();
    initEventListeners();
    initPage();
});

/**
 * 初始化 DOM 元素引用
 */
function initElements() {
    elements = {
        // 表单相关
        queryForm: document.getElementById('queryForm'),
        nameInput: document.getElementById('nameInput'),
        birthdayInput: document.getElementById('birthdayInput'),
        genderSelect: document.getElementById('genderSelect'),
        submitBtn: document.getElementById('submitBtn'),
        
        // 消息区域
        messageArea: document.getElementById('messageArea'),
        
        // 结果区域
        resultSection: document.getElementById('resultSection'),
        
        // 各模块容器
        patternSection: document.getElementById('patternSection'),
        fiveElementsSection: document.getElementById('fiveElementsSection'),
        luckySection: document.getElementById('luckySection'),
        matchSection: document.getElementById('matchSection'),
        fortuneSection: document.getElementById('fortuneSection'),
        shishenSection: document.getElementById('shishenSection'),
        shenshaSection: document.getElementById('shenshaSection')
    };
}

/**
 * 初始化事件监听器
 */
function initEventListeners() {
    // 表单提交
    if (elements.queryForm) {
        elements.queryForm.addEventListener('submit', handleFormSubmit);
    }
    
    // 输入框实时验证
    if (elements.nameInput) {
        elements.nameInput.addEventListener('input', validateName);
    }
    
    if (elements.birthdayInput) {
        elements.birthdayInput.addEventListener('change', validateBirthday);
    }
}

/**
 * 初始化页面
 */
function initPage() {
    // 如果有缓存的查询结果，直接显示
    const cachedResult = sessionStorage.getItem('fortuneResult');
    if (cachedResult) {
        try {
            const result = JSON.parse(cachedResult);
            renderResult(result);
        } catch (e) {
            console.error('解析缓存结果失败:', e);
        }
    }
}

/**
 * 处理表单提交
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // 获取表单数据
    const formData = {
        name: elements.nameInput?.value?.trim() || '',
        birthday: elements.birthdayInput?.value || '',
        gender: elements.genderSelect?.value || 'male'
    };
    
    // 验证表单
    if (!validateForm(formData)) {
        return;
    }
    
    // 显示加载状态
    setLoadingState(true);
    clearMessage();
    
    try {
        // 发送请求
        const response = await queryFortune(formData);
        
        if (response.success) {
            // 缓存结果
            sessionStorage.setItem('fortuneResult', JSON.stringify(response.data));
            
            // 渲染结果
            renderResult(response.data);
            
            showMessage('查询成功！', 'success');
        } else {
            showMessage(response.message || '查询失败，请稍后重试', 'error');
        }
    } catch (error) {
        console.error('查询出错:', error);
        showMessage('网络错误，请检查服务器连接', 'error');
    } finally {
        setLoadingState(false);
    }
}

/**
 * 验证表单
 */
function validateForm(formData) {
    if (!formData.name) {
        showMessage('请输入姓名', 'error');
        elements.nameInput?.focus();
        return false;
    }
    
    if (!formData.birthday) {
        showMessage('请选择出生日期', 'error');
        elements.birthdayInput?.focus();
        return false;
    }
    
    // 验证日期格式
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(formData.birthday)) {
        showMessage('日期格式不正确，请选择有效日期', 'error');
        return false;
    }
    
    return true;
}

/**
 * 验证姓名
 */
function validateName(event) {
    const value = event.target.value;
    // 限制输入长度
    if (value.length > 20) {
        event.target.value = value.substring(0, 20);
    }
}

/**
 * 验证生日
 */
function validateBirthday(event) {
    const value = event.target.value;
    const selectedDate = new Date(value);
    const today = new Date();
    
    if (selectedDate > today) {
        showMessage('出生日期不能晚于今天', 'error');
        event.target.value = '';
    }
}

/**
 * 发送查询请求
 */
async function queryFortune(formData) {
    const url = `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.query}`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('请求失败:', error);
        throw error;
    }
}

/**
 * 渲染查询结果
 */
function renderResult(data) {
    if (!data || !elements.resultSection) return;
    
    // 显示结果区域
    elements.resultSection.classList.add('show');
    
    // 更新全局配置
    if (data.config) {
        Object.assign(CONFIG, data.config);
    }
    
    // 重新初始化页面
    if (typeof initPage === 'function') {
        initPage();
    }
    
    // 重新初始化图表
    if (typeof initCharts === 'function') {
        initCharts();
    }
    
    // 滚动到结果区域
    elements.resultSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 设置加载状态
 */
function setLoadingState(loading) {
    if (elements.submitBtn) {
        elements.submitBtn.disabled = loading;
        if (loading) {
            elements.submitBtn.innerHTML = '<span class="loading"></span> 计算中...';
        } else {
            elements.submitBtn.innerHTML = '<i class="fa fa-search"></i> 开始算命';
        }
    }
}

/**
 * 显示消息
 */
function showMessage(message, type = 'info') {
    if (!elements.messageArea) return;
    
    const className = type === 'error' ? 'error-message' : 
                      type === 'success' ? 'success-message' : 'info-message';
    
    elements.messageArea.innerHTML = `<div class="${className}">${message}</div>`;
    elements.messageArea.style.display = 'block';
    
    // 自动隐藏
    if (type === 'success') {
        setTimeout(() => {
            clearMessage();
        }, 3000);
    }
}

/**
 * 清除消息
 */
function clearMessage() {
    if (elements.messageArea) {
        elements.messageArea.innerHTML = '';
        elements.messageArea.style.display = 'none';
    }
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}年${month}月${day}日`;
}

/**
 * 计算年龄
 */
function calculateAge(birthday) {
    const today = new Date();
    const birthDate = new Date(birthday);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    return age;
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 本地存储工具
 */
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('存储失败:', e);
            return false;
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (e) {
            console.error('读取失败:', e);
            return defaultValue;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('删除失败:', e);
            return false;
        }
    }
};

/**
 * 导出模块（如果需要模块化使用）
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        queryFortune,
        renderResult,
        showMessage,
        formatDate,
        calculateAge,
        Storage
    };
}