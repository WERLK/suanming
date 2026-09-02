/**
 * 设备检测与桌面端适配
 * 自动检测设备类型，桌面端注入侧边栏
 */
(function() {
    'use strict';
    var ua = navigator.userAgent.toLowerCase();
    var width = window.innerWidth || document.documentElement.clientWidth;
    var isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    var device = 'mobile';

    if (/windows|macintosh|linux x86_64|linux i686/.test(ua) && !/mobile|android|iphone|ipad/.test(ua)) {
        device = width >= 1024 ? 'desktop' : 'tablet';
    } else if (/ipad/.test(ua) || (/android/.test(ua) && !/mobile/.test(ua))) {
        device = 'tablet';
    }
    if (width >= 1280 && !isTouch) device = 'desktop';

    document.documentElement.setAttribute('data-device', device);
    document.body.classList.add('is-' + device);
    document.cookie = 'device=' + device + ';path=/;max-age=86400';

    // 桌面端：注入侧边栏（如果页面没有的话）
    if (device === 'desktop' && !document.querySelector('.desktop-sidebar')) {
        var sidebarHTML =
            '<aside class="desktop-sidebar" id="desktopSidebar">' +
            '  <div class="sidebar-logo">' +
            '    <div class="logo-icon">🔮</div>' +
            '    <div><span class="logo-text">玄机算命网</span><span class="logo-sub">传承千年智慧</span></div>' +
            '  </div>' +
            '  <nav class="sidebar-nav">' +
            '    <div class="sidebar-nav-section">' +
            '      <div class="sidebar-nav-title">主导航</div>' +
            '      <a href="/" class="sidebar-nav-item ' + (location.pathname === '/' || location.pathname === '/index.html' ? 'active' : '') + '"><span class="nav-icon">🏠</span> 首页</a>' +
            '      <a href="/more.html" class="sidebar-nav-item ' + (location.pathname === '/more.html' ? 'active' : '') + '"><span class="nav-icon">🔮</span> 更多模块</a>' +
            '      <a href="/vip.html" class="sidebar-nav-item ' + (location.pathname === '/vip.html' ? 'active' : '') + '"><span class="nav-icon">👑</span> 会员中心</a>' +
            '      <a href="/profile.html" class="sidebar-nav-item ' + (location.pathname === '/profile.html' ? 'active' : '') + '"><span class="nav-icon">👤</span> 个人中心</a>' +
            '      <a href="/download.html" class="sidebar-nav-item ' + (location.pathname === '/download.html' ? 'active' : '') + '"><span class="nav-icon">📥</span> 下载客户端</a>' +
            '    </div>' +
            '    <div class="sidebar-nav-section">' +
            '      <div class="sidebar-nav-title">热门功能</div>' +
            '      <a href="/modules/bazi.html" class="sidebar-nav-item"><span class="nav-icon">🎴</span> 八字排盘</a>' +
            '      <a href="/modules/ziwei.html" class="sidebar-nav-item"><span class="nav-icon">⭐</span> 紫微斗数</a>' +
            '      <a href="/modules/heyun.html" class="sidebar-nav-item"><span class="nav-icon">💑</span> 合婚配对</a>' +
            '      <a href="/modules/shengxiao.html" class="sidebar-nav-item"><span class="nav-icon">🐉</span> 生肖运势</a>' +
            '      <a href="/modules/tarot.html" class="sidebar-nav-item"><span class="nav-icon">🃏</span> 塔罗牌</a>' +
            '      <a href="/modules/zhougong.html" class="sidebar-nav-item"><span class="nav-icon">😴</span> 周公解梦</a>' +
            '      <a href="/modules/fengshui.html" class="sidebar-nav-item"><span class="nav-icon">🏠</span> 风水堪舆</a>' +
            '      <a href="/modules/huangdao.html" class="sidebar-nav-item"><span class="nav-icon">📅</span> 黄道吉日</a>' +
            '    </div>' +
            '  </nav>' +
            '  <div class="sidebar-footer">' +
            '    <a href="/profile.html" class="sidebar-user" id="sidebarUser">' +
            '      <div class="user-avatar">👤</div>' +
            '      <div class="user-info">' +
            '        <div class="user-name" id="sidebarUserName">未登录</div>' +
            '        <div class="user-status">点击登录</div>' +
            '      </div>' +
            '    </a>' +
            '  </div>' +
            '</aside>';
        var wrapper = document.createElement('div');
        wrapper.innerHTML = sidebarHTML;
        document.body.insertBefore(wrapper.firstChild, document.body.firstChild);
        document.body.classList.add('has-desktop-sidebar');

        // 隐藏移动端导航
        var tn = document.querySelector('.top-nav');
        if (tn) tn.style.display = 'none';
        var bn = document.querySelector('.bottom-nav');
        if (bn) bn.style.display = 'none';
        var ph = document.querySelector('.page-header');
        if (ph) ph.style.display = 'none';

        // 同步登录状态
        try {
            var user = JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{}');
            if (user && user.username) {
                var nameEl = document.getElementById('sidebarUserName');
                var statusEl = document.querySelector('.sidebar-user .user-status');
                if (nameEl) nameEl.textContent = user.username;
                if (statusEl) statusEl.textContent = '已登录';
            }
        } catch (_) {}
    }
})();

// ===== XSS 防护工具 =====
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ===== 动态星空背景 =====
function createStars() {
    const stars = document.getElementById('stars');
    if (!stars) return;
    
    const count = 100;
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.width = star.style.height = Math.random() * 3 + 1 + 'px';
        star.style.setProperty('--dur', Math.random() * 3 + 2 + 's');
        stars.appendChild(star);
    }
}

// 页面加载时创建星空
document.addEventListener('DOMContentLoaded', createStars);

// ===== 显示提示框 =====
function showToast(message, duration = 2000) {
    // 移除已有的提示框
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 创建新的提示框
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // 显示提示框
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // 自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

// ===== 打开表单页面 =====
function openForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.classList.add('show');
    }
}

// ===== 关闭表单页面 =====
function closeForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.classList.remove('show');
    }
}

// ===== 打开结果页面 =====
function openResult(resultId) {
    const result = document.getElementById(resultId);
    if (result) {
        result.classList.add('show');
    }
}

// ===== 关闭结果页面 =====
function closeResult(resultId) {
    const result = document.getElementById(resultId);
    if (result) {
        result.classList.remove('show');
    }
}

// ===== 页面切换 =====
function showPage(page) {
    // 更新底部导航状态
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    if (page === 'home') {
        navItems[0].classList.add('active');
        // 显示首页内容
        const main = document.querySelector('.main');
        if (main) main.style.display = 'block';
    } else if (page === 'more') {
        navItems[1].classList.add('active');
        // 显示更多页面
        showToast('更多功能页面开发中...');
    } else if (page === 'user') {
        navItems[2].classList.add('active');
        // 显示用户页面
        showToast('用户中心页面开发中...');
    }
}

// ===== 搜索功能 =====
function initSearch() {
    const searchInput = document.querySelector('.sch-in');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const keyword = e.target.value.toLowerCase();
        const items = document.querySelectorAll('.item');
        
        items.forEach(item => {
            const label = item.querySelector('.lb').textContent.toLowerCase();
            if (label.includes(keyword)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// ===== 全站版本号 + 备案号注入（modules页面无footer.js时自动显示） =====
(function() {
    var FALLBACK_VERSION = 'v1.0.0';
    var FALLBACK_COMMIT = 'unknown';
    var ICP_NUMBER = '辽ICP备2026010972号-1';
    var ICP_URL = 'https://beian.miit.gov.cn/';

    function injectVersionFooter(version, commit) {
        // 如果 footer.js 已注入 site-footer 则跳过，避免重复
        if (document.querySelector('.site-footer')) return;
        var container = document.body;
        if (!container) return;
        var html = '<div class="site-footer" style="text-align:center;padding:1.5rem 1rem 4rem;margin-top:2rem;border-top:1px solid rgba(232,184,75,0.08);">' +
            '<div style="margin-bottom:0.5rem;">' +
            '<span style="display:inline-block;background:rgba(232,184,75,0.08);border-radius:4px;padding:0.15rem 0.5rem;' +
            'font-family:monospace;font-size:0.68rem;color:rgba(232,184,75,0.5);letter-spacing:0.5px;">' +
            version + ' · ' + commit + '</span></div>' +
            '<div style="font-size:0.7rem;">' +
            '<a href="' + ICP_URL + '" target="_blank" rel="noopener" ' +
            'style="color:rgba(255,255,255,0.3);text-decoration:none;">' + ICP_NUMBER + '</a>' +
            '<span style="color:rgba(255,255,255,0.1);margin:0 0.6rem;">|</span>' +
            '<span style="color:rgba(255,255,255,0.12);">公安联网备案审核中</span>' +
            '</div></div>';
        var div = document.createElement('div');
        div.innerHTML = html;
        container.appendChild(div.firstElementChild);
    }

    function tryInject() {
        fetch('/version.json?_=' + Date.now())
            .then(function(resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.json();
            })
            .then(function(data) {
                var version = data.version ? 'v' + data.version : FALLBACK_VERSION;
                var commit = data.git_commit || FALLBACK_COMMIT;
                injectVersionFooter(version, commit);
            })
            .catch(function() {
                injectVersionFooter(FALLBACK_VERSION, FALLBACK_COMMIT);
            });
    }

    // 等 DOM 就绪后再注入
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', tryInject);
    } else {
        tryInject();
    }
})();

// ===== 广告模块加载（modules页面无footer.js时自动加载） =====
(function() {
    if (window.BaiduAd) return;
    if (document.querySelector('script[src*="ads.js"]')) return;
    var s = document.createElement('script');
    s.src = '/js/ads.js?v=1.3.0';
    s.async = true;
    document.head.appendChild(s);
})();

// ===== 动态背景加载（modules页面无footer.js时自动加载） =====
(function() {
    if (document.getElementById('__bgCanvas')) return;
    if (document.querySelector('script[src*="bg.js"]')) return;
    var s = document.createElement('script');
    s.src = '/js/bg.js?v=1.4.3';
    s.async = true;
    document.head.appendChild(s);
})();

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initDesktopSidebar();
});

// ===== 桌面端侧边栏初始化 =====
function initDesktopSidebar() {
    var sidebarUser = document.getElementById('sidebarUser');
    var sidebarUserName = document.getElementById('sidebarUserName');
    if (!sidebarUser || !sidebarUserName) return;
    
    var token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (token) {
        var user = null;
        try {
            var raw = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
            if (raw) user = JSON.parse(raw);
        } catch(e) {}
        if (user && user.username) {
            sidebarUserName.textContent = user.username;
            sidebarUser.querySelector('.user-status').textContent = '已登录';
            sidebarUser.href = '/profile.html';
        }
    } else {
        sidebarUserName.textContent = '未登录';
        sidebarUser.querySelector('.user-status').textContent = '点击登录';
        sidebarUser.href = '/login.html';
    }
    
    // 高亮当前页面
    var currentPath = window.location.pathname;
    var sidebarItems = document.querySelectorAll('.sidebar-nav-item');
    sidebarItems.forEach(function(item) {
        var href = item.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            item.classList.add('active');
        }
    });
}

// ===== 八字排盘计算（简化版） =====
function calcBaziSimple(birthDate, birthTime) {
    // 天干地支
    const tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
    const dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

    // 五行对应
    const wuxingMap = {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
        '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
        '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
        '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
        '戌': '土', '亥': '水'
    };

    // 根据出生日期计算四柱（简化算法）
    const date = new Date(birthDate);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    // 年柱（简化）
    const yearGan = tiangan[(year - 4) % 10];
    const yearZhi = dizhi[(year - 4) % 12];

    // 月柱（简化）
    const monthGan = tiangan[(year * 2 + month) % 10];
    const monthZhi = dizhi[(month + 1) % 12];

    // 日柱（简化）
    const dayGan = tiangan[(year * 5 + month * 3 + day) % 10];
    const dayZhi = dizhi[(year * 3 + month * 2 + day) % 12];

    // 时柱（简化）
    const shichenMap = {'子':0,'丑':1,'寅':2,'卯':3,'辰':4,'巳':5,'午':6,'未':7,'申':8,'酉':9,'戌':10,'亥':11};
    const timeChar = birthTime ? birthTime.charAt(0) : '子';
    const timeIdx = shichenMap[timeChar] !== undefined ? shichenMap[timeChar] : 0;
    // 时干推算：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
    const dayGanIdx = tiangan.indexOf(dayGan);
    const hourGanIdx = (dayGanIdx % 5) * 2 + timeIdx;
    const hourGan = tiangan[hourGanIdx % 10];
    const hourZhi = dizhi[timeIdx];

    // 四柱
    const pillars = {
        year: yearGan + yearZhi,
        month: monthGan + monthZhi,
        day: dayGan + dayZhi,
        hour: hourGan + hourZhi
    };

    // 五行统计
    const wuxing = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0};
    const allChars = pillars.year + pillars.month + pillars.day + pillars.hour;

    for (let char of allChars) {
        if (wuxingMap[char]) {
            wuxing[wuxingMap[char]]++;
        }
    }

    return {
        pillars: pillars,
        wuxing: wuxing,
        dayMaster: dayGan,
        dayMasterElement: wuxingMap[dayGan]
    };
}

// ===== 生成八字排盘结果 HTML =====
function generateBaziResultHTML(data) {
    const { pillars, wuxing, dayMaster, dayMasterElement } = data;
    
    let html = `
        <div class="result-section fade-in">
            <h3>☯ 四柱八字</h3>
            <table class="result-table">
                <tr>
                    <th>年柱</th>
                    <th>月柱</th>
                    <th>日柱</th>
                    <th>时柱</th>
                </tr>
                <tr>
                    <td>${pillars.year}</td>
                    <td>${pillars.month}</td>
                    <td>${pillars.day}</td>
                    <td>${pillars.hour}</td>
                </tr>
            </table>
        </div>
        
        <div class="result-section fade-in">
            <h3>⚖️ 五行统计</h3>
            <table class="result-table">
                <tr>
                    <th>五行</th>
                    <th>数量</th>
                    <th>状态</th>
                </tr>
    `;
    
    // 修复：用 Object.keys 代替 for...in
    const wuxingOrder = ['木','火','土','金','水'];
    for (let i = 0; i < wuxingOrder.length; i++) {
        const element = wuxingOrder[i];
        const count = wuxing[element];
        let status = '';
        if (count === 0) {
            status = '缺';
        } else if (count <= 1) {
            status = '弱';
        } else if (count <= 2) {
            status = '中';
        } else {
            status = '旺';
        }
        
        html += `
                <tr>
                    <td>${element}</td>
                    <td>${count}</td>
                    <td>${status}</td>
                </tr>
        `;
    }
    
    // 修复：喜用神根据日主五行判断，不用随机
    const dayMasterIdx = ['木','火','土','金','水'].indexOf(dayMasterElement);
    const xiyong = [];
    const jishen = [];
    // 日主偏强：喜克泄耗（官杀、食伤、财星）
    // 日主偏弱：喜生扶（印星、比劫）
    const isStrong = wuxing[dayMasterElement] >= 2;
    if (isStrong) {
        // 喜：克我（官杀）、我生（食伤）、我克（财）
        xiyong.push(['金','木','水','火','土'][(dayMasterIdx+4)%5]); // 官杀
        xiyong.push(['金','木','水','火','土'][(dayMasterIdx+2)%5]); // 食伤
    } else {
        // 喜：生我（印）、同我（比劫）
        xiyong.push(['金','木','水','火','土'][(dayMasterIdx+4)%5]); // 印
        xiyong.push(dayMasterElement); // 比劫
    }
    // 忌神取相反的五行
    jishen.push(['金','木','水','火','土'][(dayMasterIdx+3)%5]);
    jishen.push(['金','木','水','火','土'][(dayMasterIdx+1)%5]);

    html += `
            </table>
        </div>
        
        <div class="result-section fade-in">
            <h3>📊 命局分析</h3>
            <p><strong>日主：</strong>${dayMaster}（${dayMasterElement}）</p>
            <p><strong>日主强弱：</strong>${isStrong ? '偏强' : '偏弱'}</p>
            <p><strong>喜用神：</strong>${[...new Set(xiyong)].join('、')}</p>
            <p><strong>忌神：</strong>${[...new Set(jishen)].join('、')}</p>
        </div>
    `;
    
    return html;
}

// ===== 导出函数 =====
// 如果你的其他脚本需要这些函数，可以将它们添加到 global 对象
window.createStars = createStars;
window.showToast = showToast;
window.openForm = openForm;
window.closeForm = closeForm;
window.openResult = openResult;
window.closeResult = closeResult;
window.showPage = showPage;
window.calcBaziSimple = calcBaziSimple;
window.generateBaziResultHTML = generateBaziResultHTML;

// ===== 首页模块跳转函数 =====
function openBazi() { window.location.href = '/modules/bazi.html'; }
function openZiwei() { window.location.href = '/modules/ziwei.html'; }
function openHeyun() { window.location.href = '/modules/heyun.html'; }
function openShengxiao() { window.location.href = '/modules/shengxiao.html'; }
function openXingming() { window.location.href = '/modules/xingming.html'; }
function openTarot() { window.location.href = '/modules/tarot.html'; }
function openFengshui() { window.location.href = '/modules/fengshui.html'; }
function openZhougong() { window.location.href = '/modules/zhougong.html'; }
function openHuangdao() { window.location.href = '/modules/huangdao.html'; }
function openJiexing() { window.location.href = '/modules/jiexing.html'; }
function openCaishen() { window.location.href = '/modules/caishen.html'; }

// ===== 图片上传智能分析（通用） =====
function triggerImageUpload(moduleType) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function() {
        const file = this.files[0];
        if (!file) return;
        showToast('正在分析图片...');
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64 = e.target.result;
            fetch('/api/image-analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64, module_type: moduleType })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showImageAnalysisResult(data.analysis, data.image_info);
                } else {
                    showToast('分析失败：' + (data.message || '未知错误'));
                }
            })
            .catch(err => {
                showToast('分析失败，请检查网络');
                console.error('图片分析错误：', err);
            });
        };
        reader.readAsDataURL(file);
    };
    input.click();
}

function showImageAnalysisResult(analysisText, imageInfo) {
    let html = '<div class="image-analysis-result" style="background:linear-gradient(135deg,rgba(232,184,75,0.08),rgba(232,184,75,0.02));border:1px solid rgba(232,184,75,0.15);border-radius:12px;padding:1.5rem;margin-top:1rem;">';
    html += '<h3 style="color:#e8b84b;margin-bottom:1rem;">📷 图片分析结果</h3>';
    html += '<pre style="white-space:pre-wrap;font-family:inherit;color:rgba(255,255,255,0.85);line-height:1.8;font-size:0.9rem;">' + analysisText + '</pre>';
    if (imageInfo) {
        html += '<div style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid rgba(232,184,75,0.1);color:rgba(255,255,255,0.5);font-size:0.8rem;">';
        html += '图片信息：' + imageInfo.width + '×' + imageInfo.height + ' | 主色调：' + imageInfo.dominant_color + ' | 亮度：' + imageInfo.brightness;
        html += '</div>';
    }
    html += '<button onclick="this.parentElement.remove();" style="margin-top:1rem;background:rgba(232,184,75,0.2);color:#e8b84b;border:1px solid rgba(232,184,75,0.3);border-radius:8px;padding:0.5rem 1rem;cursor:pointer;">关闭</button>';
    html += '</div>';

    // 尝试插入到结果区域
    const resultArea = document.getElementById('resultArea') || document.getElementById('analysisResult') || document.querySelector('.result-area');
    if (resultArea) {
        resultArea.innerHTML = html;
        resultArea.style.display = 'block';
    } else {
        // 如果找不到结果区域，就追加到 content-area
        const contentArea = document.querySelector('.content-area');
        if (contentArea) {
            const div = document.createElement('div');
            div.innerHTML = html;
            contentArea.appendChild(div.firstChild);
        } else {
            showToast('分析完成！请在页面查看结果');
            console.log('图片分析结果：', analysisText);
        }
    }
}

function openMore() { window.location.href = '/more.html'; }

// ===== 桌面端侧边栏用户信息更新 =====
(function() {
    // 仅在桌面端（有侧边栏时）执行
    var sidebar = document.getElementById('desktopSidebar');
    if (!sidebar) return;
    
    var token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (!token) return;
    
    // 尝试从本地存储读取用户信息
    var user = null;
    try {
        var raw = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
        if (raw) user = JSON.parse(raw);
    } catch(e) {}
    
    if (!user || !user.username) {
        // 如果有token但没有本地用户信息，从API获取
        fetch('/api/profile', {
            headers: { 'Authorization': 'Bearer ' + token }
        })
        .then(function(resp) { return resp.json(); })
        .then(function(data) {
            if (data.success && data.user) {
                updateSidebarUser(data.user);
            }
        })
        .catch(function() {});
        return;
    }
    
    updateSidebarUser(user);
    
    function updateSidebarUser(u) {
        var nameEl = document.getElementById('sidebarUserName');
        var statusEl = sidebar.querySelector('.user-status');
        if (nameEl) nameEl.textContent = u.username || '用户';
        if (statusEl) statusEl.textContent = '已登录';
        
        // 更新VIP等级显示
        if (u.vip_level && u.vip_level !== 'free') {
            var badge = document.createElement('span');
            badge.className = 'nav-badge';
            badge.textContent = u.vip_level === 'premium' ? '高级' : '基础';
            badge.style.cssText = 'margin-left:auto;font-size:0.7rem;padding:0.15rem 0.5rem;border-radius:10px;background:rgba(232,184,75,0.15);color:#e8b84b;';
            var sidebarUserEl = document.getElementById('sidebarUser');
            if (sidebarUserEl && !sidebarUserEl.querySelector('.nav-badge')) {
                sidebarUserEl.querySelector('.user-info').appendChild(badge);
            }
        }
    }
})();