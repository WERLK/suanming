#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成正确的 index.html，确保 checkLogin() 能正常跳转
"""
html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover">
<title>玄机算命网 - 专业命理测算平台</title>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a1a2e">
<style>
{*}{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;overflow:hidden;width:100vw;height:100vh;}
.phone{width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;background:linear-gradient(135deg,#0a0a0a 0%,#1a1a2e 50%,#0a0a0a 100%);}
.app{width:100%;max-width:420px;height:100vh;display:flex;flex-direction:column;background:linear-gradient(180deg,#0f0c29 0%,#1a1a2e 30%,#16213e 70%,#0a0a1a 100%);position:relative;overflow:hidden;box-shadow:0 0 80px rgba(255,215,0,0.1);}
.status{display:flex;justify-content:space-between;align-items:center;padding:0.2rem 1rem;background:rgba(0,0,0,0.7);font-size:0.7rem;color:#fff;flex-shrink:0;height:26px;z-index:1000;}
.status .t{font-weight:700;font-size:0.8rem;}
.sig{display:flex;align-items:flex-end;gap:1.5px;height:12px;margin-right:3px;}
.sig i{display:block;width:2.5px;background:#4cd964;border-radius:1px;transition:all 0.3s;}
.sig i:nth-child(1){height:3.5px;}.sig i:nth-child(2){height:5.5px;}.sig i:nth-child(3){height:7.5px;}.sig i:nth-child(4){height:10px;}
.sig i.w{background:#ff3b30;}.sig i.m{background:#ffcc00;}.sig i.o{background:rgba(255,255,255,0.2);}
.bat{display:flex;align-items:center;gap:3px;margin-left:3px;}
.bat-b{width:20px;height:10px;border:1.5px solid #fff;border-radius:2px;position:relative;display:flex;align-items:center;padding:1.5px;}
.bat-b:after{content:'';position:absolute;right:-3px;top:2.5px;width:1.5px;height:4px;background:#fff;border-radius:0 1px 1px 0;}
.bat-f{height:100%;border-radius:1px;background:#4cd964;transition:all 0.5s;}
.bat-f.lo{background:#ff3b30;}.bat-f.mi{background:#ffcc00;}
.bat-t{font-size:0.58rem;min-width:23px;text-align:right;}
.hdr{text-align:center;padding:0.65rem 1rem 0.45rem;background:linear-gradient(180deg,rgba(0,0,0,0.75),transparent);border-bottom:1px solid rgba(255,215,0,0.12);flex-shrink:0;}
.hdr h1{font-size:1.2rem;font-weight:800;background:linear-gradient(90deg,#ffd700,#ff6b35,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:2.5px;}
.hdr .sub{font-size:0.62rem;color:rgba(255,255,255,0.4);margin-top:2px;letter-spacing:1px;}
.sta{display:flex;justify-content:center;align-items:center;gap:0.6rem;padding:0.25rem 1rem;font-size:0.63rem;color:rgba(255,255,255,0.52);background:rgba(255,215,0,0.04);flex-shrink:0;}
.sta .d{width:5px;height:5px;border-radius:50%;background:#4cd964;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.45;}}
.not{display:flex;align-items:center;gap:0.35rem;padding:0.25rem 1rem;font-size:0.62rem;color:#ffd700;background:rgba(255,215,0,0.06);overflow:hidden;flex-shrink:0;border-bottom:1px solid rgba(255,215,0,0.05);}
.not span{white-space:nowrap;animation:scr 25s linear infinite;}
@keyframes scr{0%{transform:translateX(100%);}100%{transform:translateX(-100%);}}
.views{position:relative;flex:1;overflow:hidden;}
.page{position:absolute;top:0;left:0;width:100%;height:100%;overflow-y:auto;display:none;flex-direction:column;-webkit-overflow-scrolling:touch;}
.page.active{display:flex;}
.page::-webkit-scrollbar{display:none;}
.sch{padding:0.5rem 1rem;flex-shrink:0;}
.sch-i{display:flex;align-items:center;gap:0.5rem;background:rgba(255,255,255,0.06);border-radius:20px;padding:0.5rem 1rem;font-size:0.75rem;color:rgba(255,255,255,0.35);border:1px solid rgba(255,255,255,0.04);}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.5rem;padding:0.45rem 1rem;flex-shrink:0;}
.item{display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015));border-radius:12px;padding:0.6rem 0.1rem;gap:0.28rem;cursor:pointer;border:1px solid rgba(255,215,0,0.06);transition:all 0.15s;position:relative;overflow:hidden;}
.item:before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,215,0,0.22),transparent);}
.item:active{transform:scale(0.93);background:rgba(255,215,0,0.1);}
.item .ic{font-size:1.45rem;}
.item .lb{font-size:0.6rem;color:rgba(255,255,255,0.78);text-align:center;line-height:1.2;font-weight:500;}
.sec{padding:0.7rem 1rem 0.35rem;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.sec h3{font-size:0.85rem;color:#ffd700;font-weight:700;display:flex;align-items:center;gap:0.3rem;}
.sec h3:before{content:'';display:inline-block;width:2.5px;height:12px;background:linear-gradient(180deg,#ffd700,#ff6b35);border-radius:2px;}
.sec .mo{font-size:0.65rem;color:rgba(255,255,255,0.35);}
.card{margin:0.45rem 1rem;padding:0.8rem;background:linear-gradient(135deg,rgba(255,215,0,0.09),rgba(255,107,53,0.05));border-radius:12px;border:1px solid rgba(255,215,0,0.13);flex-shrink:0;}
.card h4{font-size:0.8rem;color:#ffd700;margin-bottom:0.45rem;}
.card p{font-size:0.7rem;color:rgba(255,255,255,0.62);line-height:1.7;}
.kb-l{padding:0.45rem 1rem;flex-shrink:0;}
.kb{background:rgba(255,255,255,0.035);border-radius:12px;margin-bottom:0.5rem;overflow:hidden;border:1px solid rgba(255,255,255,0.045);}
.kb-h{display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem;cursor:pointer;}
.kb-t{font-size:0.78rem;color:rgba(255,255,255,0.85);font-weight:600;}
.kb-ar{font-size:0.63rem;color:rgba(255,255,255,0.33);transition:transform 0.3s;}
.kb.x .kb-ar{transform:rotate(180deg);}
.kb-b{max-height:0;overflow:hidden;transition:max-height 0.35s ease,padding 0.3s;padding:0 1rem;}
.kb.x .kb-b{max-height:550px;padding:0 1rem 0.8rem;}
.kb-c{font-size:0.7rem;color:rgba(255,255,255,0.56);line-height:1.75;}
.kb-c p{margin-bottom:0.4rem;}
.tag{display:inline-block;padding:2px 6px;background:rgba(255,215,0,0.07);color:#ffd700;border-radius:5px;font-size:0.56rem;margin:2px 2px 2px 0;}
hr{height:1px;background:rgba(255,255,255,0.045);margin:0.2rem 1rem;border:none;flex-shrink:0;}
.zg{display:grid;grid-template-columns:repeat(4,1fr);gap:0.5rem;padding:0.45rem 1rem;}
.zi{display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(255,255,255,0.045);border-radius:12px;padding:0.7rem 0.15rem;gap:0.22rem;cursor:pointer;border:1px solid rgba(255,215,0,0.06);transition:all 0.15s;}
.zi:active{transform:scale(0.93);background:rgba(255,215,0,0.1);}
.zi .em{font-size:1.6rem;}
.zi .nm{font-size:0.68rem;color:rgba(255,255,255,0.78);font-weight:600;}
.zi .rk{font-size:0.56rem;color:rgba(255,255,255,0.38);}
.dl{padding:0.45rem 1rem;}
.di{display:flex;align-items:center;gap:0.7rem;padding:0.8rem;margin-bottom:0.5rem;background:rgba(255,255,255,0.045);border-radius:12px;border:1px solid rgba(255,255,255,0.045);cursor:pointer;transition:all 0.15s;}
.di:active{background:rgba(255,215,0,0.07);transform:scale(0.975);}
.di .ic{font-size:1.8rem;}
.di .in{flex:1;}
.di .nm{font-size:0.8rem;color:rgba(255,255,255,0.86);font-weight:600;}
.di .ds{font-size:0.65rem;color:rgba(255,255,255,0.46);margin-top:3px;}
.di .ar{color:rgba(255,255,255,0.26);font-size:0.73rem;}
.ft{display:flex;justify-content:space-around;align-items:center;padding:0.3rem 0.5rem 0.45rem;flex-shrink:0;background:rgba(0,0,0,0.88);backdrop-filter:blur(30px);border-top:1px solid rgba(255,255,255,0.08);z-index:1000;}
.ft .t{display:flex;flex-direction:column;align-items:center;gap:0.1rem;color:rgba(255,255,255,0.3);font-size:0.54rem;cursor:pointer;padding:0.2rem 0.7rem;border-radius:8px;transition:all 0.15s;flex:1;text-align:center;}
.ft .t .ti{font-size:1.15rem;transition:all 0.15s;}
.ft .t.a{color:#ffd700;}
.ft .t.a .ti{transform:scale(1.06);}
.ft .t:active{background:rgba(255,215,0,0.08);}
.auth-page{position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(180deg,#0f0c29 0%,#1a1a2e 50%,#0a0a1a 100%);display:none;flex-direction:column;padding:2rem 1.5rem;z-index:2000;overflow-y:auto;}
.auth-page.active{display:flex;}
.auth-page::-webkit-scrollbar{display:none;}
.auth-back{position:absolute;top:1rem;left:1rem;font-size:1.3rem;color:rgba(255,255,255,0.5);cursor:pointer;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;}
.auth-back:active{background:rgba(255,255,255,0.1);}
.auth-logo{text-align:center;margin-bottom:2rem;margin-top:2rem;}
.auth-logo h2{font-size:1.8rem;font-weight:800;background:linear-gradient(90deg,#ffd700,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:3px;}
.auth-logo p{font-size:0.7rem;color:rgba(255,255,255,0.45);margin-top:0.5rem;}
.auth-tabs{display:flex;gap:0;margin-bottom:1.5rem;border-bottom:1px solid rgba(255,255,255,0.1);}
.auth-tab{flex:1;text-align:center;padding:0.6rem;font-size:0.85rem;color:rgba(255,255,255,0.4);cursor:pointer;transition:all 0.2s;border-bottom:2px solid transparent;}
.auth-tab.a{color:#ffd700;border-bottom-color:#ffd700;font-weight:600;}
.auth-form{display:flex;flex-direction:column;gap:1rem;}
.auth-input{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.8rem 1rem;color:#fff;font-size:0.85rem;outline:none;transition:all 0.2s;}
.auth-input:focus{border-color:rgba(255,215,0,0.5);background:rgba(255,255,255,0.1);}
.auth-input::placeholder{color:rgba(255,255,255,0.35);}
.auth-code{display:flex;gap:0.5rem;}
.auth-code .auth-input{flex:1;}
.auth-code-btn{background:rgba(255,215,0,0.15);border:1px solid rgba(255,215,0,0.3);border-radius:12px;padding:0.8rem 1rem;color:#ffd700;font-size:0.75rem;cursor:pointer;white-space:nowrap;transition:all 0.2s;font-weight:500;}
.auth-code-btn:active{background:rgba(255,215,0,0.25);}
.auth-code-btn:disabled{opacity:0.5;cursor:not-allowed;}
.auth-btn{background:linear-gradient(135deg,#ffd700,#ff6b35);border:none;border-radius:12px;padding:0.85rem;color:#000;font-size:0.9rem;font-weight:700;cursor:pointer;transition:all 0.2s;margin-top:0.5rem;}
.auth-btn:active{transform:scale(0.97);opacity:0.9;}
.auth-btn:disabled{opacity:0.5;cursor:not-allowed;}
.auth-switch{text-align:center;margin-top:1.5rem;font-size:0.75rem;color:rgba(255,255,255,0.5);}
.auth-switch a{color:#ffd700;text-decoration:none;font-weight:600;}
.auth-divider{display:flex;align-items:center;gap:1rem;margin:1.5rem 0;font-size:0.7rem;color:rgba(255,255,255,0.3);}
.auth-divider:before,.auth-divider:after{content:'';flex:1;height:1px;background:rgba(255,255,255,0.1);}
.auth-third{display:flex;justify-content:center;gap:1.5rem;margin-top:1rem;}
.auth-third-btn{width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;font-size:1.5rem;cursor:pointer;transition:all 0.2s;border:1px solid rgba(255,255,255,0.1);}
.auth-third-btn:active{transform:scale(0.93);background:rgba(255,255,255,0.12);}
.toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.92);color:#fff;padding:0.7rem 1.3rem;border-radius:10px;font-size:0.82rem;z-index:99999;pointer-events:none;animation:tin 0.25s ease;}
@keyframes tin{from{opacity:0;transform:translate(-50%,-50%) scale(0.9);}to{opacity:1;transform:translate(-50%,-50%) scale(1);}}
.fort{margin:0.5rem 1rem;padding:0.8rem;background:linear-gradient(135deg,rgba(255,215,0,0.08),rgba(255,107,53,0.05));border-radius:12px;border:1px solid rgba(255,215,0,0.12);flex-shrink:0;}
.fort h4{font-size:0.82rem;color:#ffd700;margin-bottom:0.5rem;}
.fr{display:flex;justify-content:space-between;align-items:center;padding:0.45rem 0;border-bottom:1px solid rgba(255,255,255,0.04);}
.fr:last-child{border-bottom:none;}
.fl{font-size:0.72rem;color:rgba(255,255,255,0.58);}
.fb{flex:1;height:5px;background:rgba(255,255,255,0.07);border-radius:2.5px;margin:0 0.6rem;overflow:hidden;}
.fb-f{height:100%;border-radius:2.5px;transition:width 1s ease;}
.fv{font-size:0.68rem;font-weight:600;min-width:32px;text-align:right;}
.user-bar{display:flex;align-items:center;gap:0.8rem;padding:0.8rem 1rem;background:rgba(255,215,0,0.06);border-radius:12px;margin:0.5rem 1rem;flex-shrink:0;cursor:pointer;border:1px solid rgba(255,215,0,0.1);}
.user-avatar{width:45px;height:45px;border-radius:50%;background:linear-gradient(135deg,#ffd700,#ff6b35);display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0;}
.user-info{flex:1;}
.user-name{font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.9);}
.user-desc{font-size:0.65rem;color:rgba(255,255,255,0.45);margin-top:3px;}
.user-arrow{color:rgba(255,255,255,0.3);font-size:0.8rem;}
</style>
</head>
<body>
<div class="phone">
<div class="app">
  <!-- iOS状态栏（更真实）-->
  <div class="status">
    <div style="display:flex;align-items:center;gap:4px;">
      <span id="carrier">中国移动</span>
      <span style="font-size:0.55rem;opacity:0.5;">|</span>
      <span id="nt" style="font-size:0.6rem;opacity:0.63;">4G</span>
    </div>
    <span class="t" id="clk">12:23</span>
    <div style="display:flex;align-items:center;gap:3px;">
      <div style="display:flex;align-items:flex-end;gap:1px;height:12px;padding-bottom:1px;">
        <div style="width:13px;height:8px;background:rgba(255,255,255,0.9);border-radius:1px;font-size:0.45rem;display:flex;align-items:flex-end;justify-content:center;padding-bottom:1px;">Wi-Fi</div>
      </div>
      <div class="sig" id="sig"><i></i><i></i><i></i><i></i></div>
      <div class="bat">
        <div class="bat-b"><div class="bat-f" id="bf" style="width:78%;"></div></div>
        <span class="bat-t" id="bt">78%</span>
      </div>
    </div>
  </div>
  
  <!-- 顶部标题栏 -->
  <div class="hdr">
    <h1>玄机算命网</h1>
    <div class="sub">测命理 · 知天命 · 改运势 · 掌人生</div>
  </div>
  
  <!-- 在线统计 -->
  <div class="sta">
    <div class="d"></div>
    <span>在线 <strong id="oc" style="color:#ffd700;font-weight:700;">16,847</strong> 人</span>
    <span style="margin-left:auto;font-size:0.6rem;opacity:0.33;">今日测算 58,369次</span>
  </div>
  
  <!-- 公告 -->
  <div class="not"><span>📢</span><span>新用户注册送3次免费测算 · 关注公众号【玄机算命】领688积分 · 大师一对一在线解读 · 每日签到送VIP</span></div>
  
  <!-- 页面容器 -->
  <div class="views">
    <!-- 首页 -->
    <div class="page active" id="p-home">
      <div class="sch"><div class="sch-i" onclick="showToast('搜索功能开发中')">🔍 搜索算命、八字、风水、生肖...</div></div>
      
      <!-- 用户信息栏 -->
      <div class="user-bar" onclick="checkLogin()">
        <div class="user-avatar">👤</div>
        <div class="user-info">
          <div class="user-name" id="user-name-display">点击登录/注册</div>
          <div class="user-desc" id="user-desc-display">登录后享受更多免费测算次数</div>
        </div>
        <span class="user-arrow">›</span>
      </div>
      
      <!-- 热门测算 -->
      <div class="sec"><h3>🔥 热门测算</h3><span class="mo">全部 ></span></div>
      <div class="grid">
        <div class="item" onclick="openM('八字算命')"><span class="ic">📊</span><span class="lb">八字算命</span></div>
        <div class="item" onclick="openM('紫微斗数')"><span class="ic">⭐</span><span class="lb">紫微斗数</span></div>
        <div class="item" onclick="openM('塔罗牌')"><span class="ic">🀄</span><span class="lb">塔罗牌</span></div>
        <div class="item" onclick="openM('易经占卜')"><span class="ic">☯</span><span class="lb">易经占卜</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('姓名测试')"><span class="ic">📝</span><span class="lb">姓名测试</span></div>
        <div class="item" onclick="openM('风水布局')"><span class="ic">🏠</span><span class="lb">风水布局</span></div>
        <div class="item" onclick="openM('面相分析')"><span class="ic">👤</span><span class="lb">面相分析</span></div>
        <div class="item" onclick="openM('手相解读')"><span class="ic">✋</span><span class="lb">手相解读</span></div>
      </div>
      
      <hr>
      
      <!-- 今日运势 -->
      <div class="sec"><h3>📅 今日运势播报</h3><span class="mo">详情 ></span></div>
      <div class="fort">
        <h4>📅 今日综合运势</h4>
        <div class="fr"><span class="fl">综合运势</span><div class="fb"><div class="fb-f" style="width:82%;background:linear-gradient(90deg,#4cd964,#30d158);"></div></div><span class="fv" style="color:#4cd964;">82</span></div>
        <div class="fr"><span class="fl">爱情运势</span><div class="fb"><div class="fb-f" style="width:75%;background:linear-gradient(90deg,#ff6b35,#ffd700);"></div></div><span class="fv" style="color:#ff6b35;">75</span></div>
        <div class="fr"><span class="fl">事业运势</span><div class="fb"><div class="fb-f" style="width:88%;background:linear-gradient(90deg,#30d1ff,#5856d6);"></div></div><span class="fv" style="color:#30d1ff;">88</span></div>
        <div class="fr"><span class="fl">财运指数</span><div class="fb"><div class="fb-f" style="width:70%;background:linear-gradient(90deg,#ffd700,#ff6b35);"></div></div><span class="fv" style="color:#ffd700;">70</span></div>
        <div class="fr"><span class="fl">健康指数</span><div class="fb"><div class="fb-f" style="width:90%;background:linear-gradient(90deg,#4cd964,#30d158);"></div></div><span class="fv" style="color:#4cd964;">90</span></div>
        <div style="margin-top:0.5rem;font-size:0.65rem;color:rgba(255,255,255,0.5);line-height:1.6;">✅ 宜：签约 出行 求财 拜访贵人<br>⚠️ 忌：争吵 高风险投资 远行</div>
      </div>
      
      <hr>
      
      <!-- 更多功能 -->
      <div class="sec"><h3>📌 更多功能</h3><span class="mo">全部 ></span></div>
      <div class="grid">
        <div class="item" onclick="openM('爱情配对')"><span class="ic">💕</span><span class="lb">爱情配对</span></div>
        <div class="item" onclick="openM('财运分析')"><span class="ic">💰</span><span class="lb">财运分析</span></div>
        <div class="item" onclick="openM('健康运势')"><span class="ic">❤️</span><span class="lb">健康运势</span></div>
        <div class="item" onclick="openM('周公解梦')"><span class="ic">🌙</span><span class="lb">周公解梦</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('生肖运势')"><span class="ic">🐉</span><span class="lb">生肖运势</span></div>
        <div class="item" onclick="openM('八字合婚')"><span class="ic">💑</span><span class="lb">八字合婚</span></div>
        <div class="item" onclick="openM('抉择占卜')"><span class="ic">🤔</span><span class="lb">抉择占卜</span></div>
        <div class="item" onclick="openM('黄历查询')"><span class="ic">📅</span><span class="lb">黄历查询</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('AI智能算命')"><span class="ic">🤖</span><span class="lb">AI智能算命</span></div>
        <div class="item" onclick="openM('星座运势')"><span class="ic">🌟</span><span class="lb">星座运势</span></div>
        <div class="item" onclick="openM('数字命理')"><span class="ic">🔢</span><span class="lb">数字命理</span></div>
        <div class="item" onclick="openM('事业运势')"><span class="ic">💼</span><span class="lb">事业运势</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('子女缘分')"><span class="ic">👶</span><span class="lb">子女缘分</span></div>
        <div class="item" onclick="openM('家居风水')"><span class="ic">🏡</span><span class="lb">家居风水</span></div>
        <div class="item" onclick="openM('今日运势')"><span class="ic">📆</span><span class="lb">今日运势</span></div>
        <div class="item" onclick="openM('六爻占卜')"><span class="ic">🎲</span><span class="lb">六爻占卜</span></div>
      </div>
      
      <hr>
      
      <!-- 高阶占卜 -->
      <div class="sec"><h3>🎯 高阶占卜</h3><span class="mo">全部 ></span></div>
      <div class="grid">
        <div class="item" onclick="openM('奇门遁甲')"><span class="ic">🌀</span><span class="lb">奇门遁甲</span></div>
        <div class="item" onclick="openM('大六壬')"><span class="ic">🌊</span><span class="lb">大六壬</span></div>
        <div class="item" onclick="openM('梅花易数')"><span class="ic">🌸</span><span class="lb">梅花易数</span></div>
        <div class="item" onclick="openM('小六壬')"><span class="ic">🎋</span><span class="lb">小六壬</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('财神方位')"><span class="ic">🙏</span><span class="lb">财神方位</span></div>
        <div class="item" onclick="openM('韦特塔罗')"><span class="ic">🃏</span><span class="lb">韦特塔罗</span></div>
        <div class="item" onclick="openM('农历转换')"><span class="ic">📆</span><span class="lb">农历转换</span></div>
        <div class="item" onclick="openM('择日吉凶')"><span class="ic">📿</span><span class="lb">择日吉凶</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('太乙神数')"><span class="ic">🔮</span><span class="lb">太乙神数</span></div>
        <div class="item" onclick="openM('铁板神数')"><span class="ic">📯</span><span class="lb">铁板神数</span></div>
        <div class="item" onclick="openM('皇极经世')"><span class="ic">📜</span><span class="lb">皇极经世</span></div>
        <div class="item" onclick="openM('河洛理数')"><span class="ic">🌊</span><span class="lb">河洛理数</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openM('称骨算命')"><span class="ic">⚖️</span><span class="lb">称骨算命</span></div>
        <div class="item" onclick="openM('三世书')"><span class="ic">📖</span><span class="lb">三世书</span></div>
        <div class="item" onclick="openM('九星玄空')"><span class="ic">✨</span><span class="lb">九星玄空</span></div>
        <div class="item" onclick="openM('白鹤神数')"><span class="ic">🦢</span><span class="lb">白鹤神数</span></div>
      </div>
      
      <hr>
      
      <!-- 更多分类 -->
      <div class="sec"><h3>🎨 更多分类</h3><span class="mo">全部 ></span></div>
      <div class="grid">
        <div class="item" onclick="openM('八字排盘')"><span class="ic">📋</span><span class="lb">八字排盘</span></div>
        <div class="item" onclick="openM('紫微排盘')"><span class="ic">🔯</span><span class="lb">紫微排盘</span></div>
        <div class="item" onclick="openM('流年运势')"><span class="ic">📈</span><span class="lb">流年运势</span></div>
        <div class="item" onclick="openM('婚姻配对')"><span class="ic">💒</span><span class="lb">婚姻配对</span></div>
      </div>
      
      <div style="padding:1.5rem 1rem;text-align:center;color:rgba(255,255,255,0.3);font-size:0.65rem;">
        <p>🌟 玄机算命网 · 专业命理测算平台</p>
        <p style="margin-top:0.3rem;">联系客服 · 意见反馈 · 关于我们</p>
      </div>
    </div>    
    <!-- 生肖页面 -->
    <div class="page" id="p-zod">
      <div class="sch"><div class="sch-i" onclick="showToast('搜索生肖')">🔍 搜索你的生肖...</div></div>
      <div class="sec"><h3>🐉 十二生肖运势</h3></div>
      <div class="zg">
        <div class="zi" onclick="showToast('鼠-开发中')"><span class="em">🐭</span><span class="nm">鼠</span><span class="rk">第一名</span></div>
        <div class="zi" onclick="showToast('牛-开发中')"><span class="em">🐮</span><span class="nm">牛</span><span class="rk">第二名</span></div>
        <div class="zi" onclick="showToast('虎-开发中')"><span class="em">🐯</span><span class="nm">虎</span><span class="rk">第三名</span></div>
        <div class="zi" onclick="showToast('兔-开发中')"><span class="em">🐰</span><span class="nm">兔</span><span class="rk">第四名</span></div>
        <div class="zi" onclick="showToast('龙-开发中')"><span class="em">🐲</span><span class="nm">龙</span><span class="rk">第五名</span></div>
        <div class="zi" onclick="showToast('蛇-开发中')"><span class="em">🐍</span><span class="nm">蛇</span><span class="rk">第六名</span></div>
        <div class="zi" onclick="showToast('马-开发中')"><span class="em">🐴</span><span class="nm">马</span><span class="rk">第七名</span></div>
        <div class="zi" onclick="showToast('羊-开发中')"><span class="em">🐑</span><span class="nm">羊</span><span class="rk">第八名</span></div>
        <div class="zi" onclick="showToast('猴-开发中')"><span class="em">🐵</span><span class="nm">猴</span><span class="rk">第九名</span></div>
        <div class="zi" onclick="showToast('鸡-开发中')"><span class="em">🐔</span><span class="nm">鸡</span><span class="rk">第十名</span></div>
        <div class="zi" onclick="showToast('狗-开发中')"><span class="em">🐶</span><span class="nm">狗</span><span class="rk">第十一名</span></div>
        <div class="zi" onclick="showToast('猪-开发中')"><span class="em">🐷</span><span class="nm">猪</span><span class="rk">第十二名</span></div>
      </div>
      <div style="padding:0.8rem;font-size:0.72rem;color:rgba(255,255,255,0.55);line-height:1.8;">
        <div style="background:rgba(255,215,0,0.07);border-radius:10px;padding:0.7rem;">
          <strong style="color:#ffd700;">📅 本周生肖运势排行</strong><br>
          🥇 龙：贵人运强，事业有突破<br>
          🥈 鼠：财运亨通，适合投资理财<br>
          🥉 蛇：桃花运旺，感情有进展<br>
          4️⃣ 牛：健康运佳，注意休息<br>
          5️⃣ 兔：学业运好，考试顺利
        </div>
      </div>
    </div>    
    <!-- 占卜页面 -->
    <div class="page" id="p-div">
      <div class="sch"><div class="sch-i" onclick="showToast('搜索占卜')">🔍 搜索占卜方式...</div></div>
      <div class="sec"><h3>🔮 选择占卜方式</h3></div>
      <div class="dl">
        <div class="di" onclick="openM('塔罗牌')"><span class="ic">🀄</span><div class="in"><div class="nm">塔罗牌占卜</div><div class="ds">78张牌解读命运奥秘 · 爱情/事业/运势</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('易经占卜')"><span class="ic">☯</span><div class="in"><div class="nm">易经六十四卦</div><div class="ds">群经之首 · 阴阳变化 · 决策参考</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('六爻占卜')"><span class="ic">🎲</span><div class="in"><div class="nm">六爻占卜</div><div class="ds">三钱起卦 · 六亲配六神 · 预测吉凶</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('梅花易数')"><span class="ic">🌸</span><div class="in"><div class="nm">梅花易数</div><div class="ds">宋代邵雍创立 · 数字/时间/方位起卦</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('奇门遁甲')"><span class="ic">🌀</span><div class="in"><div class="nm">奇门遁甲</div><div class="ds">帝王之术 · 择吉/风水/决策</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('大六壬')"><span class="ic">🌊</span><div class="in"><div class="nm">大六壬占卜</div><div class="ds">三式之一 · 以月将加时起课</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('韦特塔罗')"><span class="ic">🃏</span><div class="in"><div class="nm">韦特塔罗牌</div><div class="ds">最流行的塔罗体系 · 22张大阿卡纳</div></div><span class="ar">›</span></div>
        <div class="di" onclick="openM('小六壬')"><span class="ic">🎋</span><div class="in"><div class="nm">小六壬速断</div><div class="ds">左手掐指一算 · 快速简便</div></div><span class="ar">›</span></div>
      </div>
    </div>    
    <!-- 知识库页面 -->
    <div class="page" id="p-kb">
      <div class="sch"><div class="sch-i" onclick="showToast('搜索知识')">🔍 搜索命理知识...</div></div>
      <div class="sec"><h3>📚 命理知识库</h3><span class="mo">共128篇文章</span></div>
      <div class="kb-l">
        <div class="kb" onclick="this.classList.toggle('x')">
          <div class="kb-h"><span class="kb-t">📚 八字命理大全</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p><strong style="color:#ffd700;">一、什么是八字</strong></p><p>八字，即生辰八字，是一个人出生时的干支历日期。年干和年支组成年柱，月干和月支组成月柱，日干和日支组成日柱，时干和时支组成时柱；一共四柱，四个干和四个支共八个字，故称八字，亦称四柱。</p><p><strong style="color:#ffd700;">二、天干地支</strong></p><p>十天干：甲(ji·)、乙(yǐ)、丙(bǐng)、丁(dīng)、戊(wù)、己(jǐ)、庚(gēng)、辛(xīn)、壬(rén)、癸(guǐ)</p><p>十二地支：子(zǐ)、丑(chǒu)、寅(yín)、卯(mǎo)、辰(chén)、巳(sì)、午(wǔ)、未(wèi)、申(shēn)、酉(yǒu)、戌(xū)、亥(hài)</p><p><strong style="color:#ffd700;">三、五行生克</strong></p><p>五行相生：金生水、水生木、木生火、火生土、土生金。相生代表生发、促进、助长。</p><p>五行相克：金克木、木克土、土克水、水克火、火克金。相克代表制约、克制、战胜。</p><p><strong style="color:#ffd700;">四、十神关系</strong></p><p>以日干为中心，与其他天干地支的生克关系定出：比肩、劫财、食神、伤官、正财、偏财、正官、七杀、正印、偏印，称为十神。</p><span class="tag">基础</span><span class="tag">八字</span><span class="tag">必读</span></div></div>
        </div>
        <div class="kb" onclick="this.classList.toggle('x')">
          <div class="kb-h"><span class="kb-t">⭐ 紫微斗数详解</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p>紫微斗数，是中国传统命理学的重要支派，以星宿配合十二宫的术数算命方法。</p><p><strong style="color:#ffd700;">十四主星详解：</strong></p><p>北斗七星：紫微（帝星·领导才能）、天机（谋臣·智慧策略）、太阳（光明·热情大方）、武曲（财星·坚毅果断）、天同（福星·温和体贴）、廉贞（囚星·廉洁忠诚）、天府（禄库·稳重保守）</p><p>南斗七星：太阴（月亮·温柔内敛）、贪狼（桃花·多才多艺）、巨门（暗星·口才思辨）、天相（印星·端庄稳重）、天梁（寿星·慈悲为怀）、七杀（将星·勇猛果断）、破军（耗星·开创变革）</p><p><strong style="color:#ffd700;">十二宫位：</strong>命宫、兄弟、夫妻、子女、财帛、疾厄、迁移、交友、官禄、田宅、福德、父母</p><span class="tag">紫微斗数</span><span class="tag">星曜</span><span class="tag">十二宫</span></div></div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 底部标签栏 -->
  <div class="ft">
    <div class="t a" onclick="switchTab('home',this)"><span class="ti">🏠</span>首页</div>
    <div class="t" onclick="switchTab('zod',this)"><span class="ti">🐉</span>生肖</div>
    <div class="t" onclick="switchTab('div',this)"><span class="ti">🔮</span>占卜</div>
    <div class="t" onclick="checkLogin()"><span class="ti">👤</span>我的</div>
  </div>
</div>
</div>

<!-- 登录/注册页面 -->
<div class="auth-page" id="auth-page">
  <div class="auth-back" onclick="closeAuth()">‹</div>
  <div class="auth-logo">
    <h2>玄机算命网</h2>
    <p id="auth-subtitle">登录后享受更多免费测算</p>
  </div>
  
  <!-- 登录/注册标签切换 -->
  <div class="auth-tabs">
    <div class="auth-tab a" id="tab-code-login" onclick="switchAuthTab('code-login')">验证码登录</div>
    <div class="auth-tab" id="tab-pwd-login" onclick="switchAuthTab('pwd-login')">密码登录</div>
    <div class="auth-tab" id="tab-register" onclick="switchAuthTab('register')">注册</div>
  </div>
  
  <!-- 验证码登录表单 -->
  <div id="form-code-login" class="auth-form">
    <input type="tel" class="auth-input" placeholder="请输入手机号" id="login-phone" maxlength="11">
    <div class="auth-code">
      <input type="text" class="auth-input" placeholder="请输入验证码" id="login-code" maxlength="6">
      <button class="auth-code-btn" id="login-code-btn" onclick="sendCode('login')">获取验证码</button>
    </div>
    <button class="auth-btn" onclick="doLogin()">登 录</button>
  </div>
  
  <!-- 密码登录表单 -->
  <div id="form-pwd-login" class="auth-form" style="display:none;">
    <input type="text" class="auth-input" placeholder="手机号" id="pwd-login-phone" maxlength="11">
    <input type="password" class="auth-input" placeholder="密码" id="pwd-login-pwd">
    <div style="display:flex;justify-content:flex-end;font-size:0.7rem;">
      <a onclick="openForgotPwd()" style="color:#ffd700;cursor:pointer;">忘记密码？</a>
    </div>
    <button class="auth-btn" onclick="doPwdLogin()">登 录</button>
  </div>
  
  <!-- 注册表单 -->
  <div id="form-register" class="auth-form" style="display:none;">
    <input type="tel" class="auth-input" placeholder="请输入手机号" id="reg-phone" maxlength="11">
    <div class="auth-code">
      <input type="text" class="auth-input" placeholder="请输入验证码" id="reg-code" maxlength="6">
      <button class="auth-code-btn" id="reg-code-btn" onclick="sendCode('register')">获取验证码</button>
    </div>
    <input type="password" class="auth-input" placeholder="设置密码（至少6位）" id="reg-pass" minlength="6">
    <input type="password" class="auth-input" placeholder="确认密码" id="reg-pass2">
    <button class="auth-btn" onclick="doRegister()">注 册</button>
  </div>
  
  <div style="text-align:center;font-size:0.65rem;color:rgba(255,255,255,0.35);margin-top:1.5rem;">
    注册即同意 <a style="color:#ffd700;text-decoration:none;">《用户协议》</a> 和 <a style="color:#ffd700;text-decoration:none;">《隐私政策》</a>
  </div>
</div>

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
    想起密码了？<a onclick="switchAuthTab('pwd-login')" style="color:#ffd700;cursor:pointer;">立即登录</a>
  </div>
</div>

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

<script>
// ===== 全局数据 =====
var currentUser = null;
var codeTimer = null;

// ===== 时间更新 =====
function updateClock(){
    var d = new Date();
    var h = d.getHours().toString().padStart(2,'0');
    var m = d.getMinutes().toString().padStart(2,'0');
    document.getElementById('clk').textContent = h + ':' + m;
}
setInterval(updateClock, 1000);
updateClock();

// ===== 电池 =====
var batLevel = 78;
function updateBattery(){
    document.getElementById('bf').style.width = batLevel + '%';
    document.getElementById('bt').textContent = batLevel + '%';
    var f = document.getElementById('bf');
    f.classList.remove('lo','mi');
    if(batLevel <= 20) f.classList.add('lo');
    else if(batLevel <= 50) f.classList.add('mi');
}
if(navigator.getBattery){
    navigator.getBattery().then(function(b){
        batLevel = Math.round(b.level * 100);
        updateBattery();
        b.addEventListener('levelchange', function(){
            batLevel = Math.round(b.level * 100);
            updateBattery();
        });
    });
} else {
    setInterval(function(){
        batLevel = Math.max(15, Math.min(100, batLevel + (Math.random() > 0.5 ? 1 : -1)));
        updateBattery();
    }, 30000);
}
updateBattery();

// ===== 信号 =====
function updateSignal(){
    var bs = document.querySelectorAll('#sig i');
    var r = Math.random();
    bs.forEach(function(b,i){
        b.classList.remove('w','m','o');
        if(r < 0.12 && i > 1) b.classList.add('o');
        else if(r < 0.3 && i > 2) b.classList.add('m');
    });
}
setInterval(updateSignal, 5000);
updateSignal();

// ===== 在线人数 =====
function updateOnlineCount(){
    document.getElementById('oc').textContent = (16000 + Math.floor(Math.random() * 2000)).toLocaleString();
}
setInterval(updateOnlineCount, 8000);
updateOnlineCount();

// ===== 页面切换 =====
function switchTab(page, el){
    document.querySelectorAll('.page').forEach(function(x){ x.classList.remove('active'); });
    document.querySelectorAll('.ft .t').forEach(function(x){ x.classList.remove('a'); });
    var pg = document.getElementById('p-' + page);
    if(pg) pg.classList.add('active');
    if(el) el.classList.add('a');
}

// ===== 登录/注册页面 =====
function openAuth(){
    if(currentUser){
        openUserCenter();
        return;
    }
    closeAllAuthPages();
    document.getElementById('auth-page').style.display = 'flex';
    setTimeout(function(){ document.getElementById('auth-page').classList.add('active'); }, 10);
    switchAuthTab('code-login');
}

function closeAuth(){
    document.getElementById('auth-page').classList.remove('active');
    setTimeout(function(){ document.getElementById('auth-page').style.display = 'none'; }, 300);
}

function switchAuthTab(tab){
    document.querySelectorAll('.auth-tab').forEach(function(x){ x.classList.remove('a'); });
    document.getElementById('tab-' + tab).classList.add('a');
    
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

// ===== 找回密码页面 =====
function openForgotPwd(){
    closeAllAuthPages();
    document.getElementById('auth-forgot').style.display = 'flex';
    setTimeout(function(){ document.getElementById('auth-forgot').classList.add('active'); }, 10);
}

function closeForgotPwd(){
    document.getElementById('auth-forgot').classList.remove('active');
    setTimeout(function(){ document.getElementById('auth-forgot').style.display = 'none'; }, 300);
}

// ===== 用户中心页面 =====
function openUserCenter(){
    if(!currentUser){
        openAuth();
        return;
    }
    
    document.getElementById('uc-name').textContent = currentUser.name;
    document.getElementById('uc-phone').textContent = currentUser.phone.substring(0,3) + '****' + currentUser.phone.substring(7);
    document.getElementById('uc-free-count').textContent = currentUser.free_count;
    
    closeAllAuthPages();
    document.getElementById('auth-user-center').style.display = 'flex';
    setTimeout(function(){ document.getElementById('auth-user-center').classList.add('active'); }, 10);
}

function closeUserCenter(){
    document.getElementById('auth-user-center').classList.remove('active');
    setTimeout(function(){ document.getElementById('auth-user-center').style.display = 'none'; }, 300);
}

function closeAllAuthPages(){
    document.querySelectorAll('.auth-page').forEach(function(x){
        x.classList.remove('active');
        setTimeout(function(){ x.style.display = 'none'; }, 300);
    });
}

// ===== 检查登录状态 =====
function checkLogin(){
    if(currentUser){
        openUserCenter();
    } else {
        openAuth();
    }
}

// ===== 发送验证码 =====
function sendCode(type){
    var phoneInput = document.getElementById(type === 'login' ? 'login-phone' : 'reg-phone');
    var phone = phoneInput.value.trim();
    
    if(!phone || phone.length !== 11 || !/^1[3-9]\d{9}$/.test(phone)){
        showToast('请输入正确的手机号');
        return;
    }
    
    var btn = document.getElementById(type + '-code-btn');
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

// ===== 验证码登录 =====
function doLogin(){
    var phone = document.getElementById('login-phone').value.trim();
    var code = document.getElementById('login-code').value.trim();
    
    if(!phone || phone.length !== 11){
        showToast('请输入正确的手机号');
        return;
    }
    if(!code || code.length !== 6){
        showToast('请输入6位验证码');
        return;
    }
    
    showToast('登录中...');
    
    fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code})
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
        console.error('登录失败：', err);
        showToast('网络错误，请重试');
    });
}

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
        console.error('登录失败：', err);
        showToast('网络错误，请重试');
    });
}

// ===== 注册 =====
function doRegister(){
    var phone = document.getElementById('reg-phone').value.trim();
    var code = document.getElementById('reg-code').value.trim();
    var pass = document.getElementById('reg-pass').value;
    var pass2 = document.getElementById('reg-pass2').value;
    
    if(!phone || phone.length !== 11 || !/^1[3-9]\d{9}$/.test(phone)){
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
    
    showToast('注册中...');
    
    fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone: phone, code: code, password: pass})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            currentUser = data.data;
            updateUserUI();
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
}

// ===== 发送找回密码验证码 =====
function sendForgotCode(){
    var phone = document.getElementById('forgot-phone').value.trim();
    
    if(!phone || phone.length !== 11 || !/^1[3-9]\d{9}$/.test(phone)){
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

// ===== 找回密码 =====
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
        body: JSON.stringify({phone: phone, code: code, new_password: newPwd})
    })
    .then(res => res.json())
    .then(data => {
        if(data.code === 200){
            showToast('密码重置成功！请使用新密码登录');
            setTimeout(function(){ switchAuthTab('pwd-login'); }, 1500);
        } else {
            showToast(data.msg || '重置失败');
        }
    })
    .catch(err => {
        console.error('找回密码失败：', err);
        showToast('网络错误，请重试');
    });
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

// ===== 更新用户界面 =====
function updateUserUI(){
    if(currentUser){
        document.getElementById('user-name-display').textContent = currentUser.name;
        document.getElementById('user-desc-display').textContent = '今日剩余免费测算：' + currentUser.free_count + '次';
    }
}

// ===== Toast提示 =====
function showToast(msg){
    var t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function(){ t.remove(); }, 2000);
}

// ===== 模块点击 =====
function openM(name){
    var needLogin = ['八字算命','紫微斗数','塔罗牌','易经占卜','姓名测试','风水布局'];
    if(needLogin.indexOf(name) !== -1 && !currentUser){
        showToast('请先登录后再使用');
        openAuth();
        return;
    }
    showToast(name + ' - 功能开发中，敬请期待...');
}

// ===== 点击背景关闭登录页 =====
document.getElementById('auth-page').addEventListener('click', function(e){
    if(e.target === this) closeAuth();
});
document.getElementById('auth-forgot').addEventListener('click', function(e){
    if(e.target === this) closeForgotPwd();
});
document.getElementById('auth-user-center').addEventListener('click', function(e){
    if(e.target === this) closeUserCenter();
});
</script>
</body>
</html>"""

with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('DONE: index.html written')
print('File size:', len(html), 'bytes')
print('Function modules:', html.count('class="item"'))
print('Pages:', html.count('class="page"'))
