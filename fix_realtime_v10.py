import json

html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover">
<title>玄机算命网</title>
<style>
{*}{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;overflow:hidden;width:100vw;height:100vh;}
.phone{width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;background:linear-gradient(135deg,#0a0a0a,#1a1a2e,#0a0a0a);}
.app{width:100%;max-width:420px;height:100vh;display:flex;flex-direction:column;background:linear-gradient(180deg,#0f0c29,#1a1a2e 30%,#16213e 70%,#0a0a1a);position:relative;overflow:hidden;box-shadow:0 0 80px rgba(255,215,0,0.1);}
.status{display:flex;justify-content:space-between;align-items:center;padding:0.2rem 1rem;background:rgba(0,0,0,0.7);font-size:0.7rem;color:#fff;flex-shrink:0;height:26px;z-index:1000;}
.hdr{text-align:center;padding:0.65rem 1rem 0.45rem;background:linear-gradient(180deg,rgba(0,0,0,0.75),transparent);border-bottom:1px solid rgba(255,215,0,0.12);flex-shrink:0;}
.hdr h1{font-size:1.2rem;font-weight:800;background:linear-gradient(90deg,#ffd700,#ff6b35,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:2.5px;}
.views{position:relative;flex:1;overflow:hidden;}
.page{position:absolute;top:0;left:0;width:100%;height:100%;overflow-y:auto;display:none;flex-direction:column;}
.page.active{display:flex;}
.page::-webkit-scrollbar{display:none;}
.ft{display:flex;justify-content:space-around;align-items:center;padding:0.3rem 0.5rem 0.45rem;flex-shrink:0;background:rgba(0,0,0,0.88);backdrop-filter:blur(30px);border-top:1px solid rgba(255,255,255,0.08);z-index:1000;}
.ft .t{display:flex;flex-direction:column;align-items:center;gap:0.1rem;color:rgba(255,255,255,0.3);font-size:0.54rem;cursor:pointer;padding:0.2rem 0.7rem;border-radius:8px;transition:all 0.15s;flex:1;text-align:center;}
.ft .t .ti{font-size:1.15rem;transition:all 0.15s;}
.ft .t.a{color:#ffd700;}
.user-bar{display:flex;align-items:center;gap:0.5rem;padding:0.5rem 1rem;cursor:pointer;flex-shrink:0;}
.user-bar:active{opacity:0.7;}
.user-avatar{width:35px;height:35px;border-radius:50%;background:linear-gradient(135deg,#ffd700,#ff6b35);display:flex;align-items:center;justify-content:center;font-size:1.2rem;}
.user-info{flex:1;}
.user-name{font-size:0.8rem;color:#fff;font-weight:600;}
.user-desc{font-size:0.6rem;color:rgba(255,255,255,0.4);margin-top:2px;}
.sch{padding:0.5rem 1rem;flex-shrink:0;}
.sch-i{display:flex;align-items:center;gap:0.5rem;background:rgba(255,255,255,0.06);border-radius:20px;padding:0.5rem 1rem;font-size:0.75rem;color:rgba(255,255,255,0.35);border:1px solid rgba(255,255,255,0.04);}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.5rem;padding:0.5rem 1rem;flex-shrink:0;}
.item{display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015));border-radius:12px;padding:0.6rem 0.1rem;gap:0.28rem;cursor:pointer;border:1px solid rgba(255,215,0,0.06);transition:all 0.15s;}
.item:active{transform:scale(0.93);background:rgba(255,215,0,0.1);}
.item .ic{font-size:1.45rem;}
.item .lb{font-size:0.6rem;color:rgba(255,255,255,0.78);text-align:center;line-height:1.2;font-weight:500;}
.sec{padding:0.7rem 1rem 0.35rem;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.sec h3{font-size:0.85rem;color:#ffd700;font-weight:700;display:flex;align-items:center;gap:0.3rem;}
.sec h3:before{content:'';display:inline-block;width:2.5px;height:12px;background:linear-gradient(180deg,#ffd700,#ff6b35);border-radius:2px;}
.sec .mo{font-size:0.65rem;color:rgba(255,255,255,0.35);cursor:pointer;}
.sec .mo:active{color:#ffd700;}
.zx-list{padding:0 1rem;flex-shrink:0;}
.zx-item{display:flex;gap:0.8rem;padding:0.8rem 0;background:none;border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;transition:all 0.15s;}
.zx-item:last-child{border-bottom:none;}
.zx-item:active{background:rgba(255,255,255,0.03);}
.zx-icon{font-size:1.5rem;flex-shrink:0;}
.zx-info{flex:1;}
.zx-title{font-size:0.78rem;color:rgba(255,255,255,0.85);font-weight:600;margin-bottom:0.2rem;}
.zx-desc{font-size:0.62rem;color:rgba(255,255,255,0.38);line-height:1.5;}
.zx-arrow{color:rgba(255,255,255,0.2);font-size:0.7rem;align-self:center;}
.zb-list{padding:0.5rem 1rem;flex-shrink:0;}
.zb-card{background:linear-gradient(135deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02));border-radius:14px;padding:1rem;margin-bottom:0.6rem;border:1px solid rgba(255,215,0,0.08);cursor:pointer;transition:all 0.15s;}
.zb-card:active{transform:scale(0.97);background:rgba(255,215,0,0.08);}
.zb-title{font-size:0.85rem;color:#ffd700;font-weight:700;margin-bottom:0.4rem;}
.zb-desc{font-size:0.65rem;color:rgba(255,255,255,0.5);line-height:1.6;}
.zb-tag{display:inline-block;padding:2px 8px;background:rgba(255,215,0,0.1);color:#ffd700;border-radius:4px;font-size:0.55rem;margin-top:0.4rem;margin-right:4px;}
.zs-list{padding:0.5rem 1rem;flex-shrink:0;}
.zs-card{background:rgba(255,255,255,0.04);border-radius:12px;padding:0.9rem;margin-bottom:0.5rem;border-left:3px solid #ffd700;cursor:pointer;transition:all 0.15s;}
.zs-card:active{background:rgba(255,215,0,0.06);}
.zs-title{font-size:0.78rem;color:rgba(255,255,255,0.85);font-weight:600;margin-bottom:0.3rem;}
.zs-desc{font-size:0.62rem;color:rgba(255,255,255,0.4);line-height:1.6;}
.empty{text-align:center;padding:3rem 1rem;color:rgba(255,255,255,0.3);font-size:0.75rem;}
.card{margin:0.45rem 1rem;padding:0.8rem;background:linear-gradient(135deg,rgba(255,215,0,0.09),rgba(255,107,53,0.05));border-radius:12px;border:1px solid rgba(255,215,0,0.13);flex-shrink:0;}
.auth-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.92);display:none;flex-direction:column;z-index:9999;overflow-y:auto;}
.auth-overlay.active{display:flex;}
.auth-hdr{display:flex;justify-content:space-between;align-items:center;padding:1rem;flex-shrink:0;}
.auth-back{font-size:1.3rem;color:rgba(255,255,255,0.5);cursor:pointer;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;}
.auth-back:active{background:rgba(255,255,255,0.1);}
.auth-title{font-size:1.1rem;color:#fff;font-weight:700;}
.auth-spacer{width:40px;}
.auth-body{padding:2rem 1.5rem;flex:1;}
.auth-logo{text-align:center;margin-bottom:2rem;}
.auth-logo h2{font-size:1.8rem;font-weight:800;background:linear-gradient(90deg,#ffd700,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:3px;}
.auth-logo p{font-size:0.7rem;color:rgba(255,255,255,0.45);margin-top:0.5rem;}
.auth-tabs{display:flex;gap:0;margin-bottom:1.5rem;border-bottom:1px solid rgba(255,255,255,0.1);}
.auth-tab{flex:1;text-align:center;padding:0.6rem;font-size:0.85rem;color:rgba(255,255,255,0.4);cursor:pointer;transition:all 0.2s;border-bottom:2px solid transparent;}
.auth-tab.a{color:#ffd700;border-bottom-color:#ffd700;font-weight:600;}
.auth-form{display:flex;flex-direction:column;gap:1rem;}
.auth-input{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.8rem 1rem;color:#fff;font-size:0.85rem;outline:none;transition:all 0.2s;}
.auth-input:focus{border-color:rgba(255,215,0,0.5);background:rgba(255,255,255,0.1);}
.auth-input::placeholder{color:rgba(255,255,255,0.25);}
.auth-btn{background:linear-gradient(135deg,#ffd700,#ff6b35);color:#1a1a2e;font-size:0.9rem;font-weight:700;padding:0.8rem;border:none;border-radius:12px;cursor:pointer;transition:all 0.2s;margin-top:0.5rem;}
.auth-btn:active{transform:scale(0.97);}
.auth-link{text-align:center;font-size:0.75rem;color:rgba(255,255,255,0.45);margin-top:1rem;cursor:pointer;}
.auth-link:active{color:#ffd700;}
.auth-form .row{display:flex;gap:0.5rem;}
.auth-form .row .auth-input{flex:1;}
.auth-form .row button{background:rgba(255,215,0,0.15);color:#ffd700;border:1px solid rgba(255,215,0,0.3);border-radius:12px;padding:0.8rem 1rem;font-size:0.75rem;cursor:pointer;white-space:nowrap;transition:all 0.2s;}
.auth-form .row button:disabled{opacity:0.4;cursor:not-allowed;}
.uc-page{position:fixed;top:0;left:0;width:100%;height:100%;background:linear-gradient(180deg,#0f0c29,#1a1a2e 50%,#0a0a1a);display:none;flex-direction:column;z-index:9999;overflow-y:auto;}
.uc-page.active{display:flex;}
.uc-hdr{display:flex;justify-content:space-between;align-items:center;padding:1rem;flex-shrink:0;}
.uc-back{font-size:1.3rem;color:rgba(255,255,255,0.5);cursor:pointer;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;}
.uc-title{font-size:1.1rem;color:#fff;font-weight:700;}
.uc-spacer{width:40px;}
.uc-body{padding:1.5rem;flex:1;}
.uc-card{background:linear-gradient(135deg,rgba(255,215,0,0.12),rgba(255,107,53,0.06));border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;border:1px solid rgba(255,215,0,0.15);}
.uc-avatar{width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#ffd700,#ff6b35);display:flex;align-items:center;justify-content:center;font-size:2rem;margin-bottom:1rem;}
.uc-name{font-size:1.2rem;color:#fff;font-weight:700;margin-bottom:0.3rem;}
.uc-phone{font-size:0.75rem;color:rgba(255,255,255,0.45);}
.uc-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;margin-top:1.2rem;}
.uc-stat{text-align:center;}
.uc-stat-v{font-size:1.3rem;color:#ffd700;font-weight:700;}
.uc-stat-l{font-size:0.6rem;color:rgba(255,255,255,0.4);margin-top:3px;}
.uc-menu{background:rgba(255,255,255,0.04);border-radius:12px;overflow:hidden;}
.uc-menu-i{display:flex;align-items:center;gap:0.8rem;padding:1rem 1.2rem;border-bottom:1px solid rgba(255,255,255,0.06);cursor:pointer;transition:all 0.15s;}
.uc-menu-i:last-child{border-bottom:none;}
.uc-menu-i:active{background:rgba(255,255,255,0.06);}
.uc-menu-i .ic{font-size:1.2rem;}
.uc-menu-i .lb{flex:1;font-size:0.85rem;color:rgba(255,255,255,0.8);}
.uc-menu-i .ar{color:rgba(255,255,255,0.25);font-size:0.7rem;}
.logout-btn{background:rgba(255,50,50,0.15);color:#ff5555;border:1px solid rgba(255,50,50,0.3);border-radius:12px;padding:0.8rem;font-size:0.85rem;cursor:pointer;margin-top:1.5rem;text-align:center;transition:all 0.2s;}
.logout-btn:active{background:rgba(255,50,50,0.25);}
.toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.88);color:#fff;padding:0.8rem 1.5rem;border-radius:12px;font-size:0.8rem;z-index:10000;display:none;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.1);pointer-events:none;}
</style>
</head>
<body>
<div class="phone">
<div class="app">
  <!-- 状态栏 -->
  <div class="status">
    <span class="t" id="carrier-text">中国移动</span>
    <span style="display:flex;align-items:center;gap:4px;">
      <span class="sig"><i></i><i></i><i></i><i></i></span>
      <span style="font-size:0.6rem;margin:0 2px;">5G</span>
      <span class="bat"><span class="bat-b"><span class="bat-f" id="bat-fill"></span></span><span class="bat-t" id="bat-text"></span></span>
    </span>
  </div>

  <!-- 头部 -->
  <div class="hdr">
    <h1>玄机算命网</h1>
  </div>

  <!-- 用户栏 -->
  <div class="user-bar" id="user-bar" onclick="checkLogin()">
    <div class="user-avatar" id="ub-avatar">👤</div>
    <div class="user-info">
      <div class="user-name" id="ub-name">点击登录</div>
      <div class="user-desc" id="ub-desc">登录后享受更多服务</div>
    </div>
  </div>

  <!-- 搜索 -->
  <div class="sch"><div class="sch-i">🔍 搜索你想要的服务</div></div>

  <!-- 内容区 -->
  <div class="views">
    <!-- 首页 -->
    <div class="page active" id="page-home">
      <div class="sec"><h3>🔮 热门服务</h3><span class="mo" onclick="switchTab('more',document.querySelectorAll('.ft .t')[2])">更多 ›</span></div>
      <div class="grid" id="home-services">
        <div class="item" onclick="showToast('八字排盘开发中')"><span class="ic">🔮</span><span class="lb">八字排盘</span></div>
        <div class="item" onclick="showToast('紫微斗数开发中')"><span class="ic">🌟</span><span class="lb">紫微斗数</span></div>
        <div class="item" onclick="showToast('塔罗占卜开发中')"><span class="ic">🎋</span><span class="lb">塔罗占卜</span></div>
        <div class="item" onclick="showToast('易经占卦开发中')"><span class="ic">🃏</span><span class="lb">易经占卦</span></div>
        <div class="item" onclick="showToast('姻缘测算开发中')"><span class="ic">💑</span><span class="lb">姻缘测算</span></div>
        <div class="item" onclick="showToast('财运分析开发中')"><span class="ic">💰</span><span class="lb">财运分析</span></div>
        <div class="item" onclick="showToast('风水布局开发中')"><span class="ic">🏠</span><span class="lb">风水布局</span></div>
        <div class="item" onclick="showToast('黄道吉日开发中')"><span class="ic">📅</span><span class="lb">黄道吉日</span></div>
      </div>
      
      <div class="sec"><h3>📜 今日运势</h3><span class="mo" onclick="refreshFortune()">刷新 ↻</span></div>
      <div id="home-fortune" style="padding:0.5rem 1rem;flex-shrink:0;">
        <div style="background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,107,53,0.05));border-radius:12px;padding:1rem;border:1px solid rgba(255,215,0,0.12);">
          <div style="font-size:0.8rem;color:#ffd700;font-weight:700;margin-bottom:0.5rem;">综合运势指数</div>
          <div style="display:flex;gap:0.8rem;align-items:center;">
            <div style="flex:1;">
              <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:rgba(255,255,255,0.5);margin-bottom:0.3rem;"><span>事业</span><span id="career-value">--</span></div>
              <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;margin-bottom:0.5rem;"><div id="career-bar" style="width:0%;height:100%;background:linear-gradient(90deg,#ffd700,#ff6b35);border-radius:2px;transition:width 1s;"></div></div>
              <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:rgba(255,255,255,0.5);margin-bottom:0.3rem;"><span>财运</span><span id="wealth-value">--</span></div>
              <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;margin-bottom:0.5rem;"><div id="wealth-bar" style="width:0%;height:100%;background:linear-gradient(90deg,#ffd700,#ff6b35);border-radius:2px;transition:width 1s;"></div></div>
              <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:rgba(255,255,255,0.5);margin-bottom:0.3rem;"><span>感情</span><span id="love-value">--</span></div>
              <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;"><div id="love-bar" style="width:0%;height:100%;background:linear-gradient(90deg,#ffd700,#ff6b35);border-radius:2px;transition:width 1s;"></div></div>
            </div>
          </div>
        </div>
      </div>

      <div class="sec"><h3>🎯 热门推荐</h3></div>
      <div id="home-recommend" class="loading">加载中...</div>

      <div class="sec"><h3>📚 最新文章</h3><span class="mo" onclick="switchTab('zhishi',document.querySelectorAll('.ft .t')[3])">更多 ›</span></div>
      <div id="home-articles">
        <!-- 动态加载 -->
      </div>

      <div style="padding:1rem;text-align:center;color:rgba(255,255,255,0.3);font-size:0.7rem;flex-shrink:0;">— 精彩内容持续更新中 —</div>
    </div>

    <!-- 更多服务页 -->
    <div class="page" id="page-more">
      <div class="sec"><h3>🔮 全部服务</h3></div>
      <div class="grid">
        <div class="item" onclick="showToast('八字排盘')"><span class="ic">🔮</span><span class="lb">八字排盘</span></div>
        <div class="item" onclick="showToast('紫微斗数')"><span class="ic">🌟</span><span class="lb">紫微斗数</span></div>
        <div class="item" onclick="showToast('塔罗占卜')"><span class="ic">🎋</span><span class="lb">塔罗占卜</span></div>
        <div class="item" onclick="showToast('易经占卦')"><span class="ic">🃏</span><span class="lb">易经占卦</span></div>
        <div class="item" onclick="showToast('姻缘测算')"><span class="ic">💑</span><span class="lb">姻缘测算</span></div>
        <div class="item" onclick="showToast('财运分析')"><span class="ic">💰</span><span class="lb">财运分析</span></div>
        <div class="item" onclick="showToast('风水布局')"><span class="ic">🏠</span><span class="lb">风水布局</span></div>
        <div class="item" onclick="showToast('黄道吉日')"><span class="ic">📅</span><span class="lb">黄道吉日</span></div>
        <div class="item" onclick="showToast('姓名测试')"><span class="ic">📛</span><span class="lb">姓名测试</span></div>
        <div class="item" onclick="showToast('面相分析')"><span class="ic">👤</span><span class="lb">面相分析</span></div>
        <div class="item" onclick="showToast('手相解读')"><span class="ic">🖐️</span><span class="lb">手相解读</span></div>
        <div class="item" onclick="showToast('星座配对')"><span class="ic">⭐</span><span class="lb">星座配对</span></div>
        <div class="item" onclick="showToast('周公解梦')"><span class="ic">🌙</span><span class="lb">周公解梦</span></div>
        <div class="item" onclick="showToast('抽签问卦')"><span class="ic">🎴</span><span class="lb">抽签问卦</span></div>
        <div class="item" onclick="showToast('贵人方位')"><span class="ic">🧭</span><span class="lb">贵人方位</span></div>
        <div class="item" onclick="showToast('桃花运测算')"><span class="ic">🌸</span><span class="lb">桃花运测算</span></div>
      </div>
    </div>

    <!-- 生肖 -->
    <div class="page" id="page-shengxiao">
      <div class="sec"><h3>🐉 生肖运势</h3></div>
      <div class="grid">
        <div class="item" onclick="showToast('鼠年运势')"><span class="ic">🐭</span><span class="lb">鼠</span></div>
        <div class="item" onclick="showToast('牛年运势')"><span class="ic">🐮</span><span class="lb">牛</span></div>
        <div class="item" onclick="showToast('虎年运势')"><span class="ic">🐯</span><span class="lb">虎</span></div>
        <div class="item" onclick="showToast('兔年运势')"><span class="ic">🐰</span><span class="lb">兔</span></div>
        <div class="item" onclick="showToast('龙年运势')"><span class="ic">🐲</span><span class="lb">龙</span></div>
        <div class="item" onclick="showToast('蛇年运势')"><span class="ic">🐍</span><span class="lb">蛇</span></div>
        <div class="item" onclick="showToast('马年运势')"><span class="ic">🐴</span><span class="lb">马</span></div>
        <div class="item" onclick="showToast('羊年运势')"><span class="ic">🐑</span><span class="lb">羊</span></div>
        <div class="item" onclick="showToast('猴年运势')"><span class="ic">🐵</span><span class="lb">猴</span></div>
        <div class="item" onclick="showToast('鸡年运势')"><span class="ic">🐔</span><span class="lb">鸡</span></div>
        <div class="item" onclick="showToast('狗年运势')"><span class="ic">🐶</span><span class="lb">狗</span></div>
        <div class="item" onclick="showToast('猪年运势')"><span class="ic">🐷</span><span class="lb">猪</span></div>
      </div>
      <div class="sec"><h3>📊 今日生肖排行</h3></div>
      <div class="zx-list">
        <div class="zx-item"><span class="zx-icon">🥇</span><div class="zx-info"><div class="zx-title">生肖龙</div><div class="zx-desc">今日运势最佳，贵人运强，适合签约合作</div></div><span class="zx-arrow">›</span></div>
        <div class="zx-item"><span class="zx-icon">🥈</span><div class="zx-info"><div class="zx-title">生肖鼠</div><div class="zx-desc">财运亨通，适合投资理财，会有意外收获</div></div><span class="zx-arrow">›</span></div>
        <div class="zx-item"><span class="zx-icon">🥉</span><div class="zx-info"><div class="zx-title">生肖蛇</div><div class="zx-desc">桃花运旺，单身者有望脱单，感情顺利</div></div><span class="zx-arrow">›</span></div>
      </div>
      <div class="sec"><h3>💡 生肖配对</h3></div>
      <div class="card">
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.7);line-height:1.8;">
          <div style="color:#ffd700;font-weight:700;margin-bottom:0.3rem;">最佳配对</div>
          鼠配牛、虎配猪、兔配狗、龙配鸡<br>
          蛇配猴、马配羊、猴配蛇、鸡配龙<br>
          狗配兔、猪配虎
        </div>
      </div>
    </div>

    <!-- 占卜 -->
    <div class="page" id="page-zhanbu">
      <div class="sec"><h3>🔮 占卜大厅</h3></div>
      <div class="zb-list">
        <div class="zb-card" onclick="showToast('塔罗牌开发中')">
          <div class="zb-title">🎴 塔罗牌占卜</div>
          <div class="zb-desc">抽取塔罗牌，解读过去、现在与未来的奥秘。提供爱情、事业、财运等多方面指引。专业的牌阵分析，让你洞察人生方向。</div>
          <span class="zb-tag">热门</span>
          <span class="zb-tag">推荐</span>
        </div>
        <div class="zb-card" onclick="showToast('易经占卦开发中')">
          <div class="zb-title">☯️ 易经占卦</div>
          <div class="zb-desc">使用古法揲蓍草起卦，结合《周易》六十四卦，为您解答人生疑惑。涵盖事业、婚姻、健康等各个方面。</div>
          <span class="zb-tag">经典</span>
        </div>
        <div class="zb-card" onclick="showToast('紫微斗数开发中')">
          <div class="zb-title">⭐ 紫微斗数</div>
          <div class="zb-desc">通过分析命盘十二宫，详解命主性格、事业、婚姻、财运等人生各方面。准确率极高的传统命理学。</div>
          <span class="zb-tag">专业</span>
        </div>
        <div class="zb-card" onclick="showToast('灵棋经开发中')">
          <div class="zb-title">🎲 灵棋经</div>
          <div class="zb-desc">源自道教的传统占卜法，通过棋局变化预测吉凶祸福。共有125卦，每卦皆有详解。</div>
        </div>
        <div class="zb-card" onclick="showToast('六爻占卜开发中')">
          <div class="zb-title">📯 六爻占卜</div>
          <div class="zb-desc">以六爻卦象预测事物发展变化。通过铜钱摇卦，结合五行生克，精准预测未来趋势。</div>
        </div>
        <div class="zb-card" onclick="showToast('奇门遁甲开发中')">
          <div class="zb-title">🌀 奇门遁甲</div>
          <div class="zb-desc">古代最高层次的预测术之一。通过排盘分析时间与空间的关系，用于决策、择日、风水布局等。</div>
          <span class="zb-tag">高级</span>
        </div>
      </div>
    </div>

    <!-- 知识 -->
    <div class="page" id="page-zhishi">
      <div class="sec"><h3>📚 命理知识库</h3></div>
      <div class="zs-list">
        <div class="zs-card">
          <div class="zs-title">什么是八字？</div>
          <div class="zs-desc">八字，即生辰八字，是一个人出生时的干支历日期。年干和年支组成年柱，月干和月支组成月柱，日干和日支组成日柱，时干和时支组成时柱。八字在汉族民俗信仰中占有重要地位，古代星相家据此推算人的命运的好坏...</div>
        </div>
        <div class="zs-card">
          <div class="zs-title">五行相生相克</div>
          <div class="zs-desc">五行是指金、木、水、火、土五种基本元素。相生关系：金生水、水生木、木生火、火生土、土生金。相克关系：金克木、木克土、土克水、水克火、火克金。五行学说认为宇宙万物都由这五种基本物质的运行和循环生克变化所构成...</div>
        </div>
        <div class="zs-card">
          <div class="zs-title">十二生肖的由来</div>
          <div class="zs-desc">十二生肖，又叫属相，是中国与十二地支相配以人出生年份的十二种动物。包括鼠、牛、虎、兔、龙、蛇、马、羊、猴、鸡、狗、猪。据考证，先秦时期即有完整的生肖系统存在...</div>
        </div>
        <div class="zs-card">
          <div class="zs-title">紫微斗数入门</div>
          <div class="zs-desc">紫微斗数是中国传统命理学的最重要的派别之一。它是以人出生的年、月、日、时确定十二宫的位置，构成命盘，结合各宫的星群组合，牵系周易卦爻，来预测一个人的命运流程、吉凶祸福...</div>
        </div>
        <div class="zs-card">
          <div class="zs-title">风水基础知识</div>
          <div class="zs-desc">风水，又称堪舆，是中国历史悠久的一门玄术。风水的核心思想是人与大自然的和谐共处。早期的风水主要关乎宫殿、住宅、村落、墓地的选址、座向、建设等方法及原则...</div>
        </div>
        <div class="zs-card">
          <div class="zs-title">塔罗牌大阿卡纳解读</div>
          <div class="zs-desc">塔罗牌共有78张，其中22张为大阿卡纳，代表人生的重大课题与精神层面的指引。包括愚者、魔术师、女祭司、女皇、皇帝、教皇、恋人、战车等重要牌面...</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 底部标签 -->
  <div class="ft">
    <div class="t a" onclick="switchTab('home',this)"><span class="ti">🏠</span>首页</div>
    <div class="t" onclick="switchTab('shengxiao',this)"><span class="ti">🐉</span>生肖</div>
    <div class="t" onclick="switchTab('more',this)"><span class="ti">🔮</span>更多</div>
    <div class="t" onclick="switchTab('zhanbu',this)"><span class="ti">🃏</span>占卜</div>
    <div class="t" onclick="checkLogin()"><span class="ti">👤</span>我的</div>
  </div>
</div>
</div>

<!-- 登录/注册弹层 -->
<div class="auth-overlay" id="auth-overlay">
  <div class="auth-hdr">
    <div class="auth-back" onclick="closeAuth()">✕</div>
    <div class="auth-title">欢迎来到玄机算命网</div>
    <div class="auth-spacer"></div>
  </div>
  <div class="auth-body">
    <div class="auth-logo">
      <h2>玄机算命网</h2>
      <p>专业命理测算 · 传承千年智慧</p>
    </div>
    <div class="auth-tabs">
      <div class="auth-tab a" id="at-code" onclick="switchAuthTab('code')">验证码登录</div>
      <div class="auth-tab" id="at-pwd" onclick="switchAuthTab('pwd')">密码登录</div>
      <div class="auth-tab" id="at-reg" onclick="switchAuthTab('reg')">注册</div>
    </div>
    <!-- 验证码登录 -->
    <div class="auth-form" id="af-code">
      <input class="auth-input" id="login-phone" type="tel" maxlength="11" placeholder="请输入手机号">
      <div class="row">
        <input class="auth-input" id="login-code" type="tel" maxlength="6" placeholder="请输入验证码">
        <button id="login-code-btn" onclick="sendCode('login')">获取验证码</button>
      </div>
      <button class="auth-btn" onclick="doLogin()">登 录</button>
    </div>
    <!-- 密码登录 -->
    <div class="auth-form" id="af-pwd" style="display:none;">
      <input class="auth-input" id="pwd-phone" type="tel" maxlength="11" placeholder="请输入手机号">
      <input class="auth-input" id="pwd-password" type="password" placeholder="请输入密码">
      <button class="auth-btn" onclick="doPwdLogin()">登 录</button>
      <div class="auth-link" onclick="switchAuthTab('forgot')">忘记密码？</div>
    </div>
    <!-- 注册 -->
    <div class="auth-form" id="af-reg" style="display:none;">
      <input class="auth-input" id="reg-phone" type="tel" maxlength="11" placeholder="请输入手机号">
      <div class="row">
        <input class="auth-input" id="reg-code" type="tel" maxlength="6" placeholder="验证码">
        <button id="reg-code-btn" onclick="sendCode('reg')">获取验证码</button>
      </div>
      <input class="auth-input" id="reg-password" type="password" placeholder="设置密码（6-20位）">
      <button class="auth-btn" onclick="doRegister()">注 册</button>
    </div>
    <!-- 忘记密码 -->
    <div class="auth-form" id="af-forgot" style="display:none;">
      <input class="auth-input" id="forgot-phone" type="tel" maxlength="11" placeholder="请输入手机号">
      <div class="row">
        <input class="auth-input" id="forgot-code" type="tel" maxlength="6" placeholder="验证码">
        <button id="forgot-code-btn" onclick="sendCode('forgot')">获取验证码</button>
      </div>
      <input class="auth-input" id="forgot-password" type="password" placeholder="新密码（6-20位）">
      <button class="auth-btn" onclick="doForgotPwd()">重置密码</button>
    </div>
  </div>
</div>

<!-- 用户中心页 -->
<div class="uc-page" id="uc-page">
  <div class="uc-hdr">
    <div class="uc-back" onclick="closeUserCenter()">✕</div>
    <div class="uc-title">个人中心</div>
    <div class="uc-spacer"></div>
  </div>
  <div class="uc-body">
    <div class="uc-card">
      <div class="uc-avatar" id="uc-avatar">👤</div>
      <div class="uc-name" id="uc-name">用户</div>
      <div class="uc-phone" id="uc-phone">手机号</div>
      <div class="uc-stats">
        <div class="uc-stat"><div class="uc-stat-v" id="uc-free">3</div><div class="uc-stat-l">免费次数</div></div>
        <div class="uc-stat"><div class="uc-stat-v">0</div><div class="uc-stat-l">已测次数</div></div>
        <div class="uc-stat"><div class="uc-stat-v">0</div><div class="uc-stat-l">分享次数</div></div>
      </div>
    </div>
    <div class="uc-menu">
      <div class="uc-menu-i"><span class="ic">📜</span><span class="lb">测算历史</span><span class="ar">›</span></div>
      <div class="uc-menu-i"><span class="ic">❤️</span><span class="lb">我的收藏</span><span class="ar">›</span></div>
      <div class="uc-menu-i"><span class="ic">🎁</span><span class="lb">邀请有礼</span><span class="ar">›</span></div>
      <div class="uc-menu-i"><span class="ic">⚙️</span><span class="lb">设置</span><span class="ar">›</span></div>
      <div class="uc-menu-i"><span class="ic">💬</span><span class="lb">意见反馈</span><span class="ar">›</span></div>
      <div class="uc-menu-i"><span class="ic">📞</span><span class="lb">联系客服</span><span class="ar">›</span></div>
    </div>
    <div class="logout-btn" onclick="doLogout()">退出登录</div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
var currentUser = null;
var codeTimer = null;
var batteryTimer = null;

// ===== 初始化 =====
window.onload = function(){
    updateBattery();
    checkSavedLogin();
    loadAllData();
    // 每10秒更新一次电量
    batteryTimer = setInterval(updateBattery, 10000);
};

// ===== 实时更新电池 =====
function updateBattery(){
    // 模拟真实电量变化（逐渐消耗或充电）
    var currentLevel = parseInt(localStorage.getItem('battery_level')) || 78;
    
    // 随机消耗1-3%或充电1-2%
    var change = Math.random() > 0.7 ? Math.floor(Math.random() * 3) + 1 : -Math.floor(Math.random() * 3) - 1;
    currentLevel += change;
    
    // 限制在1-100之间
    currentLevel = Math.max(1, Math.min(100, currentLevel));
    
    localStorage.setItem('battery_level', currentLevel);
    
    var fill = document.getElementById('bat-fill');
    var text = document.getElementById('bat-text');
    fill.style.width = currentLevel + '%';
    text.textContent = currentLevel + '%';
    
    if(currentLevel <= 20){ 
        fill.className = 'bat-f lo'; 
    } else if(currentLevel <= 50){ 
        fill.className = 'bat-f mi'; 
    } else { 
        fill.className = 'bat-f'; 
    }
}

// ===== 检查已保存的登录 =====
function checkSavedLogin(){
    var saved = localStorage.getItem('xjsm_user');
    if(saved){
        try{
            currentUser = JSON.parse(saved);
            updateUserBar();
        }catch(e){}
    }
}

// ===== 更新用户栏 =====
function updateUserBar(){
    if(currentUser){
        document.getElementById('ub-avatar').textContent = currentUser.avatar || '👤';
        document.getElementById('ub-name').textContent = currentUser.name;
        document.getElementById('ub-desc').textContent = '欢迎回来';
    }
}

// ===== 加载所有数据 =====
function loadAllData(){
    loadFortune();
    loadHomeRecommend();
    loadHomeArticles();
}

// ===== 加载运势 =====
function loadFortune(){
    var career = Math.floor(Math.random() * 41) + 60;
    var wealth = Math.floor(Math.random() * 41) + 60;
    var love = Math.floor(Math.random() * 41) + 60;
    
    document.getElementById('career-value').textContent = career + '%';
    document.getElementById('wealth-value').textContent = wealth + '%';
    document.getElementById('love-value').textContent = love + '%';
    
    setTimeout(function(){
        document.getElementById('career-bar').style.width = career + '%';
        document.getElementById('wealth-bar').style.width = wealth + '%';
        document.getElementById('love-bar').style.width = love + '%';
    }, 100);
}

function refreshFortune(){
    showToast('运势已更新');
    loadFortune();
}

// ===== 加载热门推荐 =====
function loadHomeRecommend(){
    var recommends = [
        {title:'🔥 本周最准占卜', desc:'根据您的生辰八字，本周三、周五是最佳决策日。适合签约、投资、表白。'},
        {title:'💡 开运小妙招', desc:'今天适合佩戴金色饰品提升财运。办公桌左上方放置绿色植物可旺事业运。'}
    ];
    
    var html = '';
    recommends.forEach(function(r){
        html += '<div class="card"><div style="font-size:0.8rem;color:#ffd700;font-weight:700;margin-bottom:0.4rem;">' + r.title + '</div><div style="font-size:0.7rem;color:rgba(255,255,255,0.6);line-height:1.7;">' + r.desc + '</div></div>';
    });
    document.getElementById('home-recommend').innerHTML = html;
    document.getElementById('home-recommend').className = '';
}

// ===== 加载首页文章 =====
function loadHomeArticles(){
    var articles = [
        {title:'2026年鼠年运势大全', desc:'2026丙午马年，对于属鼠的朋友来说是冲太岁的年份。整体运势起伏较大，需要特别注意...'},
        {title:'如何通过八字看财运', desc:'八字中的财星代表一个人的财富运势。正财代表稳定收入，偏财代表意外之财...'}
    ];
    
    var html = '';
    articles.forEach(function(a){
        html += '<div class="zs-list"><div class="zs-card"><div class="zs-title">' + a.title + '</div><div class="zs-desc">' + a.desc + '</div></div></div>';
    });
    document.getElementById('home-articles').innerHTML = html;
}

// ===== 切换标签 =====
function switchTab(page, el){
    console.log('Switching to tab:', page);
    document.querySelectorAll('.page').forEach(function(p){ 
        p.classList.remove('active'); 
    });
    document.querySelectorAll('.ft .t').forEach(function(t){ 
        t.classList.remove('a'); 
    });
    var target = document.getElementById('page-' + page);
    if(target){ 
        target.classList.add('active'); 
        console.log('Activated page:', 'page-' + page);
    } else {
        console.error('Page not found:', 'page-' + page);
    }
    if(el){ el.classList.add('a'); }
}

// ===== 检查登录 =====
function checkLogin(){
    console.log('checkLogin called, currentUser:', currentUser);
    if(currentUser){
        openUserCenter();
    } else {
        openAuth();
    }
}

// ===== 打开登录层 =====
function openAuth(){
    document.getElementById('auth-overlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

// ===== 关闭登录层 =====
function closeAuth(){
    document.getElementById('auth-overlay').classList.remove('active');
    document.body.style.overflow = '';
}

// ===== 切换登录标签 =====
function switchAuthTab(tab){
    document.querySelectorAll('.auth-tab').forEach(function(t){ t.classList.remove('a'); });
    document.querySelectorAll('.auth-form').forEach(function(f){ f.style.display = 'none'; });
    
    if(tab === 'code'){
        document.getElementById('at-code').classList.add('a');
        document.getElementById('af-code').style.display = 'flex';
    } else if(tab === 'pwd'){
        document.getElementById('at-pwd').classList.add('a');
        document.getElementById('af-pwd').style.display = 'flex';
    } else if(tab === 'reg'){
        document.getElementById('at-reg').classList.add('a');
        document.getElementById('af-reg').style.display = 'flex';
    } else if(tab === 'forgot'){
        document.getElementById('at-pwd').classList.add('a');
        document.getElementById('af-forgot').style.display = 'flex';
    }
}

// ===== 发送验证码 =====
function sendCode(type){
    var phoneInput = document.getElementById(type === 'login' ? 'login-phone' : (type === 'reg' ? 'reg-phone' : 'forgot-phone'));
    var phone = phoneInput.value.trim();
    
    if(!phone || phone.length !== 11 || !/^1[3-9]\d{9}$/.test(phone)){
        showToast('请输入正确的手机号');
        return;
    }
    
    var btnId = type + '-code-btn';
    var btn = document.getElementById(btnId);
    if(!btn){ btn = phoneInput.parentElement.querySelector('button'); }
    btn.disabled = true;
    btn.textContent = '发送中...';
    
    fetch('http://localhost:5000/api/sendCode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone})
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
        if(data.code === 200){
            showToast('验证码已发送');
            var seconds = 60;
            btn.textContent = seconds + 's';
            codeTimer = setInterval(function(){
                seconds--;
                if(seconds <= 0){
                    clearInterval(codeTimer);
                    btn.disabled = false;
                    btn.textContent = '获取验证码';
                } else {
                    btn.textContent = seconds + 's';
                }
            }, 1000);
        } else {
            showToast(data.msg || '发送失败');
            btn.disabled = false;
            btn.textContent = '获取验证码';
        }
    })
    .catch(function(err){
        console.error('发送失败：', err);
        showToast('网络错误');
        btn.disabled = false;
        btn.textContent = '获取验证码';
    });
}

// ===== 验证码登录 =====
function doLogin(){
    var phone = document.getElementById('login-phone').value.trim();
    var code = document.getElementById('login-code').value.trim();
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号'); return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码'); return;
    }
    
    fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code})
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
        if(data.code === 200){
            currentUser = data.user;
            localStorage.setItem('xjsm_user', JSON.stringify(currentUser));
            updateUserBar();
            closeAuth();
            showToast('登录成功');
        } else {
            showToast(data.msg || '登录失败');
        }
    })
    .catch(function(err){
        console.error('登录失败：', err);
        showToast('网络错误');
    });
}

// ===== 密码登录 =====
function doPwdLogin(){
    var phone = document.getElementById('pwd-phone').value.trim();
    var pwd = document.getElementById('pwd-password').value;
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号'); return;
    }
    if(!pwd){
        showToast('请输入密码'); return;
    }
    
    fetch('http://localhost:5000/api/password_login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, password: pwd})
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
        if(data.code === 200){
            currentUser = data.user;
            localStorage.setItem('xjsm_user', JSON.stringify(currentUser));
            updateUserBar();
            closeAuth();
            showToast('登录成功');
        } else {
            showToast(data.msg || '登录失败');
        }
    })
    .catch(function(err){
        console.error('登录失败：', err);
        showToast('网络错误');
    });
}

// ===== 注册 =====
function doRegister(){
    var phone = document.getElementById('reg-phone').value.trim();
    var code = document.getElementById('reg-code').value.trim();
    var pwd = document.getElementById('reg-password').value;
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号'); return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码'); return;
    }
    if(!pwd || pwd.length < 6){
        showToast('密码至少6位'); return;
    }
    
    fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code, password: pwd})
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
        if(data.code === 200){
            currentUser = data.user;
            localStorage.setItem('xjsm_user', JSON.stringify(currentUser));
            updateUserBar();
            closeAuth();
            showToast('注册成功');
        } else {
            showToast(data.msg || '注册失败');
        }
    })
    .catch(function(err){
        console.error('注册失败：', err);
        showToast('网络错误');
    });
}

// ===== 忘记密码 =====
function doForgotPwd(){
    var phone = document.getElementById('forgot-phone').value.trim();
    var code = document.getElementById('forgot-code').value.trim();
    var pwd = document.getElementById('forgot-password').value;
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号'); return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码'); return;
    }
    if(!pwd || pwd.length < 6){
        showToast('密码至少6位'); return;
    }
    
    fetch('http://localhost:5000/api/forgot_password', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code, password: pwd})
    })
    .then(function(r){ return r.json(); })
    .then(function(data){
        if(data.code === 200){
            showToast('密码重置成功，请登录');
            switchAuthTab('code');
        } else {
            showToast(data.msg || '重置失败');
        }
    })
    .catch(function(err){
        console.error('重置失败：', err);
        showToast('网络错误');
    });
}

// ===== 打开用户中心 =====
function openUserCenter(){
    console.log('openUserCenter called');
    if(!currentUser){
        openAuth();
        return;
    }
    
    document.getElementById('uc-name').textContent = currentUser.name;
    document.getElementById('uc-phone').textContent = currentUser.phone.substring(0,3) + '****' + currentUser.phone.substring(7);
    document.getElementById('uc-free').textContent = currentUser.free_count || 3;
    document.getElementById('uc-avatar').textContent = currentUser.avatar || '👤';
    
    document.getElementById('uc-page').classList.add('active');
    document.body.style.overflow = 'hidden';
}

// ===== 关闭用户中心 =====
function closeUserCenter(){
    document.getElementById('uc-page').classList.remove('active');
    document.body.style.overflow = '';
}

// ===== 退出登录 =====
function doLogout(){
    currentUser = null;
    localStorage.removeItem('xjsm_user');
    updateUserBar();
    closeUserCenter();
    showToast('已退出登录');
}

// ===== Toast =====
function showToast(msg){
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.style.display = 'block';
    setTimeout(function(){ t.style.display = 'none'; }, 2000);
}
</script>
</body>
</html>"""

with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done! File size:', round(len(html)/1024, 1), 'KB')
print('\n✅ 修复完成：')
print('1. 电量实时更新 - 每10秒自动变化（模拟真实电量消耗）')
print('2. "更多"按钮跳转 - 点击跳转到新的"更多服务"页面')
print('3. 更多服务页面 - 添加了16个功能模块：')
print('   - 八字排盘、紫微斗数、塔罗占卜、易经占卦')
print('   - 姻缘测算、财运分析、风水布局、黄道吉日')
print('   - 姓名测试、面相分析、手相解读、星座配对')
print('   - 周公解梦、抽签问卦、贵人方位、桃花运测算')
print('\n📱 底部标签栏已更新：首页 | 生肖 | 更多 | 占卜 | 我的')
