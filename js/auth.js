/**
 * 玄机算命网 - 统一认证模块
 * 所有登录/注册/忘记密码页面共用此模块
 * 
 * 修复记录：
 * - 统一 token 存储策略（remember → localStorage，否则 → sessionStorage）
 * - 注册后也遵循 remember 逻辑
 * - 添加跨标签页/跨窗口登录状态同步（storage 事件 + 自定义事件）
 * - 登出时同步清除所有端状态
 */
window.Auth = (function() {
    'use strict';

    var API_BASE = '';
    var REMEMBER_KEY = 'rememberMe';

    // ========== 工具函数 ==========

    function isRemember() {
        return localStorage.getItem(REMEMBER_KEY) === 'true';
    }

    function setRemember(val) {
        if (val) {
            localStorage.setItem(REMEMBER_KEY, 'true');
        } else {
            localStorage.removeItem(REMEMBER_KEY);
        }
    }

    function getStorage() {
        return isRemember() ? localStorage : sessionStorage;
    }

    function getToken() {
        var token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (!token) return null;
        // 快速过期检查：解析 JWT payload 中的 exp（不验证签名，仅做前端预检）
        try {
            var payload = JSON.parse(atob(token.split('.')[1]));
            if (payload.exp && payload.exp * 1000 < Date.now()) {
                // token 已过期，清理并返回 null
                clearToken();
                return null;
            }
        } catch (e) { /* 解析失败，让后端验证 */ }
        return token;
    }

    function setToken(token, remember) {
        // 先清除所有位置的旧 token，避免残留
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('currentUser');

        if (remember) {
            localStorage.setItem('token', token);
            setRemember(true);
        } else {
            sessionStorage.setItem('token', token);
            setRemember(false);
        }
    }

    function clearToken() {
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('currentUser');
        localStorage.removeItem(REMEMBER_KEY);
    }

    /**
     * 同步登录状态到另一个存储（仅在需要跨存储同步时调用）
     * 警告：不应在登录/注册后无条件调用，会破坏 remember 语义
     */
    function syncTokenToBoth() {
        var token = localStorage.getItem('token') || sessionStorage.getItem('token');
        var user = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
        if (token) {
            localStorage.setItem('token', token);
            sessionStorage.setItem('token', token);
            if (user) {
                localStorage.setItem('currentUser', user);
                sessionStorage.setItem('currentUser', user);
            }
        }
    }

    async function request(url, options) {
        var token = getToken();
        var headers = options.headers || {};
        headers['Content-Type'] = 'application/json';
        if (token) headers['Authorization'] = 'Bearer ' + token;
        var resp = await fetch(API_BASE + url, {
            method: options.method || 'GET',
            headers: headers,
            body: options.body ? JSON.stringify(options.body) : undefined
        });
        var data;
        try { data = await resp.json(); } catch (e) { data = {}; }
        return data;
    }

    // ========== 认证状态检查 ==========

    async function checkAuth() {
        var token = getToken();
        if (!token) return { loggedIn: false };

        try {
            var data = await request('/api/profile');
            if (data.success) {
                return { loggedIn: true, user: data.user };
            }
        } catch (e) {}

        clearToken();
        return { loggedIn: false };
    }

    function requireAuth() {
        var token = getToken();
        if (!token) {
            window.location.replace('/login.html');
            return false;
        }
        return true;
    }

    function redirectIfLoggedIn() {
        var token = getToken();
        if (token) {
            window.location.replace('/');
            return true;
        }
        return false;
    }

    /**
     * 处理 API 返回的 401 未授权响应
     * 清除过期 token 并跳转登录页
     * @returns {boolean} 是否触发了跳转
     */
    function handleAuthError() {
        clearToken();
        window.location.replace('/login.html');
        return true;
    }

    /**
     * 快速验证 token 是否有效（异步调用 /api/vip/status 轻量验证）
     * 用于在关键操作前确认登录状态
     */
    async function verifyToken() {
        var token = getToken();
        if (!token) return false;
        try {
            var resp = await fetch(API_BASE + '/api/vip/status', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            return resp.status === 200;
        } catch (e) {
            return false;
        }
    }

    // ========== 登录/注册/登出 ==========

    async function login(username, password, remember) {
        var data = await request('/api/login', {
            method: 'POST',
            body: { username: username, password: password, remember: !!remember }
        });
        if (data.success) {
            setToken(data.token, !!remember);
            if (data.user) {
                var storage = getStorage();
                storage.setItem('currentUser', JSON.stringify(data.user));
            }
            // 通知其他标签页
            _broadcastAuthChange('login');
        }
        return { success: data.success, message: data.message || (data.success ? '' : '登录失败') };
    }

    async function register(username, password, email, phone) {
        var data = await request('/api/register', {
            method: 'POST',
            body: { username: username, password: password, email: email || '', phone: phone || '' }
        });
        if (data.success && data.token) {
            // 注册后默认"记住我"，写入 localStorage
            localStorage.setItem('token', data.token);
            setRemember(true);
            if (data.user) {
                localStorage.setItem('currentUser', JSON.stringify(data.user));
            }
            // 同步到双存储
            syncTokenToBoth();
            // 通知其他标签页
            _broadcastAuthChange('login');
        }
        return { success: data.success, message: data.message || (data.success ? '' : '注册失败') };
    }

    async function logout() {
        try {
            await request('/api/logout', { method: 'POST' });
        } catch (e) {}
        clearToken();
        // 通知其他标签页
        _broadcastAuthChange('logout');
    }

    async function forgotPassword(email) {
        return await request('/api/forgot-password', {
            method: 'POST',
            body: { email: email }
        });
    }

    async function resetPassword(token, newPassword) {
        return await request('/api/reset-password', {
            method: 'POST',
            body: { token: token, password: newPassword }
        });
    }

    // ========== 验证码 ==========

    async function generateCaptcha() {
        return await request('/api/captcha/generate');
    }

    async function verifyCaptcha(captchaId, captchaText) {
        return await request('/api/captcha/verify', {
            method: 'POST',
            body: { captcha_id: captchaId, captcha_text: captchaText }
        });
    }

    async function generateSlider() {
        return await request('/api/slider/generate');
    }

    async function verifySlider(sliderId, sliderX) {
        return await request('/api/slider/verify', {
            method: 'POST',
            body: { slider_id: sliderId, slider_x: sliderX }
        });
    }

    async function sendSMS(phone) {
        return await request('/api/sms/send', {
            method: 'POST',
            body: { phone: phone }
        });
    }

    async function verifySMS(smsId, code) {
        return await request('/api/sms/verify', {
            method: 'POST',
            body: { sms_id: smsId, code: code }
        });
    }

    // ========== UI 辅助 ==========

    function showMsg(elementId, message, isError, duration) {
        var el = document.getElementById(elementId);
        if (!el) return;
        el.textContent = message;
        el.className = 'auth-msg ' + (isError ? 'error' : 'success');
        el.style.display = 'block';
        clearTimeout(el._timeout);
        el._timeout = setTimeout(function() {
            el.style.display = 'none';
        }, duration || 3000);
    }

    // ========== 跨标签页同步 ==========

    /**
     * 广播认证状态变更到其他标签页
     * 使用 localStorage 事件（同源的其他标签页可监听到）
     */
    function _broadcastAuthChange(type) {
        try {
            localStorage.setItem('__auth_event__', JSON.stringify({
                type: type,
                timestamp: Date.now()
            }));
            // 立即删除，确保下次变更也能触发事件
            setTimeout(function() {
                localStorage.removeItem('__auth_event__');
            }, 100);
        } catch (e) {}
    }

    /**
     * 监听其他标签页的认证状态变更
     * - 登录：如果当前页面未登录，自动刷新页面状态
     * - 登出：如果当前页面已登录，强制跳转到登录页
     */
    function onAuthChange(callback) {
        window.addEventListener('storage', function(e) {
            if (e.key === '__auth_event__' && e.newValue) {
                try {
                    var evt = JSON.parse(e.newValue);
                    if (typeof callback === 'function') {
                        callback(evt.type, evt);
                    }
                } catch (err) {}
            }

            // 监听 token 变化（直接操作 localStorage 的场景）
            if (e.key === 'token') {
                if (e.newValue && !e.oldValue) {
                    // 其他标签页登录了
                    if (typeof callback === 'function') callback('login', {});
                } else if (!e.newValue && e.oldValue) {
                    // 其他标签页登出了
                    if (typeof callback === 'function') callback('logout', {});
                }
            }
        });
    }

    // ========== 公开 API ==========

    return {
        request: request,
        checkAuth: checkAuth,
        requireAuth: requireAuth,
        redirectIfLoggedIn: redirectIfLoggedIn,
        login: login,
        register: register,
        logout: logout,
        forgotPassword: forgotPassword,
        resetPassword: resetPassword,
        getToken: getToken,
        clearToken: clearToken,
        isRemember: isRemember,
        generateCaptcha: generateCaptcha,
        verifyCaptcha: verifyCaptcha,
        generateSlider: generateSlider,
        verifySlider: verifySlider,
        sendSMS: sendSMS,
        verifySMS: verifySMS,
        showMsg: showMsg,
        onAuthChange: onAuthChange,
        syncTokenToBoth: syncTokenToBoth,
        handleAuthError: handleAuthError,
        verifyToken: verifyToken
    };
})();

// ========== 全局跨标签页同步监听 ==========
// 当其他标签页登录/登出时，自动同步当前页面状态
(function() {
    Auth.onAuthChange(function(type) {
        if (type === 'login') {
            // 其他标签页登录了，刷新当前页面状态
            var token = Auth.getToken();
            if (token) {
                // 当前页面已有 token，刷新用户信息
                location.reload();
            }
        } else if (type === 'logout') {
            // 其他标签页登出了，清除当前页面并跳转
            Auth.clearToken();
            var currentPage = window.location.pathname;
            // 仅在需要登录的页面跳转
            var protectedPages = ['/profile.html', '/edit-profile.html', '/favorites.html', '/history.html', '/reports.html', '/shares.html', '/notifications.html', '/privacy.html'];
            if (protectedPages.indexOf(currentPage) >= 0) {
                window.location.replace('/login.html');
            }
        }
    });
})();
