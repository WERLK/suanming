#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化测试：检查点击"我的"是否能跳转
仅生成底部标签栏 + checkLogin 函数
"""
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover">
<title>测试</title>
<style>
body{background:#000;color:#fff;font-family:-apple-system,sans-serif;overflow:hidden;width:100vw;height:100vh;}
.phone{width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;background:#0a0a0a;}
.app{width:100%;max-width:420px;height:100vh;display:flex;flex-direction:column;background:#0f0c29;position:relative;}
.status{display:flex;justify-content:space-between;align-items:center;padding:0.2rem 1rem;background:rgba(0,0,0,0.7);font-size:0.7rem;color:#fff;flex-shrink:0;height:26px;}
.views{flex:1;position:relative;overflow:hidden;}
.page{position:absolute;top:0;left:0;width:100%;height:100%;overflow-y:auto;display:none;flex-direction:column;padding:1rem;}
.page.active{display:flex;}
.ft{display:flex;justify-content:space-around;align-items:center;padding:0.3rem 0.5rem 0.45rem;flex-shrink:0;background:rgba(0,0,0,0.88);border-top:1px solid rgba(255,255,255,0.08);}
.ft .t{display:flex;flex-direction:column;align-items:center;gap:0.1rem;color:rgba(255,255,255,0.3);font-size:0.54rem;cursor:pointer;padding:0.2rem 0.7rem;border-radius:8px;transition:all 0.15s;flex:1;text-align:center;}
.ft .t.a{color:#ffd700;}
.auth-page{position:absolute;top:0;left:0;width:100%;height:100%;background:#0f0c29;display:none;flex-direction:column;padding:2rem 1.5rem;z-index:2000;overflow-y:auto;}
.auth-page.active{display:flex;}
</style>
</head>
<body>
<div class="phone">
<div class="app">
  <div class="status">
    <span>中国移动</span>
    <span>12:23</span>
    <span>4G</span>
  </div>
  <div class="views">
    <div class="page active" id="p-home">
      <h2 style="color:#ffd700;">首页</h2>
      <p style="margin-top:1rem;">currentUser = <span id="user-status">未登录</span></p>
      <button onclick="doTestLogin()" style="margin-top:1rem;padding:0.5rem 1rem;background:#ffd700;color:#000;border:none;border-radius:8px;cursor:pointer;">模拟登录</button>
    </div>
    <div class="page" id="p-uc">
      <h2 style="color:#ffd700;">用户中心</h2>
      <p style="margin-top:1rem;">欢迎，<span id="uc-name">用户</span></p>
      <button onclick="doTestLogout()" style="margin-top:1rem;padding:0.5rem 1rem;background:#ffd700;color:#000;border:none;border-radius:8px;cursor:pointer;">退出登录</button>
    </div>
  </div>
  <div class="ft">
    <div class="t a" onclick="switchTab('home',this)"><span style="font-size:1.15rem;">🏠</span>首页</div>
    <div class="t" onclick="checkLogin()"><span style="font-size:1.15rem;">👤</span>我的</div>
  </div>
</div>
</div>

<div class="auth-page" id="auth-page">
  <h2 style="color:#ffd700;text-align:center;">登录页</h2>
  <button onclick="closeAuth()" style="margin-top:1rem;padding:0.5rem 1rem;background:#ffd700;color:#000;border:none;border-radius:8px;cursor:pointer;">关闭</button>
</div>

<script>
var currentUser = null;

function checkLogin(){
    console.log('checkLogin() 被调用了！currentUser:', currentUser);
    if(currentUser){
        openUserCenter();
    } else {
        openAuth();
    }
}

function openAuth(){
    console.log('openAuth() 被调用了！');
    document.getElementById('auth-page').classList.add('active');
}

function closeAuth(){
    document.getElementById('auth-page').classList.remove('active');
}

function openUserCenter(){
    console.log('openUserCenter() 被调用了！');
    document.querySelectorAll('.page').forEach(function(x){ x.classList.remove('active'); });
    document.getElementById('p-uc').classList.add('active');
    document.getElementById('uc-name').textContent = currentUser.name;
}

function switchTab(page, el){
    document.querySelectorAll('.page').forEach(function(x){ x.classList.remove('active'); });
    document.querySelectorAll('.ft .t').forEach(function(x){ x.classList.remove('a'); });
    var pg = document.getElementById('p-' + page);
    if(pg) pg.classList.add('active');
    if(el) el.classList.add('a');
}

function doTestLogin(){
    currentUser = {name: '测试用户'};
    document.getElementById('user-status').textContent = '已登录 (' + currentUser.name + ')';
    alert('模拟登录成功！现在点击"我的"应该能跳转了');
}

function doTestLogout(){
    currentUser = null;
    document.getElementById('user-status').textContent = '未登录';
    switchTab('home', document.querySelector('.ft .t'));
    alert('已退出登录');
}
</script>
</body>
</html>"""

with open('/workspace/test_minimal.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ 最小化测试页面已生成：/workspace/test_minimal.html')
print('📌 请打开这个文件测试"我的"按钮是否能跳转')
print('   1. 先点击"模拟登录"')
print('   2. 再点击底部"我的"')
print('   3. 如果能跳转，说明原函数名有问题')
print('   4. 如果不能，打开浏览器控制台看错误')
