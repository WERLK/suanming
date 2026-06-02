/**
 * 玄机算命网 - 自建广告管理系统
 * 
 * 设计理念：不依赖任何第三方广告联盟审核。
 * 支持三种广告类型：
 *   1. 嵌入代码（AdSense / 任何联盟的 JS 代码）
 *   2. 图片广告（直接放图片+链接，适合自营/直投）
 *   3. 文字链接广告
 * 
 * 配置方式：修改下方 AD_CONFIG 对象即可，无需改 HTML。
 * 广告位：首页 hero 下方、模块列表中间、详情页底部。
 */

var AD_CONFIG = {
    // ========== 广告位 1：首页 Hero 横幅（大尺寸） ==========
    heroBanner: {
        enabled: true,
        type: 'image',        // 'image' | 'code' | 'text'
        // 图片模式
        imageUrl: '',
        imageLink: '',
        imageAlt: '广告合作：support@xuanjisuanming.top',
        // 代码模式（粘贴 AdSense 或其他联盟的代码）
        codeHtml: '',
        // 文字模式
        textContent: '🌟 广告位招租 — 联系 support@xuanjisuanming.top',
        textLink: 'mailto:support@xuanjisuanming.top'
    },

    // ========== 广告位 2：模块列表中间（中等尺寸） ==========
    listMiddle: {
        enabled: true,
        type: 'text',
        imageUrl: '',
        imageLink: '',
        imageAlt: '广告合作',
        codeHtml: '',
        textContent: '📢 此处广告位出租 · 精准命理流量 · 日UV 1000+',
        textLink: 'mailto:support@xuanjisuanming.top'
    },

    // ========== 广告位 3：详情页底部（小尺寸） ==========
    detailFooter: {
        enabled: true,
        type: 'text',
        imageUrl: '',
        imageLink: '',
        imageAlt: '广告合作',
        codeHtml: '',
        textContent: '🔮 精准命理流量 · 广告合作：support@xuanjisuanming.top',
        textLink: 'mailto:support@xuanjisuanming.top'
    }
};

// ===== 渲染广告 =====
(function() {
    'use strict';

    function renderAd(config) {
        if (!config || !config.enabled) return '';

        switch (config.type) {
            case 'image':
                if (!config.imageUrl) return renderTextAd(config);
                var imgHtml = '<a href="' + (config.imageLink || '#') + '" target="_blank" rel="noopener sponsored" ' +
                    'style="display:block;text-align:center;">' +
                    '<img src="' + config.imageUrl + '" alt="' + (config.imageAlt || '广告') + '" ' +
                    'style="max-width:100%;height:auto;border-radius:8px;" ' +
                    'onerror="this.parentElement.style.display=\'none\'">' +
                    '</a>';
                return imgHtml;

            case 'code':
                if (!config.codeHtml) return renderTextAd(config);
                return config.codeHtml;

            case 'text':
            default:
                return renderTextAd(config);
        }
    }

    function renderTextAd(config) {
        var content = config.textContent || '广告位招租';
        var link = config.textLink || '#';
        return '<div style="text-align:center;padding:0.8rem 1rem;margin:0.8rem 0;' +
            'background:rgba(255,215,0,0.04);border:1px dashed rgba(255,215,0,0.15);border-radius:10px;">' +
            '<a href="' + link + '" target="_blank" rel="noopener sponsored" ' +
            'style="color:rgba(255,215,0,0.55);text-decoration:none;font-size:0.82rem;' +
            'transition:color 0.2s;" ' +
            'onmouseover="this.style.color=\'rgba(255,215,0,0.85)\'" ' +
            'onmouseout="this.style.color=\'rgba(255,215,0,0.55)\'">' +
            content + '</a></div>';
    }

    function injectAd(selector, config) {
        var container = document.querySelector(selector);
        if (!container) return;
        var adHtml = renderAd(config);
        if (!adHtml) return;

        var adWrap = document.createElement('div');
        adWrap.className = '__siteAd';
        adWrap.style.cssText = 'margin:0.5rem 0;';
        adWrap.innerHTML = adHtml;
        container.appendChild(adWrap);
    }

    // 页面加载后注入广告
    function injectAll() {
        var path = window.location.pathname;

        // 首页 hero 广告
        if (/^\/(index\.html)?$/.test(path)) {
            // hero 区域后
            var heroArea = document.querySelector('.hero, .hero-section, .page-hero');
            if (heroArea) {
                injectAd.__target = heroArea;
                var adHtml = renderAd(AD_CONFIG.heroBanner);
                if (adHtml) {
                    var wrap = document.createElement('div');
                    wrap.className = '__siteAd __adHero';
                    wrap.innerHTML = adHtml;
                    wrap.style.cssText = 'max-width:720px;margin:1rem auto;padding:0 1rem;';
                    heroArea.insertAdjacentElement('afterend', wrap);
                }
            }

            // 模块列表中间广告
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

    // 延迟注入（等页面渲染完）
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(injectAll, 800);
        });
    } else {
        setTimeout(injectAll, 800);
    }

    // 暴露 API 供外部使用
    window.SiteAd = {
        config: AD_CONFIG,
        render: renderAd,
        updateConfig: function(newConfig) {
            Object.assign(AD_CONFIG, newConfig);
        },
        refresh: function() {
            // 移除已有广告
            var ads = document.querySelectorAll('.__siteAd');
            for (var i = 0; i < ads.length; i++) ads[i].remove();
            injectAll();
        }
    };
})();
