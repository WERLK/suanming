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

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
});

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
    const timeIndex = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'].indexOf(birthTime.charAt(0));
    const safeIndex = timeIndex === -1 ? 0 : timeIndex;
    const hourGan = tiangan[(dayGan.charCodeAt(0) - 19968 + safeIndex) % 10];
    const hourZhi = dizhi[safeIndex];
    
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
    
    for (let element in wuxing) {
        const count = wuxing[element];
        let status = '';
        if (count === 0) {
            status = '缺';
        } else if (count === 1) {
            status = '弱';
        } else if (count === 2) {
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
    
    html += `
            </table>
        </div>
        
        <div class="result-section fade-in">
            <h3>📊 命局分析</h3>
            <p><strong>日主：</strong>${dayMaster}（${dayMasterElement}）</p>
            <p><strong>日主强弱：</strong>${wuxing[dayMasterElement] >= 2 ? '偏强' : '偏弱'}</p>
            <p><strong>喜用神：</strong>${Object.keys(wuxing).sort(() => Math.random() - 0.5).slice(0, 2).join('、')}</p>
            <p><strong>忌神：</strong>${Object.keys(wuxing).sort(() => Math.random() - 0.5).slice(0, 2).join('、')}</p>
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