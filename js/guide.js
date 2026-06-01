/**
 * 玄机算命网 - 新手引导教程
 * 
 * 触发条件: 用户已登录 且 服务端 tutorial_shown === false
 * 完成后: POST /api/profile/tutorial-done 服务端标记, 永不再显示
 */
window.startGuide = (function() {
    'use strict';

    // 仅在首页运行
    var path = window.location.pathname;
    if (!/^\/(index\.html)?$/.test(path)) return function(){};

    var overlay = null;
    var spotlight = null;
    var tooltip = null;
    var currentStep = -1;
    var totalSteps = 0;
    var running = false;
    var authToken = '';

    function getToken() {
        if (authToken) return authToken;
        var t = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (t) authToken = t;
        return authToken;
    }

    // 教程步骤定义 (video 可选)
    var steps = [
        {
            selector: null,
            title: '🔮 欢迎来到玄机算命网',
            content: '传承千年易经智慧，为您提供八字排盘、紫微斗数、合婚配对等多种命理分析服务。\n\n观看下方 30 秒快速了解核心功能 👇',
            video: '/static/videos/guide-intro.mp4',
            poster: '/static/videos/guide-poster.jpg',
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
            content: '输入出生日期，系统自动排出八字命盘，分析五行、十神、大运流年。',
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
            content: '姓名测试、塔罗牌、风水堪舆、周公解梦、黄道吉日……十余种功能供您探索。',
            position: 'top'
        },
        {
            selector: '#__sideNav',
            title: '👤 您的账户',
            content: '菜单底部有您的账户信息。个人中心可查看历史记录、管理亲友档案、上传实名认证。',
            position: 'right'
        }
    ];

    totalSteps = steps.length;

    // ===== 注入样式 =====
    function injectStyle() {
        var style = document.createElement('style');
        style.id = '__guideStyle';
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
            + '  padding:1.5rem;max-width:360px;min-width:260px;'
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
            + '.guide-video-wrap {'
            + '  margin:0 0 1rem;border-radius:10px;overflow:hidden;'
            + '  background:#000;position:relative;'
            + '}'
            + '.guide-video-wrap video {'
            + '  width:100%;display:block;border-radius:10px;'
            + '}'
            + '.guide-video-poster {'
            + '  width:100%;display:block;border-radius:10px;'
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
            + '  #__guideTooltip { max-width:290px;padding:1.2rem; }'
            + '  #__guideTooltip h3 { font-size:0.95rem; }'
            + '  #__guideTooltip p { font-size:0.8rem; }'
            + '}';
        document.head.appendChild(style);
    }

    // ===== 构建 DOM =====
    function buildDOM() {
        overlay = document.createElement('div');
        overlay.id = '__guideOverlay';
        document.body.appendChild(overlay);

        spotlight = document.createElement('div');
        spotlight.id = '__guideSpotlight';
        document.body.appendChild(spotlight);

        tooltip = document.createElement('div');
        tooltip.id = '__guideTooltip';
        document.body.appendChild(tooltip);
    }

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
        } else {
            spotlight.style.left = '50%';
            spotlight.style.top = '50%';
            spotlight.style.width = '0px';
            spotlight.style.height = '0px';
            spotlight.style.opacity = '0';
        }

        // 提示框定位
        var tLeft, tTop;
        if (step.position === 'center' || !target) {
            tLeft = Math.max(20, (window.innerWidth - 340) / 2);
            tTop = Math.max(40, (window.innerHeight - 420) / 2);
        } else if (step.position === 'right') {
            var rect = target.getBoundingClientRect();
            tLeft = Math.min(rect.right + 16, window.innerWidth - 360);
            tTop = Math.max(20, rect.top + rect.height / 2 - 200);
        } else if (step.position === 'bottom') {
            var rect = target.getBoundingClientRect();
            tLeft = Math.max(20, Math.min(rect.left + rect.width / 2 - 170, window.innerWidth - 360));
            tTop = Math.min(rect.bottom + 16, window.innerHeight - 400);
        } else if (step.position === 'top') {
            var rect = target.getBoundingClientRect();
            tLeft = Math.max(20, Math.min(rect.left + rect.width / 2 - 170, window.innerWidth - 360));
            tTop = Math.max(20, rect.top - 400);
        }

        tooltip.style.left = tLeft + 'px';
        tooltip.style.top = tTop + 'px';
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'scale(1)';

        // 圆点指示器
        var dotsHtml = '';
        for (var i = 0; i < totalSteps; i++) {
            var cls = i === index ? ' active' : i < index ? ' done' : '';
            dotsHtml += '<span class="' + cls + '"></span>';
        }

        // 视频元素（如有）
        var videoHtml = '';
        if (step.video) {
            videoHtml = '<div class="guide-video-wrap">'
                + '<video id="__guideVideo" controls playsinline autoplay muted '
                + (step.poster ? 'poster="' + step.poster + '" ' : '')
                + 'onerror="this.style.display=\'none\'">'
                + '<source src="' + step.video + '" type="video/mp4">'
                + '</video>'
                + '</div>';
        }

        tooltip.innerHTML = ''
            + '<h3>' + step.title + '</h3>'
            + videoHtml
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
        document.getElementById('__guideSkip').onclick = finishAndMark;
        document.getElementById('__guideNext').onclick = function() {
            if (index < totalSteps - 1) {
                showStep(index + 1);
            } else {
                finishAndMark();
            }
        };
        var prevBtn = document.getElementById('__guidePrev');
        if (prevBtn) {
            prevBtn.onclick = function() {
                showStep(index - 1);
            };
        }
    }

    function showStep(index) {
        currentStep = index;
        renderStep(index);
    }

    // ===== 完成并服务端标记 =====
    function finishAndMark() {
        // 调用后端标记
        var token = getToken();
        if (token) {
            try {
                fetch('/api/profile/tutorial-done', {
                    method: 'POST',
                    headers: { 'Authorization': 'Bearer ' + token }
                }).catch(function(){});
            } catch(e) {}
        }

        // 动画退出
        if (overlay) { overlay.style.opacity = '0'; overlay.style.pointerEvents = 'none'; }
        if (spotlight) spotlight.style.opacity = '0';
        if (tooltip) { tooltip.style.opacity = '0'; tooltip.style.transform = 'scale(0.95)'; }
        setTimeout(function() {
            if (overlay) overlay.remove();
            if (spotlight) spotlight.remove();
            if (tooltip) tooltip.remove();
            var s = document.getElementById('__guideStyle');
            if (s) s.remove();
            running = false;
        }, 350);
    }

    // ===== resize 重绘 =====
    window.addEventListener('resize', function() {
        if (running && currentStep >= 0) renderStep(currentStep);
    });

    // ===== 真正的启动函数 =====
    function launch() {
        if (running) return;
        running = true;
        injectStyle();
        buildDOM();
        // 等侧边栏动画完成
        setTimeout(function() {
            showStep(0);
        }, 500);
    }

    // ===== 自动检测是否需要引导 =====
    function autoCheck() {
        var token = getToken();
        if (!token) {
            console.log('[引导] 未登录，跳过');
            return;
        }

        fetch('/api/profile', {
            headers: { 'Authorization': 'Bearer ' + token }
        }).then(function(r) { return r.json(); })
          .then(function(data) {
              if (data.success && data.user && data.user.tutorial_shown === false) {
                  console.log('[引导] 新用户首次登录，启动教程');
                  launch();
              } else {
                  console.log('[引导] 已完成或非新用户，跳过');
              }
          })
          .catch(function() {
              console.log('[引导] API 调用失败，跳过');
          });
    }

    // 导出 startGuide 供手动调用（register/login 成功后）
    function startGuide() {
        launch();
    }

    // 页面加载后 600ms 自动检测
    setTimeout(autoCheck, 600);

    return startGuide;
})();
