/**
 * 玄机算命网 - 全站底部备案信息 + 版本号
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
        var html = '<div class="site-footer" style="text-align:center;padding:1.5rem 1rem 3rem;margin-top:2rem;border-top:1px solid rgba(255,215,0,0.08);">' +
            '<div style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin-bottom:0.3rem;">' + version + ' · commit ' + commit + '</div>' +
            '<div style="font-size:0.7rem;">' +
            '<a href="' + ICP_URL + '" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.3);text-decoration:none;">' + ICP_NUMBER + '</a>';

        if (GA_NUMBER) {
            html += '<span style="color:rgba(255,255,255,0.15);margin:0 0.5rem;">|</span>' +
                '<a href="' + GA_URL + '" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.3);text-decoration:none;">' + GA_NUMBER + '</a>';
        } else {
            html += '<span style="color:rgba(255,255,255,0.15);margin:0 0.5rem;">|</span>' +
                '<span style="color:rgba(255,255,255,0.15);">公安联网备案审核中</span>';
        }

        html += '</div></div>';
        return html;
    }

    function injectFooter(version, commit) {
        // 如果页面已有 site-footer，跳过（避免重复）
        if (document.querySelector('.site-footer')) return;
        var container = document.body;
        if (!container) return;
        var div = document.createElement('div');
        div.innerHTML = buildFooterHTML(version, commit);
        container.appendChild(div.firstElementChild);
    }

    // 页面加载时从 version.json 获取最新版本号并注入
    document.addEventListener('DOMContentLoaded', function() {
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
                // 获取失败时使用回退版本号
                injectFooter(FALLBACK_VERSION, FALLBACK_COMMIT);
            });
    });
})();
