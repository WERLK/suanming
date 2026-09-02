/**
 * 玄机算命网 - 折叠版导航菜单（全站统一）
 * - 侧边栏默认展开, 可折叠
 * - 桌面端内容自动右移, 移动端覆盖显示
 */
(function() {
    'use strict';

    var sidebar = null;
    var overlay = null;
    var collapseBtn = null;
    var expandTab = null;
    var isOpen = false;

    var path = window.location.pathname;

    var navItems = [
        { icon: '🏠', label: '首页', href: '/', match: /^\/(index\.html)?$/ },
        { icon: '🔮', label: '更多模块', href: '/more.html', match: /more\.html/ },
        { icon: '👑', label: '会员中心', href: '/vip.html', match: /vip\.html/ },
        { icon: '👤', label: '个人中心', href: '/profile.html', match: /profile\.html/ },
        { icon: '👥', label: '亲友档案', href: '/contacts.html', match: /contacts\.html/ },
        { icon: '📋', label: '数据表格', href: '/datasets.html', match: /datasets\.html/ },
        { icon: '❓', label: '帮助中心', href: '/help.html', match: /help\.html/ },
        { icon: 'ℹ️', label: '关于我们', href: '/about.html', match: /about\.html/ },
        { icon: '📥', label: '下载客户端', href: '/download.html', match: /download\.html/ }
    ];

    function isActive(item) {
        return item.match.test(path);
    }

    // ===== 构建侧边栏 DOM =====
    function buildSidebar() {
        // 遮罩层（移动端用）
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
            + 'background:linear-gradient(180deg,rgba(20,20,35,0.98) 0%,rgba(10,14,31,0.98) 100%);'
            + 'backdrop-filter:blur(20px);border-right:1px solid rgba(232,184,75,0.12);'
            + 'transform:translateX(-100%);transition:transform 0.3s cubic-bezier(0.4,0,0.2,1);'
            + 'display:flex;flex-direction:column;overflow-y:auto;overscroll-behavior:contain;';

        // 标题行（含折叠按钮）
        var header = document.createElement('div');
        header.style.cssText =
            'padding:1rem 0.8rem 0.6rem;border-bottom:1px solid rgba(232,184,75,0.1);'
            + 'display:flex;align-items:flex-start;justify-content:space-between;';
        header.innerHTML =
            '<div>'
            + '<div style="font-size:1rem;color:#e8b84b;font-weight:bold;display:flex;align-items:center;gap:6px;">'
            + '🔮 玄机算命网</div>'
            + '<div style="font-size:0.7rem;color:rgba(255,255,255,0.4);margin-top:3px;">导航菜单</div>'
            + '</div>';

        // 折叠按钮
        collapseBtn = document.createElement('button');
        collapseBtn.id = '__sideCollapse';
        collapseBtn.style.cssText =
            'background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);'
            + 'color:rgba(255,255,255,0.5);font-size:1rem;cursor:pointer;'
            + 'width:28px;height:28px;border-radius:6px;'
            + 'display:flex;align-items:center;justify-content:center;'
            + 'transition:all 0.2s;flex-shrink:0;';
        collapseBtn.innerHTML = '◀';
        collapseBtn.title = '折叠菜单';
        collapseBtn.onmouseenter = function() { this.style.color = '#e8b84b'; this.style.borderColor = 'rgba(232,184,75,0.3)'; };
        collapseBtn.onmouseleave = function() { this.style.color = 'rgba(255,255,255,0.5)'; this.style.borderColor = 'rgba(255,255,255,0.1)'; };
        collapseBtn.onclick = function(e) { e.stopPropagation(); closeSidebar(); };
        header.appendChild(collapseBtn);

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
                + 'color:' + (active ? '#e8b84b' : 'rgba(255,255,255,0.75)') + ';'
                + 'text-decoration:none;font-size:0.88rem;'
                + 'transition:all 0.2s;cursor:pointer;'
                + (active ? 'background:rgba(232,184,75,0.08);border-right:2px solid #e8b84b;' : '');
            a.innerHTML =
                '<span style="font-size:1.2rem;">' + item.icon + '</span>'
                + '<span>' + item.label + '</span>';
            a.onmouseenter = function() { if (!active) this.style.background = 'rgba(232,184,75,0.06)'; };
            a.onmouseleave = function() { if (!active) this.style.background = ''; };
            nav.appendChild(a);
        });

        sidebar.appendChild(nav);

        // 底部用户信息区
        var footer = document.createElement('div');
        footer.style.cssText =
            'padding:0.8rem 1rem;border-top:1px solid rgba(232,184,75,0.08);';
        footer.innerHTML =
            '<a href="/profile.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:rgba(255,255,255,0.6);">'
            + '<div style="width:32px;height:32px;border-radius:50%;background:rgba(232,184,75,0.1);'
            + 'display:flex;align-items:center;justify-content:center;font-size:1rem;">👤</div>'
            + '<div><div id="__sideUserName" style="font-size:0.8rem;color:rgba(255,255,255,0.8);">未登录</div>'
            + '<div style="font-size:0.65rem;color:rgba(255,255,255,0.4);">点击登录</div></div></a>';
        sidebar.appendChild(footer);

        document.body.appendChild(overlay);
        document.body.appendChild(sidebar);

        updateUserName();
    }

    // ===== 展开标签（侧边栏折叠后显示） =====
    function buildExpandTab() {
        expandTab = document.createElement('div');
        expandTab.id = '__sideExpandTab';
        expandTab.style.cssText =
            'position:fixed;top:50%;left:0;z-index:9989;'
            + 'transform:translateY(-50%);'
            + 'width:24px;height:60px;border-radius:0 8px 8px 0;'
            + 'background:rgba(20,20,35,0.9);'
            + 'border:1px solid rgba(232,184,75,0.2);border-left:none;'
            + 'color:rgba(255,255,255,0.5);font-size:0.8rem;'
            + 'display:none;align-items:center;justify-content:center;'
            + 'cursor:pointer;transition:all 0.2s;'
            + 'writing-mode:vertical-rl;letter-spacing:2px;'
            + 'box-shadow:2px 0 10px rgba(0,0,0,0.2);';
        expandTab.innerHTML = '菜 单';
        expandTab.title = '展开菜单';
        expandTab.onclick = openSidebar;
        expandTab.onmouseenter = function() { this.style.color = '#e8b84b'; };
        expandTab.onmouseleave = function() { this.style.color = 'rgba(255,255,255,0.5)'; };
        document.body.appendChild(expandTab);
    }

    // ===== 更新用户名 =====
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

    // ===== 开/关 =====
    function openSidebar() {
        isOpen = true;
        sidebar.style.transform = 'translateX(0)';
        if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.pointerEvents = 'auto';
        }
        if (expandTab) expandTab.style.display = 'none';
        if (collapseBtn) { collapseBtn.innerHTML = '◀'; collapseBtn.title = '折叠菜单'; }
        updateBodyLayout();
    }

    function closeSidebar() {
        isOpen = false;
        sidebar.style.transform = 'translateX(-100%)';
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
        }
        if (expandTab) expandTab.style.display = 'flex';
        if (collapseBtn) { collapseBtn.innerHTML = '▶'; collapseBtn.title = '展开菜单'; }
        updateBodyLayout();
    }

    // ===== 根据侧边栏开关调整 body 布局 =====
    function updateBodyLayout() {
        var isDesktop = window.innerWidth >= 1024;
        if (isDesktop) {
            document.body.style.paddingLeft = isOpen ? '220px' : '';
            document.body.style.transition = 'padding-left 0.3s cubic-bezier(0.4,0,0.2,1)';
        } else {
            document.body.style.overflow = isOpen ? 'hidden' : '';
            document.body.style.paddingLeft = '';
        }
    }

    // ===== 隐藏底部导航和桌面侧边栏 =====
    function removeConflictingNavs() {
        // 隐藏原始 bottom-nav
        var navs = document.querySelectorAll('.bottom-nav');
        navs.forEach(function(nav) { nav.style.display = 'none'; });

        // 隐藏原始 desktop-sidebar（sidenav 接管）
        var ds = document.getElementById('desktopSidebar');
        if (ds) ds.style.display = 'none';
    }

    // ===== 初始化 =====
    function init() {
        buildSidebar();
        buildExpandTab();

        var isDesktop = window.innerWidth >= 1024;

        if (isDesktop) {
            // 桌面端：接管原始导航，默认展开
            removeConflictingNavs();
            openSidebar();
        } else {
            // 移动端：默认折叠，保留原始 bottom-nav
            closeSidebar();
        }

        // ESC 关闭
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isOpen && sidebar) closeSidebar();
        });

        // 窗口 resize 时更新布局
        window.addEventListener('resize', function() {
            var nowDesktop = window.innerWidth >= 1024;
            if (nowDesktop) {
                // 切换到桌面端：接管导航并展开
                removeConflictingNavs();
                if (!isOpen) openSidebar();
            } else {
                // 切换到移动端：折叠侧边栏，恢复 bottom-nav
                if (isOpen) closeSidebar();
                var navs = document.querySelectorAll('.bottom-nav');
                navs.forEach(function(nav) { nav.style.display = ''; });
            }
            updateBodyLayout();
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

    console.log('[导航] 折叠版菜单已加载');
})();
