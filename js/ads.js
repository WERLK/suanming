/**
 * 玄机算命网 - 混合广告系统 v2.0
 * 
 * 双轨策略：柠盟广告优先，无广告时自动降级为自建招租广告。
 * 通过后端 /api/ad-health 检测柠盟链接是否可用。
 * 
 * 广告位：首页 hero 下方、模块列表中间、详情页底部。
 */

var AD_CONFIG = {
    // ========== 全局开关 ==========
    // useNingmeng: true  → 优先使用柠盟（需后端验证链接可用）
    // useNingmeng: false → 始终使用自建招租广告
    useNingmeng: false,

    // 柠盟健康检查结果（由后端设置）
    _ningmengAlive: false,
    _lastCheck: 0,

    // ========== 广告位 1：首页 Hero 横幅 ==========
    heroBanner: {
        enabled: true,
        // ── 柠盟广告（CPA 直链 #1185）──
        ningmengLink: 'http://www.huyis.com/link?1185',
        ningmengText: '🌟 热门推荐 · 点击了解更多',
        // ── 自建招租广告 ──
        selfText: '🌟 广告位招租 · 精准命理流量',
        selfLink: 'mailto:support@xuanjisuanming.top?subject=首页横幅广告合作'
    },

    // ========== 广告位 2：模块列表中间 ==========
    listMiddle: {
        enabled: true,
        // ── 柠盟广告（CPA 直链 #1185 复用）──
        ningmengLink: 'http://www.huyis.com/link?1185',
        ningmengText: '📢 命理测算 · 传统文化 · 点击查看更多',
        // ── 自建招租广告 ──
        selfText: '📢 广告位招租 · 日活精准用户',
        selfLink: 'mailto:support@xuanjisuanming.top?subject=列表中间广告合作'
    },

    // ========== 广告位 3：详情页底部 ==========
    detailFooter: {
        enabled: true,
        // ── 柠盟广告（CPA 直链 #1186）──
        ningmengLink: 'http://www.huyis.com/link?1186',
        ningmengText: '🔮 精准命理流量 · 点击查看详情',
        // ── 自建招租广告 ──
        selfText: '🔮 广告位招租 · 详情页底部曝光位',
        selfLink: 'mailto:support@xuanjisuanming.top?subject=详情页广告合作'
    }
};

// ===== 健康检查 + 渲染 =====
(function() {
    'use strict';

    var CHECK_INTERVAL = 5 * 60 * 1000;  // 5 分钟检查一次

    function renderAd(config) {
        if (!config || !config.enabled) return '';

        var useNingmeng = AD_CONFIG.useNingmeng && AD_CONFIG._ningmengAlive;

        // 柠盟可用 → 柠盟链接
        if (useNingmeng && config.ningmengLink) {
            return renderTextLink(config.ningmengText || '点击查看', config.ningmengLink, true);
        }

        // 降级 → 自建招租广告
        return renderTextLink(config.selfText || '广告位招租', config.selfLink || '#', false);
    }

    function renderTextLink(text, link, isNingmeng) {
        var bgColor = isNingmeng
            ? 'rgba(255,215,0,0.06)'
            : 'rgba(255,215,0,0.03)';
        var borderColor = isNingmeng
            ? 'rgba(255,215,0,0.2)'
            : 'rgba(255,215,0,0.08)';
        var textColor = isNingmeng
            ? 'rgba(255,215,0,0.6)'
            : 'rgba(255,215,0,0.35)';

        return '<div style="text-align:center;padding:0.8rem 1rem;margin:0.8rem 0;' +
            'background:' + bgColor + ';border:1px dashed ' + borderColor + ';border-radius:10px;">' +
            '<a href="' + link + '" target="_blank" rel="noopener sponsored" ' +
            'style="color:' + textColor + ';text-decoration:none;font-size:0.82rem;' +
            'transition:color 0.2s;" ' +
            'onmouseover="this.style.color=\'rgba(255,215,0,0.85)\'" ' +
            'onmouseout="this.style.color=\'' + textColor + '\'">' +
            text + '</a></div>';
    }

    // 从后端检查柠盟健康状态（利用服务器在国内的优势）
    function checkNingmengHealth() {
        var now = Date.now();
        if (now - AD_CONFIG._lastCheck < CHECK_INTERVAL) return;

        fetch('/api/ad-health', { method: 'GET', cache: 'no-store' })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    var wasAlive = AD_CONFIG._ningmengAlive;
                    AD_CONFIG._ningmengAlive = data.alive === true;
                    AD_CONFIG._lastCheck = now;
                    // 状态变化时刷新广告
                    if (wasAlive !== AD_CONFIG._ningmengAlive) {
                        window.SiteAd && window.SiteAd.refresh();
                    }
                }
            })
            .catch(function() {
                // 检查失败，保持当前状态
                AD_CONFIG._lastCheck = now;
            });
    }

    // 页面加载后注入广告
    function injectAll() {
        var path = window.location.pathname;

        // 首页广告
        if (/^\/(index\.html)?$/.test(path)) {
            // hero 下方
            var heroArea = document.querySelector('.hero, .hero-section, .page-hero');
            if (heroArea) {
                var adHtml = renderAd(AD_CONFIG.heroBanner);
                if (adHtml) {
                    var wrap = document.createElement('div');
                    wrap.className = '__siteAd __adHero';
                    wrap.innerHTML = adHtml;
                    wrap.style.cssText = 'max-width:720px;margin:1rem auto;padding:0 1rem;';
                    heroArea.insertAdjacentElement('afterend', wrap);
                }
            }
            // 模块列表中间
            var featSection = document.querySelector('.featured-section, .quick-access');
            if (featSection) {
                var listAd = renderAd(AD_CONFIG.listMiddle);
                if (listAd) {
                    var wrap2 = document.createElement('div');
                    wrap2.className = '__siteAd __adListMiddle';
                    wrap2.innerHTML = listAd;
                    wrap2.style.cssText = 'max-width:720px;margin:0.8rem auto;padding:0 1rem;';
                    featSection.insertAdjacentElement('afterend', wrap2);
                }
            }
        }

        // 模块详情页底部广告
        if (path.indexOf('/modules/') === 0) {
            var contentArea = document.querySelector('.content-area, .page-container');
            if (contentArea) {
                var detailAd = renderAd(AD_CONFIG.detailFooter);
                if (detailAd) {
                    var wrap3 = document.createElement('div');
                    wrap3.className = '__siteAd __adDetailFooter';
                    wrap3.innerHTML = detailAd;
                    wrap3.style.cssText = 'max-width:600px;margin:1.5rem auto;padding:0 1rem;';
                    contentArea.appendChild(wrap3);
                }
            }
        }
    }

    // 延迟注入
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(injectAll, 600);
            setTimeout(checkNingmengHealth, 1000);
        });
    } else {
        setTimeout(injectAll, 600);
        setTimeout(checkNingmengHealth, 1000);
    }

    // 暴露 API
    window.SiteAd = {
        config: AD_CONFIG,
        render: renderAd,
        toggleNingmeng: function(on) {
            AD_CONFIG.useNingmeng = !!on;
            this.refresh();
        },
        refresh: function() {
            var ads = document.querySelectorAll('.__siteAd');
            for (var i = 0; i < ads.length; i++) ads[i].remove();
            injectAll();
        }
    };
})();
