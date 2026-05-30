/**
 * 玄机算命网 - 广告模块 v2
 * 
 * 底部小横幅广告 + 百度联盟对接预留
 * 设计原则：不弹窗、不遮挡内容、手机友好
 */
(function() {
    'use strict';

    // ==================== 广告配置 ====================
    window.AdConfig = {
        enabled: false,           // 百度联盟验证通过后改为 true
        unionId: '',              // 百度联盟用户 ID
        slotId: '',               // 广告位 ID
        adType: 'cpro',
        rewardSeconds: 15,        // 观看秒数
        sdkLoaded: false,
        fallbackMode: true
    };

    // ==================== 百度 SDK ====================
    function loadBaiduSDK(onLoad) {
        if (AdConfig.sdkLoaded) { if (onLoad) onLoad(); return; }
        var existing = document.querySelector('script[src*="cpro.baidustatic.com"]');
        if (existing) { AdConfig.sdkLoaded = true; if (onLoad) onLoad(); return; }
        var script = document.createElement('script');
        script.src = '//cpro.baidustatic.com/cpro/ui/cm.js';
        script.async = true;
        script.onload = function() { AdConfig.sdkLoaded = true; if (onLoad) onLoad(); };
        script.onerror = function() { AdConfig.fallbackMode = true; if (onLoad) onLoad(); };
        document.head.appendChild(script);
    }

    function renderBaiduAd(containerId, onRendered) {
        if (!AdConfig.enabled || !AdConfig.slotId) {
            AdConfig.fallbackMode = true;
            if (onRendered) onRendered();
            return;
        }
        var container = document.getElementById(containerId);
        if (!container) { if (onRendered) onRendered(); return; }
        container.innerHTML = '';
        var adDiv = document.createElement('div');
        adDiv.id = containerId + '_inner';
        adDiv.style.cssText = 'width:100%;height:100%;display:flex;align-items:center;justify-content:center;';
        container.appendChild(adDiv);
        window.slotbydup = window.slotbydup || [];
        window.slotbydup.push({ id: AdConfig.slotId, container: adDiv.id, display: 'inlay-fix', async: true });
        loadBaiduSDK(function() { setTimeout(function() { if (onRendered) onRendered(); }, 300); });
    }

    function destroyAd(containerId) {
        var c = document.getElementById(containerId);
        if (c) c.innerHTML = '';
    }

    window.BaiduAd = {
        config: AdConfig,
        loadSDK: loadBaiduSDK,
        show: renderBaiduAd,
        destroy: destroyAd,
        isReady: function() { return AdConfig.enabled && !!AdConfig.slotId; },
        getRewardSeconds: function() { return AdConfig.rewardSeconds || 15; }
    };

    // ==================== 底部广告横幅 ====================
    var adBar = null;
    var adTimer = null;
    var adSeconds = 0;
    var adTarget = 15;
    var adWatching = false;
    var adBarHidden = false;
    var lastScrollY = 0;
    var scrollTicking = false;

    // 检测是否为个人中心页面（已有 VIP 卡片，横幅位置需预留）
    function isProfilePage() {
        return window.location.pathname.indexOf('profile') !== -1;
    }

    function buildAdBarHTML() {
        var bar = document.createElement('div');
        bar.id = '__adbar';
        bar.innerHTML =
            '<div class="adbar-inner" style="'
            + 'display:flex;align-items:center;justify-content:space-between;'
            + 'height:40px;padding:0 10px;'
            + 'background:rgba(20,20,30,0.95);'
            + 'border-top:1px solid rgba(255,215,0,0.15);'
            + 'color:rgba(255,255,255,0.85);font-size:0.78rem;'
            + 'cursor:default;user-select:none;'
            + '">'
            + '<span class="adbar-label" style="display:flex;align-items:center;gap:6px;flex:1;min-width:0;overflow:hidden;">'
            + '<span class="adbar-icon">📺</span>'
            + '<span class="adbar-text">看广告赚VIP时长</span>'
            + '</span>'
            + '<div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">'
            + '<div class="adbar-ad-slot" id="adbarSlot" style="display:none;width:120px;height:32px;background:rgba(255,215,0,0.06);border-radius:4px;overflow:hidden;"></div>'
            + '<button class="adbar-watch-btn" id="adbarWatchBtn" style="'
            + 'background:rgba(255,215,0,0.15);color:#ffd700;border:1px solid rgba(255,215,0,0.3);'
            + 'border-radius:14px;padding:3px 12px;font-size:0.72rem;cursor:pointer;'
            + 'white-space:nowrap;transition:all 0.2s;'
            + '">▶ 观看</button>'
            + '<button class="adbar-close-btn" id="adbarCloseBtn" style="'
            + 'background:none;border:none;color:rgba(255,255,255,0.25);font-size:1rem;cursor:pointer;'
            + 'padding:0 2px;line-height:1;'
            + '" title="关闭">✕</button>'
            + '</div>'
            + '</div>';

        // 状态栏
        var statusBar = document.createElement('div');
        statusBar.id = '__adbarStatus';
        statusBar.style.cssText =
            'display:none;height:0;overflow:hidden;text-align:center;font-size:0.7rem;'
            + 'color:rgba(255,215,0,0.6);background:rgba(20,20,30,0.95);'
            + 'transition:height 0.25s ease;';
        bar.appendChild(statusBar);

        return bar;
    }

    function getAdBar() {
        if (!adBar) adBar = document.getElementById('__adbar');
        return adBar;
    }

    function showStatus(msg) {
        var s = document.getElementById('__adbarStatus');
        if (!s) return;
        s.textContent = msg;
        s.style.display = 'block';
        s.style.height = '22px';
        s.style.padding = '2px 0';
    }

    function hideStatus() {
        var s = document.getElementById('__adbarStatus');
        if (!s) return;
        s.style.height = '0';
        s.style.padding = '0';
        setTimeout(function() { s.style.display = 'none'; }, 260);
    }

    // ===== 观看逻辑 =====
    function startWatching() {
        if (adWatching) return;

        var token = getAuthToken();
        if (!token) {
            window.location.href = '/login.html';
            return;
        }

        adWatching = true;
        adSeconds = 0;
        adTarget = BaiduAd.getRewardSeconds();

        var btn = document.getElementById('adbarWatchBtn');
        var label = document.querySelector('.adbar-text');
        var slot = document.getElementById('adbarSlot');

        // 显示广告位（未来放真实广告）
        if (slot) {
            slot.style.display = 'block';
            if (BaiduAd.isReady()) {
                BaiduAd.show('adbarSlot', function() {});
            } else {
                slot.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;'
                    + 'color:rgba(255,215,0,0.3);font-size:0.6rem;">广告位</div>';
            }
        }

        // 更新按钮状态
        btn.textContent = '⏱ ' + adTarget + 's';
        btn.style.background = 'rgba(255,215,0,0.25)';
        btn.style.cursor = 'default';
        btn.disabled = true;
        if (label) label.textContent = '广告播放中…';

        // 倒计时
        adTimer = setInterval(function() {
            adSeconds++;
            var remain = adTarget - adSeconds;
            btn.textContent = '⏱ ' + remain + 's';

            if (adSeconds >= adTarget) {
                clearInterval(adTimer);
                adTimer = null;
                btn.textContent = '🎁 领取';
                btn.style.background = 'rgba(255,215,0,0.5)';
                btn.style.borderColor = 'rgba(255,215,0,0.7)';
                btn.style.cursor = 'pointer';
                btn.disabled = false;
                if (label) label.textContent = '观看完成，领取奖励';
                showStatus('✅ 观看完成！点击"领取"获取VIP时长');
                // 重新绑定点击为领取
                btn.onclick = claimReward;
            }
        }, 1000);
    }

    function claimReward() {
        var btn = document.getElementById('adbarWatchBtn');
        btn.disabled = true;
        btn.textContent = '...';
        btn.onclick = null;

        var token = getAuthToken();
        if (!token) { resetAdBar(); return; }

        fetch('/api/vip/watch-ad', {
            method: 'POST',
            headers: { 'Authorization': 'Bearer ' + token }
        }).then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                showStatus('✅ ' + data.message);
                setTimeout(function() {
                    hideStatus();
                    resetAdBar();
                }, 2500);
            } else {
                showStatus('⚠️ ' + data.message);
                setTimeout(function() {
                    hideStatus();
                    resetAdBar();
                }, 2000);
            }
        }).catch(function() {
            hideStatus();
            resetAdBar();
        });
    }

    function resetAdBar() {
        adWatching = false;
        if (adTimer) { clearInterval(adTimer); adTimer = null; }
        adSeconds = 0;

        var btn = document.getElementById('adbarWatchBtn');
        var label = document.querySelector('.adbar-text');
        var slot = document.getElementById('adbarSlot');

        if (slot) { slot.style.display = 'none'; BaiduAd.destroy('adbarSlot'); }
        if (btn) {
            btn.textContent = '▶ 观看';
            btn.style.background = 'rgba(255,215,0,0.15)';
            btn.style.borderColor = 'rgba(255,215,0,0.3)';
            btn.style.cursor = 'pointer';
            btn.disabled = false;
            btn.onclick = startWatching;
        }
        if (label) label.textContent = '看广告赚VIP时长';
    }

    function closeAdBar() {
        adBarHidden = true;
        var bar = getAdBar();
        if (bar) {
            bar.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            bar.style.transform = 'translateY(100%)';
            bar.style.opacity = '0';
        }
        // 3 分钟后重新显示
        setTimeout(function() {
            adBarHidden = false;
            var b = getAdBar();
            if (b) {
                b.style.transform = 'translateY(0)';
                b.style.opacity = '1';
            }
        }, 180000);
    }

    // ===== 滚动控制（向下滚动隐藏，向上滚动显示） =====
    function handleScroll() {
        if (adBarHidden) return;
        if (!scrollTicking) {
            requestAnimationFrame(function() {
                var bar = getAdBar();
                if (!bar) { scrollTicking = false; return; }
                var currentY = window.pageYOffset;
                var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
                var nearBottom = (maxScroll - currentY) < 120;

                if (currentY > lastScrollY + 10 && currentY > 100) {
                    bar.style.transform = 'translateY(100%)';
                } else if (currentY < lastScrollY - 10 || nearBottom) {
                    bar.style.transform = 'translateY(0)';
                }
                lastScrollY = currentY;
                scrollTicking = false;
            });
            scrollTicking = true;
        }
    }

    // ===== 获取 token =====
    function getAuthToken() {
        // 兼容 Auth 模块（auth.js）
        if (window.Auth && typeof window.Auth.getToken === 'function') {
            return window.Auth.getToken();
        }
        // fallback: 从 cookie 读取
        var match = document.cookie.match(/(?:^|;\s*)token=([^;]+)/);
        return match ? match[1] : null;
    }

    // ===== 注入横幅 =====
    function injectAdBar() {
        if (document.getElementById('__adbar')) return;

        var bar = buildAdBarHTML();

        // 样式
        var style = document.createElement('style');
        style.textContent =
            '#__adbar{position:fixed;bottom:0;left:0;right:0;z-index:9998;'
            + 'transition:transform 0.3s ease,opacity 0.3s ease;'
            + 'padding-bottom:env(safe-area-inset-bottom,0);'
            + '}'
            + '#__adbar .adbar-watch-btn:hover{background:rgba(255,215,0,0.3)!important;}'
            + '#__adbar .adbar-close-btn:hover{color:rgba(255,255,255,0.6)!important;}';
        document.head.appendChild(style);

        document.body.appendChild(bar);

        // 绑定事件
        var watchBtn = document.getElementById('adbarWatchBtn');
        var closeBtn = document.getElementById('adbarCloseBtn');
        if (watchBtn) watchBtn.onclick = startWatching;
        if (closeBtn) closeBtn.onclick = closeAdBar;

        // 滚动监听
        window.addEventListener('scroll', handleScroll, { passive: true });

        // 登录成功后自动显示（监听 storage 变化）
        window.addEventListener('storage', function(e) {
            if (e.key === 'token' && e.newValue) {
                adBarHidden = false;
                var b = getAdBar();
                if (b) { b.style.transform = 'translateY(0)'; b.style.opacity = '1'; }
            }
        });
    }

    // ===== 初始化 =====
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(injectAdBar, 300);
        });
    } else {
        setTimeout(injectAdBar, 300);
    }

    console.log('[广告] 底部横幅模块已加载 | 百度广告:', AdConfig.enabled ? '已启用' : '未启用（fallback）');
})();
