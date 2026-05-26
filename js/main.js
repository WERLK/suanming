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
    let html = '<div class="image-analysis-result" style="background:linear-gradient(135deg,rgba(255,215,0,0.08),rgba(255,215,0,0.02));border:1px solid rgba(255,215,0,0.15);border-radius:12px;padding:1.5rem;margin-top:1rem;">';
    html += '<h3 style="color:#ffd700;margin-bottom:1rem;">📷 图片分析结果</h3>';
    html += '<pre style="white-space:pre-wrap;font-family:inherit;color:rgba(255,255,255,0.85);line-height:1.8;font-size:0.9rem;">' + analysisText + '</pre>';
    if (imageInfo) {
        html += '<div style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid rgba(255,215,0,0.1);color:rgba(255,255,255,0.5);font-size:0.8rem;">';
        html += '图片信息：' + imageInfo.width + '×' + imageInfo.height + ' | 主色调：' + imageInfo.dominant_color + ' | 亮度：' + imageInfo.brightness;
        html += '</div>';
    }
    html += '<button onclick="this.parentElement.remove();" style="margin-top:1rem;background:rgba(255,215,0,0.2);color:#ffd700;border:1px solid rgba(255,215,0,0.3);border-radius:8px;padding:0.5rem 1rem;cursor:pointer;">关闭</button>';
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