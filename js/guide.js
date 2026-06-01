/**
 * 玄机算命网 - 新手引导教程
 * 首次访问首页时自动触发，逐步介绍核心功能
 * 完成或跳过后面不再显示（localStorage 记录）
 */
(function() {
    'use strict';

    // 仅在首页触发
    var path = window.location.pathname;
    if (!/^\/(index\.html)?$/.test(path)) return;

    // 已完成或跳过则不显示
    if (localStorage.getItem('__guide_done') === '1') return;

    // ===== DOM 元素 =====
    var overlay = null;
    var spotlight = null;
    var tooltip = null;
    var currentStep = -1;
    var totalSteps = 0;

    // 教程步骤定义
    var steps = [
        {
            selector: null, // 居中显示
            title: '🔮 欢迎来到玄机算命网',
            content: '传承千年易经智慧，为您提供八字排盘、紫微斗数、合婚配对等多种命理分析服务。\n\n接下来只需 1 分钟，带您快速了解核心功能。',
            position: 'center'
        },
        {
            selector: '#__sideNav',
            title: '📋 导航菜单',
            content: '左侧折叠菜单，可快速跳转到首页、更多模块、会员中心、个人中心、亲友档案等页面。\n\n点击 ◀ 可收起菜单。',
            position: 'right'
        },
        {
            selector: '.hero-buttons .btn-primary',
            title: '🎴 八字排盘 — 核心功能',
            content: '点击这里可以输入出生日期，系统将自动排出您的八字命盘，分析五行、十神、大运流年。',
            position: 'bottom'
        },
        {
            selector: '.quick-access',
            title: '⚡ 快捷入口',
            content: '八字排盘、紫微斗数、合婚配对、生肖运势 — 最常用的四大功能，一键直达。',
            position: 'bottom'
        },
        {
            selector: '.featured-section',
            title: '🌟 更多算命模块',
            content: '姓名测试、塔罗牌、风水堪舆、周公解梦、黄道吉日、流年解星、财神方位……十余种功能供您探索。',
            position: 'top'
        },
        {
            selector: '#__sideNav',
            title: '👤 您的账户',
            content: '菜单底部有您的账户信息。注册/登录后可解锁更多高级功能，保存亲友档案和历史记录。',
            position: 'right'
        }
    ];

    totalSteps = steps.length;

    // ===== 注入样式 =====
    var style = document.createElement('style');
    style.textContent = ''
        + '#__guideOverlay {'
        + '  position:fixed;top:0;left:0;right:0;bottom:0;z-index:9998;'
        + '  background:rgba(0,0,0,0.65);transition:opacity 0.3s;'
        + '}'
        + '#__guideSpotlight {'
        + '  position:fixed;z-index:9999;border-radius:12px;'
        + '  box-shadow:0 0 0 9999px rgba(0,0,0,0.65);'
        + '  transition:all 0.35s cubic-bezier(0.4,0,0.2,1);'
        + '  pointer-events:none;'
        + '}'
        + '#__guideTooltip {'
        + '  position:fixed;z-index:10000;'
        + '  background:linear-gradient(180deg,rgba(22,22,45,0.98),rgba(15,12,41,0.98));'
        + '  border:1px solid rgba(255,215,0,0.25);border-radius:16px;'
        + '  padding:1.5rem;max-width:320px;min-width:240px;'
        + '  box-shadow:0 8px 40px rgba(0,0,0,0.5);'
        + '  transition:all 0.35s cubic-bezier(0.4,0,0.2,1);'
        + '  color:#fff;'
        + '}'
        + '#__guideTooltip h3 {'
        + '  color:#ffd700;font-size:1.05rem;margin:0 0 0.6rem;'
        + '}'
        + '#__guideTooltip p {'
        + '  color:rgba(255,255,255,0.75);font-size:0.88rem;line-height:1.65;margin:0 0 1rem;'
        + '  white-space:pre-line;'
        + '}'
        + '#__guideNav {'
        + '  display:flex;align-items:center;justify-content:space-between;gap:0.5rem;'
        + '}'
        + '#__guideDots {'
        + '  display:flex;gap:6px;'
        + '}'
        + '#__guideDots span {'
        + '  width:6px;height:6px;border-radius:50%;'
        + '  background:rgba(255,255,255,0.2);transition:all 0.3s;'
        + '}'
        + '#__guideDots span.active {'
        + '  background:#ffd700;width:18px;border-radius:3px;'
        + '}'
        + '#__guideDots span.done {'
        + '  background:rgba(255,215,0,0.4);'
        + '}'
        + '.guide-btn {'
        + '  padding:0.45rem 0.9rem;border-radius:8px;font-size:0.82rem;cursor:pointer;'
        + '  border:none;font-weight:bold;transition:all 0.2s;'
        + '}'
        + '.guide-btn-skip {'
        + '  background:transparent;color:rgba(255,255,255,0.45);'
        + '}'
        + '.guide-btn-skip:hover { color:rgba(255,255,255,0.75); }'
        + '.guide-btn-prev {'
        + '  background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.6);'
        + '}'
        + '.guide-btn-prev:hover { background:rgba(255,255,255,0.12); }'
        + '.guide-btn-next {'
        + '  background:linear-gradient(135deg,#ffd700,#ffaa00);color:#1a1a2e;'
        + '}'
        + '.guide-btn-next:hover { opacity:0.9; }'
        + '@media (max-width:480px) {'
        + '  #__guideTooltip { max-width:280px;padding:1.2rem; }'
        + '  #__guideTooltip h3 { font-size:0.95rem; }'
        + '  #__guideTooltip p { font-size:0.8rem; }'
        + '}';
    document.head.appendChild(style);

    // ===== 构建 DOM =====
    overlay = document.createElement('div');
    overlay.id = '__guideOverlay';
    document.body.appendChild(overlay);

    spotlight = document.createElement('div');
    spotlight.id = '__guideSpotlight';
    document.body.appendChild(spotlight);

    tooltip = document.createElement('div');
    tooltip.id = '__guideTooltip';
    document.body.appendChild(tooltip);

    // ===== 定位和渲染 =====
    function renderStep(index) {
        var step = steps[index];
        var target = step.selector ? document.querySelector(step.selector) : null;

        // 聚光灯
        if (target && step.position !== 'center') {
            var rect = target.getBoundingClientRect();
            var pad = 8;
            spotlight.style.left = (rect.left - pad) + 'px';
            spotlight.style.top = (rect.top - pad) + 'px';
            spotlight.style.width = (rect.width + pad * 2) + 'px';
            spotlight.style.height = (rect.height + pad * 2) + 'px';
            spotlight.style.opacity = '1';
            spotlight.style.boxShadow = '0 0 0 9999px rgba(0,0,0,0.65)';
        } else {
            spotlight.style.left = '50%';
            spotlight.style.top = '50%';
            spotlight.style.width = '0px';
            spotlight.style.height = '0px';
            spotlight.style.opacity = '0';
        }

        // 提示框位置
        var tLeft, tTop;
        var arrow = step.position;

        if (step.position === 'center' || !target) {
            tLeft = Math.max(20, (window.innerWidth - 320) / 2);
            tTop = Math.max(60, (window.innerHeight - 300) / 2);
        } else if (step.position === 'right') {
            var rect = target.getBoundingClientRect();
            tLeft = Math.min(rect.right + 16, window.innerWidth - 340);
            tTop = Math.max(20, rect.top + rect.height / 2 - 180);
        } else if (step.position === 'bottom') {
            var rect = target.getBoundingClientRect();
            tLeft = Math.max(20, Math.min(rect.left + rect.width / 2 - 160, window.innerWidth - 340));
            tTop = Math.min(rect.bottom + 16, window.innerHeight - 380);
        } else if (step.position === 'top') {
            var rect = target.getBoundingClientRect();
            tLeft = Math.max(20, Math.min(rect.left + rect.width / 2 - 160, window.innerWidth - 340));
            tTop = Math.max(20, rect.top - 380);
        }

        tooltip.style.left = tLeft + 'px';
        tooltip.style.top = tTop + 'px';
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'scale(1)';

        // 内容
        var dotsHtml = '';
        for (var i = 0; i < totalSteps; i++) {
            var cls = '';
            if (i === index) cls = ' active';
            else if (i < index) cls = ' done';
            dotsHtml += '<span class="' + cls + '"></span>';
        }

        tooltip.innerHTML = ''
            + '<h3>' + step.title + '</h3>'
            + '<p>' + step.content + '</p>'
            + '<div id="__guideNav">'
            + '<button class="guide-btn guide-btn-skip" id="__guideSkip">跳过</button>'
            + '<div id="__guideDots">' + dotsHtml + '</div>'
            + (index > 0
                ? '<button class="guide-btn guide-btn-prev" id="__guidePrev">上一步</button>'
                : '<span style="width:52px;"></span>')
            + '<button class="guide-btn guide-btn-next" id="__guideNext">'
            + (index < totalSteps - 1 ? '下一步 →' : '开始探索 ✨')
            + '</button>'
            + '</div>';

        // 按钮事件
        document.getElementById('__guideSkip').onclick = finishGuide;
        document.getElementById('__guideNext').onclick = function() {
            if (index < totalSteps - 1) {
                showStep(index + 1);
            } else {
                finishGuide();
            }
        };
        if (document.getElementById('__guidePrev')) {
            document.getElementById('__guidePrev').onclick = function() {
                showStep(index - 1);
            };
        }
    }

    function showStep(index) {
        currentStep = index;
        renderStep(index);
    }

    function finishGuide() {
        localStorage.setItem('__guide_done', '1');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
        }
        if (spotlight) spotlight.style.opacity = '0';
        if (tooltip) {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'scale(0.95)';
        }
        setTimeout(function() {
            if (overlay) overlay.remove();
            if (spotlight) spotlight.remove();
            if (tooltip) tooltip.remove();
        }, 350);
    }

    // ===== 窗口 resize 时重绘 =====
    window.addEventListener('resize', function() {
        if (currentStep >= 0) renderStep(currentStep);
    });

    // ===== 启动 =====
    // 延迟 600ms 等侧边栏动画完成
    setTimeout(function() {
        showStep(0);
    }, 600);

    console.log('[引导] 新手教程已启动');
})();
