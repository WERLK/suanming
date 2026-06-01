/**
 * 玄机算命网 - 大数据联网实时分析 API 封装层
 * 提供统一的API调用、Loading/Error/Result三态管理、数据来源标识
 * 依赖：main.js 中的 showToast()
 */

// ===== API 地址配置 =====

/**
 * 自动检测 API 基础地址
 * - 本地开发：http://localhost:5000
 * - Render.com 部署：https://suanming-fix.onrender.com
 * - 其他生产环境：自动使用当前域名
 */
function getAPIBaseURL() {
    // 1. 如果是本地开发环境
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    
    // 2. 如果配置了自定义后端地址（通过 meta 标签）
    const metaURL = document.querySelector('meta[name="api-base-url"]');
    if (metaURL) {
        return metaURL.content;
    }
    
    // 3. 如果前端在 GitHub Pages，后端在 Render.com
    // 自动检测并使用 Render.com 地址
    if (location.hostname.endsWith('github.io')) {
        return 'https://suanming-fix.onrender.com';
    }
    
    // 4. 同域名部署（前后端在同一个域名下）
    return '';
}

const API_BASE = getAPIBaseURL();

console.log('[Fortune API] 使用API地址:', API_BASE || '(同域名)');
// ===== 统一 API 调用 =====

/**
 * POST 方式调用算命 API
 * @param {string} endpoint - API 端点路径 (如 'bazi', 'shengxiao', 'xingzuo/daily')
 * @param {object} params - 请求参数
 * @param {object} options - 可选配置 {showLoading: true, loadingMsg: '...'}
 * @returns {Promise<object|null>} API 响应数据
 */
async function fortuneAPI(endpoint, params = {}, options = {}) {
    const { showLoading = true, loadingMsg = '正在联网获取最新数据...' } = options;
    
    if (showLoading) {
        showFortuneLoading(loadingMsg);
    }
    
    try {
        const res = await fetch(API_BASE + '/api/fortune/' + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        if (res.status === 429) {
            hideFortuneLoading();
            showToast('请求过于频繁，请稍后再试');
            return null;
        }
        
        const data = await res.json();
        hideFortuneLoading();
        
        if (!data.success) {
            showToast(data.message || '分析失败，请重试');
            return null;
        }
        
        return data;
    } catch (err) {
        hideFortuneLoading();
        showToast('网络连接失败，请检查网络后重试');
        console.error('fortuneAPI error:', err);
        return null;
    }
}

/**
 * GET 方式调用算命 API
 * @param {string} endpoint - API 端点路径
 * @param {object} params - URL 查询参数
 * @returns {Promise<object|null>} API 响应数据
 */
async function fortuneGetAPI(endpoint, params = {}) {
    showFortuneLoading('正在获取实时数据...');
    
    try {
        const query = new URLSearchParams(params).toString();
        const url = API_BASE + '/api/fortune/' + endpoint + (query ? '?' + query : '');
        
        const res = await fetch(url);
        
        if (res.status === 429) {
            hideFortuneLoading();
            showToast('请求过于频繁，请稍后再试');
            return null;
        }
        
        const data = await res.json();
        hideFortuneLoading();
        
        if (!data.success) {
            showToast(data.message || '获取数据失败');
            return null;
        }
        
        return data;
    } catch (err) {
        hideFortuneLoading();
        showToast('网络连接失败，请检查网络');
        console.error('fortuneGetAPI error:', err);
        return null;
    }
}

// ===== Loading 状态管理 =====

/**
 * 显示全屏加载遮罩
 * @param {string} msg - 加载提示文字
 */
function showFortuneLoading(msg) {
    // 移除已有的 loading
    hideFortuneLoading();
    
    const overlay = document.createElement('div');
    overlay.className = 'fortune-loading-overlay';
    overlay.id = 'fortuneLoadingOverlay';
    overlay.innerHTML = `
        <div class="fortune-loading-content">
            <div class="fortune-spinner"></div>
            <p class="fortune-loading-text">${msg}</p>
            <p class="fortune-loading-sub">⚡ 大数据联网实时分析中</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

/**
 * 隐藏加载遮罩
 */
function hideFortuneLoading() {
    const overlay = document.getElementById('fortuneLoadingOverlay');
    if (overlay) {
        overlay.classList.add('fortune-loading-hide');
        setTimeout(() => overlay.remove(), 300);
    }
}

// ===== 数据来源标识 =====

/**
 * 在指定容器内显示数据来源标签
 * @param {string} source - 数据来源: 'realtime' | 'cached' | 'local' | 'local_fallback'
 * @param {string} containerId - 容器元素ID
 */
function showDataBadge(source, containerId, meta) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const badges = {
        'realtime': { text: '🟢 实时联网数据', cls: 'badge-realtime' },
        'cached': { text: '🟡 缓存数据', cls: 'badge-cached' },
        'local': { text: '🔵 服务器计算', cls: 'badge-local' },
        'local_fallback': { text: '🔴 离线数据（网络不可用）', cls: 'badge-fallback' }
    };

    const info = badges[source] || badges['local'];

    // 优先使用服务器返回的 generated_at 时间戳，保证刷新不跳变
    let timeStr;
    if (meta && meta.generated_at) {
        timeStr = new Date(meta.generated_at).toLocaleTimeString('zh-CN', { hour12: false });
    } else {
        timeStr = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    }

    // 移除已有的badge
    const existing = container.querySelector('.fortune-data-badge');
    if (existing) existing.remove();

    const badge = document.createElement('div');
    badge.className = 'fortune-data-badge ' + info.cls;
    badge.innerHTML = `${info.text} · 更新于 ${timeStr}`;
    container.insertBefore(badge, container.firstChild);
}

// ===== 错误和重试 =====

/**
 * 在容器内显示错误状态
 * @param {string} containerId - 容器ID
 * @param {string} message - 错误信息
 * @param {Function} onRetry - 重试回调
 * @param {Function} onFallback - 降级回调
 */
function showFortuneError(containerId, message, onRetry, onFallback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let retryHtml = '';
    let fallbackHtml = '';
    
    if (onRetry) {
        const retryId = 'retry_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        window._fortuneRetryCallbacks = window._fortuneRetryCallbacks || {};
        window._fortuneRetryCallbacks[retryId] = onRetry;
        retryHtml = `<button class="fortune-btn fortune-btn-retry" onclick="(window._fortuneRetryCallbacks['${retryId}'] || function(){})();">🔄 重新获取</button>`;
    }
    
    if (onFallback) {
        const fallbackId = 'fallback_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        window._fortuneRetryCallbacks = window._fortuneRetryCallbacks || {};
        window._fortuneRetryCallbacks[fallbackId] = onFallback;
        fallbackHtml = `<button class="fortune-btn fortune-btn-fallback" onclick="(window._fortuneRetryCallbacks['${fallbackId}'] || function(){})();">📡 使用本地计算</button>`;
    }
    
    container.innerHTML = `
        <div class="fortune-error-state">
            <div class="fortune-error-icon">⚠️</div>
            <p class="fortune-error-message">${message || '数据获取失败'}</p>
            <div class="fortune-error-actions">
                ${retryHtml}
                ${fallbackHtml}
            </div>
        </div>
    `;
}

// ===== 图片上传分析（升级版） =====

/**
 * 上传图片进行AI分析
 * @param {File} file - 图片文件
 * @param {string} moduleType - 模块类型 (bazi/ziwei/fengshui/mianxiang/shouxiang)
 * @returns {Promise<object|null>}
 */
async function uploadImageFortune(file, moduleType) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = async function(e) {
            const base64 = e.target.result;
            const result = await fortuneAPI('image-analyze', {
                image: base64,
                module_type: moduleType
            }, { 
                loadingMsg: '正在AI智能分析图片...',
                apiBase: API_BASE  // 传递 API 基础地址
            });
            resolve(result);
        };
        reader.onerror = function() {
            hideFortuneLoading();
            showToast('图片读取失败');
            resolve(null);
        };
        reader.readAsDataURL(file);
    });
}

/**
 * 触发图片选择并分析（升级版，替代旧的 triggerImageUpload）
 * @param {string} moduleType - 模块类型
 */
function triggerImageUploadV2(moduleType) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async function() {
        const file = this.files[0];
        if (!file) return;
        
        const result = await uploadImageFortune(file, moduleType);
        if (result && result.data) {
            showImageAnalysisResultV2(result.data, result.meta);
        }
    };
    input.click();
}

/**
 * 显示图片分析结果（升级版）
 */
function showImageAnalysisResultV2(analysisData, meta) {
    let html = '<div class="image-analysis-result">';
    html += '<h3>📷 AI智能分析结果</h3>';
    
    if (meta) {
        const sourceMap = {
            'realtime': '🟢 联网实时分析',
            'local': '🔵 本地智能分析'
        };
        const timeStr = meta.generated_at 
            ? new Date(meta.generated_at).toLocaleTimeString('zh-CN', { hour12: false })
            : new Date().toLocaleTimeString('zh-CN', { hour12: false });
        html += `<div class="fortune-data-badge badge-${meta.source || 'local'}">${sourceMap[meta.source] || '智能分析'} · ${timeStr}</div>`;
    }
    
    html += '<pre class="analysis-text">' + (typeof analysisData === 'string' ? analysisData : JSON.stringify(analysisData, null, 2)) + '</pre>';
    html += '<button class="close-btn" onclick="this.parentElement.remove();">关闭</button>';
    html += '</div>';
    
    const resultArea = document.getElementById('resultArea') || document.getElementById('analysisResult') || document.querySelector('.result-area');
    if (resultArea) {
        resultArea.innerHTML = html;
        resultArea.style.display = 'block';
    } else {
        const contentArea = document.querySelector('.content-area');
        if (contentArea) {
            const div = document.createElement('div');
            div.innerHTML = html;
            contentArea.appendChild(div.firstChild);
        }
    }
}

// ===== 导出 =====
window.fortuneAPI = fortuneAPI;
window.fortuneGetAPI = fortuneGetAPI;
window.showFortuneLoading = showFortuneLoading;
window.hideFortuneLoading = hideFortuneLoading;
window.showDataBadge = showDataBadge;

// ===== 服务器时间格式化（全局辅助） =====
function formatServerTime(meta) {
    if (meta && meta.generated_at) {
        return new Date(meta.generated_at).toLocaleTimeString('zh-CN', { hour12: false });
    }
    return new Date().toLocaleTimeString('zh-CN', { hour12: false });
}
window.formatServerTime = formatServerTime;
window.showFortuneError = showFortuneError;
window.uploadImageFortune = uploadImageFortune;
window.triggerImageUploadV2 = triggerImageUploadV2;
