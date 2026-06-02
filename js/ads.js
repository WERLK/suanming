/**
 * 玄机算命网 - 多平台广告系统 v3.0
 * 
 * 支持多个广告联盟，按优先级自动切换。
 * 每个广告位可配置多个平台，系统按顺序尝试。
 * 
 * 已对接平台：
 *   A. 柠盟 (ning.net) — CPA 直链，已注册，目前无库存
 *   B. 汇成联盟 (hczzw.com) — CPA/CPS 日付，待注册
 *   C. 觅媒汇 (mimeihui.com) — CPA 老牌，50元日付，待注册
 *   D. 逗号联盟 (union.douhao.com) — CPA 日付无门槛，待注册
 * 
 * 配置方式：将你的广告代码填入下方对应平台即可。
 */

var AD_CONFIG = {
    // ========== 全局设置 ==========
    // 平台优先级（数字越小越优先）
    platformOrder: ['ningmeng', 'huicheng', 'mimeihui', 'douhao'],

    // 当前活跃平台（系统自动检测后设置）
    _activePlatform: 'self',

    // 平台健康状态（由 /api/ad-health 批量检测）
    _platformHealth: {},

    // ========== 广告位配置 ==========
    slots: {
        // 广告位 1：首页 Hero 横幅
        heroBanner: {
            enabled: true,
            selector: '.hero, .hero-section, .page-hero',
            insertMode: 'afterend',  // afterend | append
            wrapperStyle: 'max-width:720px;margin:1rem auto;padding:0 1rem;',
            providers: {
                // ── 柠盟 #1185 ──
                ningmeng: {
                    type: 'link',
                    url: 'http://www.huyis.com/link?1185',
                    text: '🌟 热门推荐 · 点击了解更多'
                },
                // ── 汇成联盟 ──
                // 注册 https://www.hczzw.com 后，在"获取代码"中拿到推广链接填入下方 url
                huicheng: {
                    type: 'link',
                    url: 'https://www.hczzw.com/',  // ← 替换为你的汇成推广链接
                    text: '🌟 热门推荐 · 点击了解更多'
                },
                // ── 觅媒汇 ──
                // 注册 https://www.mimeihui.com 后，拿到广告代码
                mimeihui: {
                    type: 'link',
                    url: 'https://www.mimeihui.com/',  // ← 替换为你的觅媒汇推广链接
                    text: '🌟 热门推荐 · 点击了解更多'
                },
                // ── 逗号联盟 ──
                douhao: {
                    type: 'link',
                    url: 'https://union.douhao.com/',  // ← 替换为你的逗号联盟推广链接
                    text: '🌟 热门推荐 · 点击了解更多'
                }
            },
            // 自建降级广告
            fallback: {
                text: '🌟 广告位招租 · 精准命理流量',
                link: 'mailto:support@xuanjisuanming.top?subject=首页横幅广告合作'
            }
        },

        // 广告位 2：模块列表中间
        listMiddle: {
            enabled: true,
            selector: '.featured-section, .quick-access',
            insertMode: 'afterend',
            wrapperStyle: 'max-width:720px;margin:0.8rem auto;padding:0 1rem;',
            providers: {
                ningmeng: {
                    type: 'link',
                    url: 'http://www.huyis.com/link?1185',
                    text: '📢 命理测算 · 传统文化 · 点击查看更多'
                },
                huicheng: {
                    type: 'link',
                    url: 'https://www.hczzw.com/',  // ← 替换
                    text: '📢 命理测算 · 传统文化 · 点击查看更多'
                },
                mimeihui: {
                    type: 'link',
                    url: 'https://www.mimeihui.com/',  // ← 替换
                    text: '📢 命理测算 · 传统文化 · 点击查看更多'
                },
                douhao: {
                    type: 'link',
                    url: 'https://union.douhao.com/',  // ← 替换
                    text: '📢 命理测算 · 传统文化 · 点击查看更多'
                }
            },
            fallback: {
                text: '📢 广告位招租 · 日活精准用户',
                link: 'mailto:support@xuanjisuanming.top?subject=列表中间广告合作'
            }
        },

        // 广告位 3：详情页底部
        detailFooter: {
            enabled: true,
            selector: '.content-area, .page-container',
            insertMode: 'append',
            wrapperStyle: 'max-width:600px;margin:1.5rem auto;padding:0 1rem;',
            providers: {
                ningmeng: {
                    type: 'link',
                    url: 'http://www.huyis.com/link?1186',
                    text: '🔮 精准命理流量 · 点击查看详情'
                },
                huicheng: {
                    type: 'link',
                    url: 'https://www.hczzw.com/',  // ← 替换
                    text: '🔮 精准命理流量 · 点击查看详情'
                },
                mimeihui: {
                    type: 'link',
                    url: 'https://www.mimeihui.com/',  // ← 替换
                    text: '🔮 精准命理流量 · 点击查看详情'
                },
                douhao: {
                    type: 'link',
                    url: 'https://union.douhao.com/',  // ← 替换
                    text: '🔮 精准命理流量 · 点击查看详情'
                }
            },
            fallback: {
                text: '🔮 广告位招租 · 详情页底部曝光位',
                link: 'mailto:support@xuanjisuanming.top?subject=详情页广告合作'
            }
        }
    }
};

// ===== 多平台广告引擎 =====
(function() {
    'use strict';

    var CHECK_INTERVAL = 5 * 60 * 1000;  // 5 分钟检查一次

    // 选择一个可用的平台
    function pickProvider(slotConfig) {
        var order = AD_CONFIG.platformOrder;
        for (var i = 0; i < order.length; i++) {
            var pid = order[i];
            if (AD_CONFIG._platformHealth[pid] && slotConfig.providers[pid]) {
                return slotConfig.providers[pid];
            }
        }
        return null;
    }

    // 渲染广告 HTML
    function renderAd(slotConfig) {
        if (!slotConfig || !slotConfig.enabled) return '';

        var provider = pickProvider(slotConfig);

        if (provider) {
            return renderProviderAd(provider);
        }

        // 降级到自建招租广告
        return renderFallbackAd(slotConfig.fallback);
    }

    function renderProviderAd(provider) {
        if (provider.type === 'code') {
            // JavaScript/iframe 嵌入代码
            return provider.code || '';
        }
        // 文字链接（默认）
        return '<div style="text-align:center;padding:0.8rem 1rem;margin:0.8rem 0;' +
            'background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.2);border-radius:10px;">' +
            '<a href="' + (provider.url || '#') + '" target="_blank" rel="noopener sponsored" ' +
            'style="color:rgba(255,215,0,0.6);text-decoration:none;font-size:0.82rem;' +
            'transition:color 0.2s;" ' +
            'onmouseover="this.style.color=\'rgba(255,215,0,0.85)\'" ' +
            'onmouseout="this.style.color=\'rgba(255,215,0,0.6)\'">' +
            (provider.text || '点击查看') + '</a></div>';
    }

    function renderFallbackAd(fb) {
        if (!fb) return '';
        return '<div style="text-align:center;padding:0.8rem 1rem;margin:0.8rem 0;' +
            'background:rgba(255,215,0,0.02);border:1px dashed rgba(255,215,0,0.06);border-radius:10px;">' +
            '<a href="' + (fb.link || '#') + '" target="_blank" rel="noopener" ' +
            'style="color:rgba(255,215,0,0.3);text-decoration:none;font-size:0.78rem;' +
            'transition:color 0.2s;" ' +
            'onmouseover="this.style.color=\'rgba(255,215,0,0.6)\'" ' +
            'onmouseout="this.style.color=\'rgba(255,215,0,0.3)\'">' +
            (fb.text || '广告位招租') + '</a></div>';
    }

    // 向后端请求平台健康状态
    function checkPlatformHealth() {
        var now = Date.now();
        if (now - (AD_CONFIG._lastCheck || 0) < CHECK_INTERVAL) return;

        fetch('/api/ad-health', { method: 'GET', cache: 'no-store' })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    var changed = false;
                    var health = data.platforms || {};
                    for (var pid in health) {
                        if (AD_CONFIG._platformHealth[pid] !== health[pid]) {
                            changed = true;
                        }
                        AD_CONFIG._platformHealth[pid] = health[pid];
                    }
                    AD_CONFIG._lastCheck = now;
                    if (changed) {
                        window.SiteAd && window.SiteAd.refresh();
                    }
                }
            })
            .catch(function() {
                AD_CONFIG._lastCheck = now;
            });
    }

    // 注入所有广告位
    function injectAll() {
        var slots = AD_CONFIG.slots;
        var path = window.location.pathname;
        var isHome = /^\/(index\.html)?$/.test(path);
        var isModule = path.indexOf('/modules/') === 0;

        // 首页广告位
        if (isHome) {
            injectSlot(slots.heroBanner, '__adHero');
            injectSlot(slots.listMiddle, '__adListMiddle');
        }

        // 详情页广告位
        if (isModule) {
            injectSlot(slots.detailFooter, '__adDetailFooter');
        }
    }

    function injectSlot(slotConfig, className) {
        if (!slotConfig || !slotConfig.enabled) return;

        var container = document.querySelector(slotConfig.selector);
        if (!container) return;

        var adHtml = renderAd(slotConfig);
        if (!adHtml) return;

        var wrap = document.createElement('div');
        wrap.className = '__siteAd ' + (className || '');
        wrap.innerHTML = adHtml;
        if (slotConfig.wrapperStyle) {
            wrap.style.cssText = slotConfig.wrapperStyle;
        }

        if (slotConfig.insertMode === 'append') {
            container.appendChild(wrap);
        } else {
            container.insertAdjacentElement('afterend', wrap);
        }
    }

    // 页面加载
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(injectAll, 500);
            setTimeout(checkPlatformHealth, 1000);
        });
    } else {
        setTimeout(injectAll, 500);
        setTimeout(checkPlatformHealth, 1000);
    }

    // 公开 API
    window.SiteAd = {
        config: AD_CONFIG,
        refresh: function() {
            var ads = document.querySelectorAll('.__siteAd');
            for (var i = 0; i < ads.length; i++) ads[i].remove();
            injectAll();
        },
        // 手动设置活跃平台
        setPlatform: function(platformId) {
            AD_CONFIG._platformHealth[platformId] = true;
            this.refresh();
        },
        // 获取当前使用的平台
        getActivePlatform: function() {
            return pickProvider(AD_CONFIG.slots.heroBanner);
        }
    };
})();
