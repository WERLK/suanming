/**
 * 玄机算命网 - 百度广告联盟对接模块
 * 
 * 使用方法：
 *   1. 在百度联盟 (union.baidu.com) 注册并获取广告位 ID
 *   2. 将 slotId 填入下方 AdConfig.slotId
 *   3. 将 AdConfig.enabled 改为 true
 *   4. 部署后真广告自动替换假广告
 */

(function() {
    'use strict';

    // ==================== 广告配置 ====================
    window.AdConfig = {
        /** 总开关：注册百度联盟后改为 true */
        enabled: false,

        /** 百度联盟用户 ID（注册后获取） */
        unionId: '',

        /** 广告位 ID（百度联盟后台创建广告位后获取） */
        slotId: '',

        /** 广告类型: cpro（联名广告） */
        adType: 'cpro',

        /** 观看广告达到此秒数后激活领取按钮 */
        rewardSeconds: 5,

        /** 百度 SDK 是否已加载 */
        sdkLoaded: false,

        /** 当前是否在使用 fallback 模式 */
        fallbackMode: true
    };

    // ==================== 百度广告 SDK 加载器 ====================

    /**
     * 异步加载百度联盟 SDK (cm.js)
     * 加载成功后回调 onLoad
     */
    function loadBaiduSDK(onLoad) {
        if (AdConfig.sdkLoaded) {
            if (onLoad) onLoad();
            return;
        }

        // 检查 SDK 是否已加载
        var existing = document.querySelector('script[src*="cpro.baidustatic.com"]');
        if (existing) {
            AdConfig.sdkLoaded = true;
            if (onLoad) onLoad();
            return;
        }

        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = '//cpro.baidustatic.com/cpro/ui/cm.js';
        script.async = true;
        script.onload = function() {
            AdConfig.sdkLoaded = true;
            if (onLoad) onLoad();
        };
        script.onerror = function() {
            console.warn('[广告] 百度 SDK 加载失败，使用 fallback 模式');
            AdConfig.fallbackMode = true;
            if (onLoad) onLoad();
        };
        document.head.appendChild(script);
    }

    // ==================== 广告展示管理 ====================

    /**
     * 在指定容器中展示百度联盟广告
     * @param {string} containerId - 广告容器 DOM ID
     * @param {Function} onRendered - 广告渲染完成回调
     */
    function renderBaiduAd(containerId, onRendered) {
        if (!AdConfig.enabled || !AdConfig.slotId) {
            console.warn('[广告] 百度广告未配置，使用 fallback');
            AdConfig.fallbackMode = true;
            if (onRendered) onRendered();
            return;
        }

        var container = document.getElementById(containerId);
        if (!container) {
            if (onRendered) onRendered();
            return;
        }

        // 清空旧内容
        container.innerHTML = '';

        // 创建广告容器
        var adDiv = document.createElement('div');
        adDiv.id = containerId + '_inner';
        adDiv.style.cssText = 'width:100%;min-height:250px;display:flex;align-items:center;justify-content:center;';
        container.appendChild(adDiv);

        // 推送广告位配置
        window.slotbydup = window.slotbydup || [];
        window.slotbydup.push({
            id: AdConfig.slotId,
            container: adDiv.id,
            display: 'inlay-fix',
            async: true
        });

        // 加载 SDK 并触发渲染
        loadBaiduSDK(function() {
            // 给 SDK 一点时间渲染
            setTimeout(function() {
                if (onRendered) onRendered();
            }, 300);
        });
    }

    /**
     * 销毁广告容器内容
     */
    function destroyAd(containerId) {
        var container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }

    // ==================== 公共 API ====================

    window.BaiduAd = {
        /** 广告配置 */
        config: AdConfig,

        /** 加载 SDK */
        loadSDK: loadBaiduSDK,

        /** 展示广告 */
        show: renderBaiduAd,

        /** 销毁广告 */
        destroy: destroyAd,

        /**
         * 检查是否应使用真广告
         */
        isReady: function() {
            return AdConfig.enabled && !!AdConfig.slotId;
        },

        /**
         * 获取配置的观看秒数
         */
        getRewardSeconds: function() {
            return AdConfig.rewardSeconds || 5;
        }
    };

    console.log('[广告] 广告模块已加载 | 百度广告:', AdConfig.enabled ? '已启用' : '未启用（fallback模式）');
})();
