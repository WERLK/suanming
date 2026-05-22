#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改 index.html 中的 sendCode(), doLogin(), doRegister() 函数
将模拟API改为真实 fetch() 调用
"""

# 读取原文件
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ===== 1. 替换 sendCode() 函数 =====
old_sendCode = """// ===== 发送验证码（模拟API调用）=====
function sendCode(type){
    var phoneInput = document.getElementById(type === 'login' ? 'login-phone' : 'reg-phone');
    var phone = phoneInput.value.trim();
    
    // 验证手机号
    if(!phone || phone.length !== 11 || !/^1[3-9]\\d{9}$/.test(phone)){
        showToast('请输入正确的手机号');
        return;
    }
    
    // 禁用按钮
    var btn = document.getElementById(type + '-code-btn');
    btn.disabled = true;
    
    // 模拟API调用
    showToast('验证码已发送到 ' + phone);
    
    var seconds = 60;
    btn.textContent = seconds + 's后重发';
    
    codeTimer = setInterval(function(){
        seconds--;
        if(seconds <= 0){
            clearInterval(codeTimer);
            btn.disabled = false;
            btn.textContent = '获取验证码';
        } else {
            btn.textContent = seconds + 's后重发';
        }
    }, 1000);
}"""

new_sendCode = """// ===== 发送验证码（真实API调用）=====
function sendCode(type){
    var phoneInput = document.getElementById(type === 'login' ? 'login-phone' : 'reg-phone');
    var phone = phoneInput.value.trim();
    
    // 验证手机号
    if(!phone || phone.length !== 11 || !/^1[3-9]\\d{9}$/.test(phone)){
        showToast('请输入正确的手机号');
        return;
    }
    
    // 禁用按钮
    var btn = document.getElementById(type + '-code-btn');
    btn.disabled = true;
    btn.textContent = '发送中...';
    
    // 调用真实API
    fetch('http://localhost:5000/api/sendCode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            showToast('验证码已发送到 ' + phone);
            
            // 开始倒计时
            var seconds = 60;
            btn.textContent = seconds + 's后重发';
            
            codeTimer = setInterval(function(){
                seconds--;
                if(seconds <= 0){
                    clearInterval(codeTimer);
                    btn.disabled = false;
                    btn.textContent = '获取验证码';
                } else {
                    btn.textContent = seconds + 's后重发';
                }
            }, 1000);
        } else {
            showToast(data.msg || '发送失败');
            btn.disabled = false;
            btn.textContent = '获取验证码';
        }
    })
    .catch(err => {
        console.error('发送验证码失败：', err);
        showToast('网络错误，请重试');
        btn.disabled = false;
        btn.textContent = '获取验证码';
    });
}"""

# ===== 2. 替换 doLogin() 函数 ======
old_doLogin = """// ===== 登录（模拟API调用）=====
function doLogin(){
    var phone = document.getElementById('login-phone').value.trim();
    var code = document.getElementById('login-code').value.trim();
    
    // 验证
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号');
        return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码');
        return;
    }
    
    // 模拟API调用
    showToast('登录中...');
    
    setTimeout(function(){
        // 模拟成功
        currentUser = {
            phone: phone,
            name: '用户' + phone.substring(7),
            avatar: '👤'
        };
        
        // 更新UI
        document.getElementById('user-name-display').textContent = currentUser.name;
        document.getElementById('user-desc-display').textContent = '今日剩余免费测算：3次';
        
        showToast('登录成功！');
        closeAuth();
    }, 1000);
}"""

new_doLogin = """// ===== 登录（真实API调用）=====
function doLogin(){
    var phone = document.getElementById('login-phone').value.trim();
    var code = document.getElementById('login-code').value.trim();
    
    // 验证
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号');
        return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码');
        return;
    }
    
    // 调用真实API
    showToast('登录中...');
    
    fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            // 登录成功
            currentUser = data.data;
            
            // 更新UI
            document.getElementById('user-name-display').textContent = currentUser.name;
            document.getElementById('user-desc-display').textContent = '今日剩余免费测算：' + currentUser.free_count + '次';
            
            showToast('登录成功！');
            closeAuth();
        } else {
            showToast(data.msg || '登录失败');
        }
    })
    .catch(err => {
        console.error('登录失败：', err);
        showToast('网络错误，请重试');
    });
}"""

# ===== 3. 替换 doRegister() 函数 ======
old_doRegister = """// ===== 注册（模拟API调用）=====
function doRegister(){
    var phone = document.getElementById('reg-phone').value.trim();
    var code = document.getElementById('reg-code').value.trim();
    var pass = document.getElementById('reg-pass').value;
    var pass2 = document.getElementById('reg-pass2').value;
    
    // 验证
    if(!phone || phone.length !== 11 || !/^1[3-9]\\d{9}$/.test(phone)){
        showToast('请输入正确的手机号');
        return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码');
        return;
    }
    if(!pass || pass.length < 6){
        showToast('密码至少6位');
        return;
    }
    if(pass !== pass2){
        showToast('两次密码不一致');
        return;
    }
    
    // 模拟API调用
    showToast('注册中...');
    
    setTimeout(function(){
        // 模拟成功
        currentUser = {
            phone: phone,
            name: '用户' + phone.substring(7),
            avatar: '👤'
        };
        
        // 更新UI
        document.getElementById('user-name-display').textContent = currentUser.name;
        document.getElementById('user-desc-display').textContent = '新用户送3次免费测算';
        
        showToast('注册成功！送3次免费测算');
        closeAuth();
    }, 1000);
}"""

new_doRegister = """// ===== 注册（真实API调用）=====
function doRegister(){
    var phone = document.getElementById('reg-phone').value.trim();
    var code = document.getElementById('reg-code').value.trim();
    var pass = document.getElementById('reg-pass').value;
    var pass2 = document.getElementById('reg-pass2').value;
    
    // 验证
    if(!phone || phone.length !== 11 || !/^1[3-9]\\d{9}$/.test(phone)){
        showToast('请输入正确的手机号');
        return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码');
        return;
    }
    if(!pass || pass.length < 6){
        showToast('密码至少6位');
        return;
    }
    if(pass !== pass2){
        showToast('两次密码不一致');
        return;
    }
    
    // 调用真实API
    showToast('注册中...');
    
    fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code, password: pass})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            // 注册成功
            currentUser = data.data;
            
            // 更新UI
            document.getElementById('user-name-display').textContent = currentUser.name;
            document.getElementById('user-desc-display').textContent = '新用户送' + currentUser.free_count + '次免费测算';
            
            showToast('注册成功！送' + currentUser.free_count + '次免费测算');
            closeAuth();
        } else {
            showToast(data.msg || '注册失败');
        }
    })
    .catch(err => {
        console.error('注册失败：', err);
        showToast('网络错误，请重试');
    });
}"""

# ===== 执行替换 =====
if old_sendCode in content:
    content = content.replace(old_sendCode, new_sendCode)
    print('✅ 已替换 sendCode() 函数')
else:
    print('❌ 未找到 sendCode() 函数，请手动检查')

if old_doLogin in content:
    content = content.replace(old_doLogin, new_doLogin)
    print('✅ 已替换 doLogin() 函数')
else:
    print('❌ 未找到 doLogin() 函数，请手动检查')

if old_doRegister in content:
    content = content.replace(old_doRegister, new_doRegister)
    print('✅ 已替换 doRegister() 函数')
else:
    print('❌ 未找到 doRegister() 函数，请手动检查')

# ===== 写回文件 =====
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n✅ index.html 已更新为真实API调用')
print('📌 注意：前端现在请求 http://localhost:5000/api/...')
print('📌 确保 server.py 已启动（端口5000）')
