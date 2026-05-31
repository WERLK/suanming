/**
 * 玄机算命网 - 侧边导航菜单
 * 替代底部导航栏，右侧滑出，可折叠
 */
(function() {
    'use strict';

    var sidebar = null;
    var overlay = null;
    var fab = null;
    var isOpen = false;

    // 当前页面路径
    var path = window.location.pathname;

    // 导航项配置
    var navItems = [
        { icon: '🏠', label: '首页', href: '/', match: /^\/(index\.html)?$/ },
        { icon: '🔮', label: '更多模块', href: '/more.html', match: /more\.html/ },
        { icon: '👑', label: '会员中心', href: '/vip.html', match: /vip\.html/ },
        { icon: '👤', label: '个人中心', href: '/profile.html', match: /profile\.html/ },
        { icon: '👥', label: '亲友档案', href: '/contacts.html', match: /contacts\.html/ },
        { icon: '📋', label: '数据表格', href: '/datasets.html', match: /datasets\.html/ }
    ];

    function isActive(item) {
        return item.match.test(path);
    }

    // ===== 构建 DOM =====
    function buildSidebar() {
        // 遮罩层
        overlay = document.createElement('div');
        overlay.id = '__sideOverlay';
        overlay.style.cssText =
            'position:fixed;top:0;left:0;right:0;bottom:0;z-index:9990;'
            + 'background:rgba(0,0,0,0.5);backdrop-filter:blur(2px);'
            + 'opacity:0;transition:opacity 0.3s ease;pointer-events:none;';
        overlay.onclick = closeSidebar;

        // 侧边栏
        sidebar = document.createElement('nav');
        sidebar.id = '__sideNav';
        sidebar.style.cssText =
            'position:fixed;top:0;left:0;bottom:0;width:220px;z-index:9991;'
            + 'background:linear-gradient(180deg,rgba(20,20,35,0.98) 0%,rgba(15,12,41,0.98) 100%);'
            + 'backdrop-filter:blur(20px);border-right:1px solid rgba(255,215,0,0.12);'
            + 'transform:translateX(-100%);transition:transform 0.3s cubic-bezier(0.4,0,0.2,1);'
            + 'display:flex;flex-direction:column;overflow-y:auto;overscroll-behavior:contain;';

        // 标题
        var header = document.createElement('div');
        header.style.cssText =
            'padding:1rem 1rem 0.6rem;border-bottom:1px solid rgba(255,215,0,0.1);';
        header.innerHTML =
            '<div style="font-size:1rem;color:#ffd700;font-weight:bold;display:flex;align-items:center;gap:6px;">'
            + '🔮 玄机算命网</div>'
            + '<div style="font-size:0.7rem;color:rgba(255,255,255,0.4);margin-top:3px;">导航菜单</div>';
        sidebar.appendChild(header);

        // 导航项
        var nav = document.createElement('div');
        nav.style.cssText = 'padding:0.5rem 0;flex:1;';

        navItems.forEach(function(item) {
            var a = document.createElement('a');
            a.href = item.href;
            var active = isActive(item);
            a.style.cssText =
                'display:flex;align-items:center;gap:10px;padding:0.7rem 1rem;'
                + 'color:' + (active ? '#ffd700' : 'rgba(255,255,255,0.75)') + ';'
                + 'text-decoration:none;font-size:0.88rem;'
                + 'transition:all 0.2s;cursor:pointer;'
                + (active ? 'background:rgba(255,215,0,0.08);border-right:2px solid #ffd700;' : '');
            a.innerHTML =
                '<span style="font-size:1.2rem;">' + item.icon + '</span>'
                + '<span>' + item.label + '</span>';
            a.onmouseenter = function() { if (!active) this.style.background = 'rgba(255,215,0,0.06)'; };
            a.onmouseleave = function() { if (!active) this.style.background = ''; };
            nav.appendChild(a);
        });

        sidebar.appendChild(nav);

        // 底部用户信息区
        var footer = document.createElement('div');
        footer.style.cssText =
            'padding:0.8rem 1rem;border-top:1px solid rgba(255,215,0,0.08);';
        footer.innerHTML =
            '<a href="/profile.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:rgba(255,255,255,0.6);">'
            + '<div style="width:32px;height:32px;border-radius:50%;background:rgba(255,215,0,0.1);'
            + 'display:flex;align-items:center;justify-content:center;font-size:1rem;">👤</div>'
            + '<div><div id="__sideUserName" style="font-size:0.8rem;color:rgba(255,255,255,0.8);">未登录</div>'
            + '<div style="font-size:0.65rem;color:rgba(255,255,255,0.4);">点击登录</div></div></a>';
        sidebar.appendChild(footer);

        document.body.appendChild(overlay);
        document.body.appendChild(sidebar);

        // 更新用户名
        updateUserName();
    }

    function updateUserName() {
        var el = document.getElementById('__sideUserName');
        if (!el) return;
        try {
            var raw = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
            if (raw) {
                var user = JSON.parse(raw);
                if (user && user.username) {
                    el.textContent = user.username;
                    var sub = el.nextElementSibling;
                    if (sub) sub.textContent = '已登录';
                }
            }
        } catch(e) {}
    }

    // ===== FAB 按钮 =====
    function buildFAB() {
        fab = document.createElement('div');
        fab.id = '__sideFab';
        fab.style.cssText =
            'position:fixed;top:40px;left:10px;z-index:9980;'
            + 'width:36px;height:36px;border-radius:8px;'
            + 'background:rgba(20,20,35,0.9);'
            + 'border:1px solid rgba(255,215,0,0.25);'
            + 'color:#ffd700;font-size:1.1rem;'
            + 'display:flex;align-items:center;justify-content:center;'
            + 'cursor:pointer;transition:all 0.3s ease;'
            + 'box-shadow:0 2px 10px rgba(0,0,0,0.3);'
            + 'user-select:none;-webkit-tap-highlight-color:transparent;';
        fab.innerHTML = '☰';
        fab.title = '导航菜单';
        fab.onclick = toggleSidebar;

        fab.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255,215,0,0.12)';
            this.style.borderColor = 'rgba(255,215,0,0.5)';
        });
        fab.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(20,20,35,0.9)';
            this.style.borderColor = 'rgba(255,215,0,0.25)';
        });

        document.body.appendChild(fab);
    }

    // ===== 开/关 =====
    function openSidebar() {
        isOpen = true;
        sidebar.style.transform = 'translateX(0)';
        overlay.style.opacity = '1';
        overlay.style.pointerEvents = 'auto';
        fab.style.opacity = '0.4';
        fab.style.pointerEvents = 'none';
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        isOpen = false;
        sidebar.style.transform = 'translateX(-100%)';
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
        fab.style.opacity = '1';
        fab.style.pointerEvents = '';
        document.body.style.overflow = '';
    }

    function toggleSidebar() {
        if (isOpen) closeSidebar(); else openSidebar();
    }

    // ===== 替换 bottom-nav =====
    function removeBottomNav() {
        var navs = document.querySelectorAll('.bottom-nav');
        navs.forEach(function(nav) {
            nav.style.display = 'none';
        });
    }

    // ===== 初始化 =====
    function init() {
        buildSidebar();
        buildFAB();
        removeBottomNav();

        // ESC 关闭
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isOpen) closeSidebar();
        });

        // 登录状态变化
        window.addEventListener('storage', function(e) {
            if (e.key === 'currentUser' || e.key === 'token') {
                updateUserName();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('[导航] 侧边菜单已加载');
})();
