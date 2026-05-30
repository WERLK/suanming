/**
 * 玄机算命网 - 全站底部：版本号 + ICP备案 + 公安联网备案
 * 所有页面统一引用，修改一处全站生效
 * 版本号从 /version.json 动态获取
 */
(function() {
    var ICP_NUMBER = '辽ICP备2026010972号-1';
    var ICP_URL = 'https://beian.miit.gov.cn/';
    var GA_NUMBER = '';  // 公安联网备案号（审核通过后填写）
    var GA_URL = 'https://www.beian.gov.cn/';
    var FALLBACK_VERSION = 'v1.0.0';
    var FALLBACK_COMMIT = 'unknown';

    function buildFooterHTML(version, commit) {
        var html = '<div class="site-footer" style="text-align:center;padding:1.5rem 1rem 4rem;margin-top:2rem;border-top:1px solid rgba(255,215,0,0.08);">';

        // 行1：版本号 + commit
        html += '<div style="margin-bottom:0.5rem;">' +
            '<span style="display:inline-block;background:rgba(255,215,0,0.08);border-radius:4px;padding:0.15rem 0.5rem;' +
            'font-family:monospace;font-size:0.68rem;color:rgba(255,215,0,0.5);letter-spacing:0.5px;">' +
            version + ' · ' + commit +
            '</span></div>';

        // 行2：备案号
        html += '<div style="font-size:0.7rem;line-height:1.6;">' +
            '<a href="' + ICP_URL + '" target="_blank" rel="noopener" ' +
            'style="color:rgba(255,255,255,0.3);text-decoration:none;transition:color 0.2s;" ' +
            'onmouseover="this.style.color=\'rgba(255,215,0,0.6)\'" ' +
            'onmouseout="this.style.color=\'rgba(255,255,255,0.3)\'">' + ICP_NUMBER + '</a>';

        html += '<span style="color:rgba(255,255,255,0.1);margin:0 0.6rem;">|</span>';

        if (GA_NUMBER) {
            html += '<a href="' + GA_URL + '" target="_blank" rel="noopener" ' +
                'style="color:rgba(255,255,255,0.3);text-decoration:none;transition:color 0.2s;" ' +
                'onmouseover="this.style.color=\'rgba(255,215,0,0.6)\'" ' +
                'onmouseout="this.style.color=\'rgba(255,255,255,0.3)\'">' + GA_NUMBER + '</a>';
        } else {
            html += '<span style="color:rgba(255,255,255,0.12);">公安联网备案审核中</span>';
        }

        html += '</div></div>';
        return html;
    }

    function injectFooter(version, commit) {
        if (document.querySelector('.site-footer')) return;
        var container = document.body;
        if (!container) return;
        var div = document.createElement('div');
        div.innerHTML = buildFooterHTML(version, commit);
        container.appendChild(div.firstElementChild);
    }

    // 加载广告模块（如果尚未加载）
    function loadAdModule() {
        if (window.BaiduAd) return;
        if (document.querySelector('script[src*="ads.js"]')) return;
        var s = document.createElement('script');
        s.src = '/js/ads.js?v=' + encodeURIComponent(FALLBACK_VERSION);
        s.async = true;
        document.head.appendChild(s);
    }

    // 页面加载时从 version.json 获取最新版本号并注入
    document.addEventListener('DOMContentLoaded', function() {
        loadAdModule();
        fetch('/version.json?_=' + Date.now())
            .then(function(resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.json();
            })
            .then(function(data) {
                var version = data.version ? 'v' + data.version : FALLBACK_VERSION;
                var commit = data.git_commit || FALLBACK_COMMIT;
                injectFooter(version, commit);
            })
            .catch(function() {
                injectFooter(FALLBACK_VERSION, FALLBACK_COMMIT);
            });
    });
})();
