/**
 * 玄机算命网 - 全站底部备案信息
 * 所有页面统一引用，修改一处全站生效
 */
(function() {
    var ICP_NUMBER = '辽ICP备2026010972号-1';
    var ICP_URL = 'https://beian.miit.gov.cn/';
    var GA_NUMBER = '';  // 公安联网备案号（审核通过后填写）
    var GA_URL = 'https://www.beian.gov.cn/';
    var VERSION = 'v1.0.0';
    var COMMIT = '1adb7b1';

    var footerHTML = '<div class="site-footer" style="text-align:center;padding:1.5rem 1rem 3rem;margin-top:2rem;border-top:1px solid rgba(255,215,0,0.08);">' +
        '<div style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin-bottom:0.3rem;">' + VERSION + ' · commit ' + COMMIT + '</div>' +
        '<div style="font-size:0.7rem;">' +
        '<a href="' + ICP_URL + '" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.3);text-decoration:none;">' + ICP_NUMBER + '</a>';

    if (GA_NUMBER) {
        footerHTML += '<span style="color:rgba(255,255,255,0.15);margin:0 0.5rem;">|</span>' +
            '<a href="' + GA_URL + '" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.3);text-decoration:none;">' + GA_NUMBER + '</a>';
    } else {
        footerHTML += '<span style="color:rgba(255,255,255,0.15);margin:0 0.5rem;">|</span>' +
            '<span style="color:rgba(255,255,255,0.15);">公安联网备案审核中</span>';
    }

    footerHTML += '</div></div>';

    // 注入到页面最底部（</body>之前）
    document.addEventListener('DOMContentLoaded', function() {
        var container = document.body;
        // 如果页面已有 site-footer，跳过（避免重复）
        if (document.querySelector('.site-footer')) return;
        var div = document.createElement('div');
        div.innerHTML = footerHTML;
        container.appendChild(div.firstElementChild);
    });
})();
