#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改 index.html：
1. 添加密码登录标签页
2. 添加找回密码页面
3. 添加用户中心页面
4. 优化手机状态栏（更真实）
"""

# 读取原文件
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ===== 1. 修改状态栏HTML（更真实）=====
old_status = '''  <!-- iOS状态栏 -->
  <div class="status">
    <span id="carrier">中国移动</span>
    <span class="t" id="clk">11:58</span>
    <div style="display:flex;align-items:center;">
      <div class="sig" id="sig"><i></i><i></i><i></i><i></i></div>
      <span id="nt" style="font-size:0.6rem;opacity:0.63;margin:0 2px;">4G</span>
      <div class="bat">
        <div class="bat-b"><div class="bat-f" id="bf" style="width:78%;"></div></div>
        <span class="bat-t" id="bt">78%</span>
      </div>
    </div>
  </div>'''

new_status = '''  <!-- iOS状态栏（更真实）-->
  <div class="status">
    <div style="display:flex;align-items:center;gap:4px;">
      <span id="carrier">中国移动</span>
      <span style="font-size:0.55rem;opacity:0.5;">|</span>
      <span id="nt" style="font-size:0.6rem;opacity:0.63;">4G</span>
    </div>
    <span class="t" id="clk">11:58</span>
    <div style="display:flex;align-items:center;gap:3px;">
      <div style="display:flex;align-items:flex-end;gap:1px;height:12px;">
        <div style="width:13px;height:8px;background:rgba(255,255,255,0.9);border-radius:1px;font-size:0.45rem;display:flex;align-items:flex-end;justify-content:center;padding-bottom:1px;">Wi-Fi</div>
      </div>
      <div class="sig" id="sig"><i></i><i></i><i></i><i></i></div>
      <div class="bat">
        <div class="bat-b"><div class="bat-f" id="bf" style="width:78%;"></div></div>
        <span class="bat-t" id="bt">78%</span>
      </div>
    </div>
  </div>'''

if old_status in content:
    content = content.replace(old_status, new_status)
    print('✅ 已更新状态栏（添加WiFi）')
else:
    print('❌ 未找到状态栏，请手动检查')

# ===== 2. 修改登录页面（添加密码登录标签）=====
old_auth_tabs = '''  <!-- 登录/注册标签切换 -->
  <div class="auth-tabs">
    <div class="auth-tab a" id="tab-login" onclick="switchAuthTab('login')">验证码登录</div>
    <div class="auth-tab" id="tab-register" onclick="switchAuthTab('register')">验证码注册</div>
  </div>'''

new_auth_tabs = '''  <!-- 登录/注册标签切换 -->
  <div class="auth-tabs">
    <div class="auth-tab a" id="tab-code-login" onclick="switchAuthTab('code-login')">验证码登录</div>
    <div class="auth-tab" id="tab-pwd-login" onclick="switchAuthTab('pwd-login')">密码登录</div>
    <div class="auth-tab" id="tab-register" onclick="switchAuthTab('register')">注册</div>
  </div>'''

if old_auth_tabs in content:
    content = content.replace(old_auth_tabs, new_auth_tabs)
    print('✅ 已添加密码登录标签')
else:
    print('❌ 未找到登录标签，请手动检查')

# ===== 3. 添加密码登录表单 =====
old_login_form = '''  <!-- 登录表单 -->
  <div id="form-login" class="auth-form">'''

new_login_form = '''  <!-- 验证码登录表单 -->
  <div id="form-code-login" class="auth-form">'''

if old_login_form in content:
    content = content.replace(old_login_form, new_login_form)
    print('✅ 已重命名登录表单')
else:
    print('❌ 未找到登录表单')

# 添加密码登录表单（在注册表单前）
pwd_login_form = '''
  <!-- 密码登录表单 -->
  <div id="form-pwd-login" class="auth-form" style="display:none;">
    <input type="text" class="auth-input" placeholder="手机号" id="pwd-login-phone" maxlength="11">
    <input type="password" class="auth-input" placeholder="密码" id="pwd-login-pwd">
    <div style="display:flex;justify-content:flex-end;font-size:0.7rem;">
      <a onclick="openForgotPwd()" style="color:#ffd700;cursor:pointer;">忘记密码？</a>
    </div>
    <button class="auth-btn" onclick="doPwdLogin()">登 录</button>
  </div>
'''

# 在 form-register 前插入密码登录表单
if '<div id="form-register"' in content:
    content = content.replace('<div id="form-register"', pwd_login_form + '\n  <div id="form-register"')
    print('✅ 已添加密码登录表单')
else:
    print('❌ 未找到注册表单')

# ===== 4. 添加找回密码页面 =====
forgot_pwd_page = '''
<!-- 找回密码页面 -->
<div class="auth-page" id="auth-forgot" style="display:none;">
  <div class="auth-back" onclick="closeForgotPwd()">‹</div>
  <div class="auth-logo">
    <h2>找回密码</h2>
    <p>重置你的登录密码</p>
  </div>
  <div class="auth-form">
    <input type="tel" class="auth-input" placeholder="请输入手机号" id="forgot-phone" maxlength="11">
    <div class="auth-code">
      <input type="text" class="auth-input" placeholder="请输入验证码" id="forgot-code" maxlength="6">
      <button class="auth-code-btn" id="forgot-code-btn" onclick="sendForgotCode()">获取验证码</button>
    </div>
    <input type="password" class="auth-input" placeholder="设置新密码（至少6位）" id="forgot-new-pwd" minlength="6">
    <input type="password" class="auth-input" placeholder="确认新密码" id="forgot-confirm-pwd">
    <button class="auth-btn" onclick="doForgotPwd()">重 置 密 码</button>
  </div>
  <div style="text-align:center;margin-top:1.5rem;font-size:0.75rem;color:rgba(255,255,255,0.5);">
    想起密码了？<a onclick="openAuth('login')" style="color:#ffd700;cursor:pointer;">立即登录</a>
  </div>
</div>
'''

# 在 </body> 前插入找回密码页面
if '</body>' in content:
    content = content.replace('</body>', forgot_pwd_page + '\n</body>')
    print('✅ 已添加找回密码页面')
else:
    print('❌ 未找到 </body>，请手动检查')

# ===== 5. 添加用户中心页面 =====
user_center_page = '''
<!-- 用户中心页面 -->
<div class="auth-page" id="auth-user-center" style="display:none;">
  <div class="auth-back" onclick="closeUserCenter()">‹</div>
  <div style="text-align:center;padding:2rem 0;">
    <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#ffd700,#ff6b35);display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin:0 auto 1rem;">👤</div>
    <div style="font-size:1.1rem;font-weight:600;color:rgba(255,255,255,0.9);" id="uc-name">用户8000</div>
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);margin-top:0.3rem;" id="uc-phone">138****8000</div>
  </div>
  
  <div style="padding:0 1.5rem;">
    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:1rem;margin-bottom:0.8rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
        <span style="font-size:0.85rem;color:rgba(255,255,255,0.7);">免费测算次数</span>
        <span style="font-size:1.2rem;font-weight:700;color:#ffd700;" id="uc-free-count">3</span>
      </div>
      <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;">
        <div style="height:100%;width:30%;background:linear-gradient(90deg,#ffd700,#ff6b35);border-radius:2px;"></div>
      </div>
    </div>
    
    <div style="background:rgba(255,255,255,0.04);border-radius:12px;overflow:hidden;">
      <div style="padding:0.8rem 1rem;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.06);cursor:pointer;" onclick="showToast('测算记录开发中')">
        <span style="font-size:0.85rem;color:rgba(255,255,255,0.7);">📊 测算记录</span>
        <span style="color:rgba(255,255,255,0.3);">›</span>
      </div>
      <div style="padding:0.8rem 1rem;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.06);cursor:pointer;" onclick="showToast('积分明细开发中')">
        <span style="font-size:0.85rem;color:rgba(255,255,255,0.7);">💰 积分明细</span>
        <span style="color:rgba(255,255,255,0.3);">›</span>
      </div>
      <div style="padding:0.8rem 1rem;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.06);cursor:pointer;" onclick="showToast('修改资料开发中')">
        <span style="font-size:0.85rem;color:rgba(255,255,255,0.7);">✏️ 修改资料</span>
        <span style="color:rgba(255,255,255,0.3);">›</span>
      </div>
      <div style="padding:0.8rem 1rem;display:flex;justify-content:space-between;align-items:center;cursor:pointer;" onclick="doLogout()">
        <span style="font-size:0.85rem;color:rgba(255,59,48,0.9);">📤 退出登录</span>
        <span style="color:rgba(255,255,255,0.3);">›</span>
      </div>
    </div>
  </div>
</div>
'''

# 在 </body> 前插入用户中心页面
if '</body>' in content:
    content = content.replace('</body>', user_center_page + '\n</body>')
    print('✅ 已添加用户中心页面')
else:
    print('❌ 未找到 </body>，请手动检查')

# ===== 6. 修改JS：添加新函数 =====
# 在 </script> 前插入新函数
new_functions = '''

// ===== 密码登录 =====
function doPwdLogin(){
    var phone = document.getElementById('pwd-login-phone').value.trim();
    var pwd = document.getElementById('pwd-login-pwd').value;
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号');
        return;
    }
    if(!pwd || pwd.length < 6){
        showToast('密码至少6位');
        return;
    }
    
    showToast('登录中...');
    
    fetch('http://localhost:5000/api/password_login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, password: pwd})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            currentUser = data.data;
            updateUserUI();
            showToast('登录成功！');
            closeAuth();
        } else {
            showToast(data.msg || '登录失败');
        }
    })
    .catch(err => {
        console.error('密码登录失败：', err);
        showToast('网络错误，请重试');
    });
}

// ===== 切换登录/注册标签 =====
function switchAuthTab(tab){
    // 切换标签样式
    document.querySelectorAll('.auth-tab').forEach(function(x){ x.classList.remove('a'); });
    document.getElementById('tab-' + tab).classList.add('a');
    
    // 切换表单
    document.getElementById('form-code-login').style.display = 'none';
    document.getElementById('form-pwd-login').style.display = 'none';
    document.getElementById('form-register').style.display = 'none';
    
    if(tab === 'code-login'){
        document.getElementById('form-code-login').style.display = 'flex';
    } else if(tab === 'pwd-login'){
        document.getElementById('form-pwd-login').style.display = 'flex';
    } else {
        document.getElementById('form-register').style.display = 'flex';
    }
}

// ===== 打开找回密码页面 =====
function openForgotPwd(){
    document.querySelectorAll('.auth-page').forEach(function(x){ x.classList.remove('active'); });
    document.getElementById('auth-forgot').style.display = 'block';
    setTimeout(function(){ document.getElementById('auth-forgot').classList.add('active'); }, 10);
}

function closeForgotPwd(){
    document.getElementById('auth-forgot').classList.remove('active');
    setTimeout(function(){ document.getElementById('auth-forgot').style.display = 'none'; }, 300);
}

// ===== 发送找回密码验证码 =====
function sendForgotCode(){
    var phone = document.getElementById('forgot-phone').value.trim();
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号');
        return;
    }
    
    var btn = document.getElementById('forgot-code-btn');
    btn.disabled = true;
    btn.textContent = '发送中...';
    
    fetch('http://localhost:5000/api/sendCode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            showToast('验证码已发送');
            
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
}

// ===== 提交找回密码 =====
function doForgotPwd(){
    var phone = document.getElementById('forgot-phone').value.trim();
    var code = document.getElementById('forgot-code').value.trim();
    var newPwd = document.getElementById('forgot-new-pwd').value;
    var confirmPwd = document.getElementById('forgot-confirm-pwd').value;
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号');
        return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码');
        return;
    }
    if(!newPwd || newPwd.length < 6){
        showToast('新密码至少6位');
        return;
    }
    if(newPwd !== confirmPwd){
        showToast('两次密码不一致');
        return;
    }
    
    showToast('重置中...');
    
    fetch('http://localhost:5000/api/forgot_password', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code, password: newPwd})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            showToast('密码重置成功！请使用新密码登录');
            setTimeout(function(){ openAuth('login'); }, 1500);
        } else {
            showToast(data.msg || '重置失败');
        }
    })
    .catch(err => {
        console.error('找回密码失败：', err);
        showToast('网络错误，请重试');
    });
}

// ===== 打开用户中心 =====
function openUserCenter(){
    if(!currentUser){
        openAuth();
        return;
    }
    
    // 填充用户信息
    document.getElementById('uc-name').textContent = currentUser.name;
    document.getElementById('uc-phone').textContent = currentUser.phone.substring(0,3) + '****' + currentUser.phone.substring(7);
    document.getElementById('uc-free-count').textContent = currentUser.free_count;
    
    // 显示页面
    document.querySelectorAll('.auth-page').forEach(function(x){ x.classList.remove('active'); });
    document.getElementById('auth-user-center').style.display = 'block';
    setTimeout(function(){ document.getElementById('auth-user-center').classList.add('active'); }, 10);
}

function closeUserCenter(){
    document.getElementById('auth-user-center').classList.remove('active');
    setTimeout(function(){ document.getElementById('auth-user-center').style.display = 'none'; }, 300);
}

// ===== 退出登录 =====
function doLogout(){
    fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(res => res.json())
    .then(data => {
        currentUser = null;
        document.getElementById('user-name-display').textContent = '点击登录/注册';
        document.getElementById('user-desc-display').textContent = '登录后享受更多免费测算次数';
        
        showToast('已退出登录');
        closeUserCenter();
    })
    .catch(err => {
        console.error('退出失败：', err);
        showToast('退出失败，请重试');
    });
}

// ===== 修改 openAuth() 函数 =====
// （需要手动替换）
'''

if '</script>' in content:
    content = content.replace('</script>', new_functions + '\n</script>')
    print('✅ 已添加新JS函数')
else:
    print('❌ 未找到 </script>，请手动检查')

# ===== 7. 修改 openAuth() 函数 =====
old_openAuth = '''function openAuth(){
    // 如果已登录，显示用户中心
    if(currentUser){
        openUserCenter();
        return;
    }
    
    // 否则打开登录页
    closeAuth();
    var page = document.getElementById('auth-page');
    page.classList.add('active');
    // 重置到登录标签
    switchAuthTab('code-login');
}'''

new_openAuth = '''function openAuth(){
    // 如果已登录，显示用户中心
    if(currentUser){
        openUserCenter();
        return;
    }
    
    // 否则打开登录页
    closeAllAuthPages();
    document.getElementById('auth-page').style.display = 'block';
    setTimeout(function(){ document.getElementById('auth-page').classList.add('active'); }, 10);
    // 重置到验证码登录标签
    switchAuthTab('code-login');
}

function closeAuth(){
    document.getElementById('auth-page').classList.remove('active');
    setTimeout(function(){ document.getElementById('auth-page').style.display = 'none'; }, 300);
}

function closeAllAuthPages(){
    document.querySelectorAll('.auth-page').forEach(function(x){
        x.classList.remove('active');
        setTimeout(function(){ x.style.display = 'none'; }, 300);
    });
}'''

if old_openAuth in content:
    content = content.replace(old_openAuth, new_openAuth)
    print('✅ 已更新 openAuth() 函数')
else:
    print('❌ 未找到 openAuth() 函数，请手动检查')

# ===== 8. 修改底部"我的"标签点击事件 =====
old_my_tab = '''    <div class="t" onclick="openAuth()"><span class="ti">👤</span>我的</div>'''

new_my_tab = '''    <div class="t" onclick="checkLogin()"><span class="ti">👤</span>我的</div>'''

if old_my_tab in content:
    content = content.replace(old_my_tab, new_my_tab)
    print('✅ 已更新底部"我的"标签')
else:
    print('❌ 未找到底部"我的"标签')

# 添加 checkLogin() 函数（在JS中）
check_login_func = '''
// ===== 检查登录状态 =====
function checkLogin(){
    if(currentUser){
        openUserCenter();
    } else {
        openAuth();
    }
}
'''

if '// ===== 检查登录状态 =====' not in content:
    # 在 updateClock() 前插入
    if '// ===== 时间更新 =====' in content:
        content = content.replace('// ===== 时间更新 =====', check_login_func + '\n// ===== 时间更新 =====')
        print('✅ 已添加 checkLogin() 函数')
    else:
        print('❌ 未找到插入位置，请手动添加 checkLogin()')

# ===== 写回文件 =====
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n✅ index.html 已更新！')
print('📌 待完成：')
print('  1. 测试密码登录')
print('  2. 测试找回密码')
print('  3. 测试用户中心')
print('  4. 测试退出登录')
