/**
 * 玄机算命网 - 统一认证模块
 * 所有登录/注册/忘记密码页面共用此模块
 */
window.Auth = (function() {
    'use strict';

    var API_BASE = '';

    // ========== 工具函数 ==========

    function getToken() {
        return localStorage.getItem('token') || sessionStorage.getItem('token');
    }

    function setToken(token, remember) {
        if (remember) {
            localStorage.setItem('token', token);
        } else {
            sessionStorage.setItem('token', token);
        }
    }

    function clearToken() {
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('currentUser');
    }

    async function request(url, options) {
        var token = getToken();
        var headers = options.headers || {};
        headers['Content-Type'] = 'application/json';
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }
        var resp = await fetch(API_BASE + url, {
            method: options.method || 'GET',
            headers: headers,
            body: options.body ? JSON.stringify(options.body) : undefined
        });
        var data = await resp.json();
        if (!resp.ok && data.message) {
            throw new Error(data.message);
        }
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

    // ========== 登录/注册/登出 ==========

    async function login(username, password, remember) {
        var data = await request('/api/login', {
            method: 'POST',
            body: { username: username, password: password, remember: !!remember }
        });
        if (data.success) {
            setToken(data.token, !!remember);
            if (data.user) {
                (remember ? localStorage : sessionStorage).setItem('currentUser', JSON.stringify(data.user));
            }
        }
        return data;
    }

    async function register(username, password, email, phone) {
        var data = await request('/api/register', {
            method: 'POST',
            body: { username: username, password: password, email: email || '', phone: phone || '' }
        });
        if (data.success && data.token) {
            localStorage.setItem('token', data.token);
            if (data.user) {
                localStorage.setItem('currentUser', JSON.stringify(data.user));
            }
        }
        return data;
    }

    async function logout() {
        try {
            await request('/api/logout', { method: 'POST' });
        } catch (e) {}
        clearToken();
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

    // ========== 公开 API ==========

    return {
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
        generateCaptcha: generateCaptcha,
        verifyCaptcha: verifyCaptcha,
        generateSlider: generateSlider,
        verifySlider: verifySlider,
        sendSMS: sendSMS,
        verifySMS: verifySMS,
        showMsg: showMsg
    };
})();
