#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成完整的index.html，包含所有功能
"""

html_content = '''<!DOCTYPE html>
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
.back-btn{display:flex;align-items:center;gap:0.5rem;padding:0.5rem 1rem;cursor:pointer;color:rgba(255,255,255,0.5);font-size:0.8rem;flex-shrink:0;}
.back-btn:active{color:#ffd700;}
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
.uc-menu-i .ar{color:rgba(255,255,255,0.3);font-size:0.7rem;}
.vip-page{position:fixed;top:0;left:0;width:100%;height:100%;background:linear-gradient(180deg,#0f0c29,#1a1a2e 50%,#0a0a1a);display:none;flex-direction:column;z-index:9999;overflow-y:auto;}
.vip-page.active{display:flex;}
.vip-hdr{display:flex;justify-content:space-between;align-items:center;padding:1rem;flex-shrink:0;}
.vip-back{font-size:1.3rem;color:rgba(255,255,255,0.5);cursor:pointer;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;}
.vip-title{font-size:1.1rem;color:#fff;font-weight:700;}
.vip-spacer{width:40px;}
.vip-body{padding:1.5rem;flex:1;}
.vip-card{background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,107,53,0.08));border-radius:16px;padding:2rem;margin-bottom:1.5rem;border:2px solid rgba(255,215,0,0.3);text-align:center;position:relative;overflow:hidden;}
.vip-badge{display:inline-block;padding:0.3rem 1rem;background:linear-gradient(90deg,#ffd700,#ff6b35);border-radius:20px;font-size:0.75rem;color:#1a1a2e;font-weight:700;margin-bottom:1rem;}
.vip-name{font-size:1.5rem;color:#ffd700;font-weight:800;margin-bottom:0.5rem;}
.vip-price{font-size:2.5rem;color:#fff;font-weight:800;margin:1rem 0;}
.vip-price span{font-size:1rem;color:rgba(255,255,255,0.5);font-weight:400;}
.vip-features{text-align:left;margin-top:1.5rem;}
.vip-feature{display:flex;align-items:center;gap:0.5rem;padding:0.5rem 0;font-size:0.8rem;color:rgba(255,255,255,0.8);}
.vip-feature .check{color:#ffd700;font-size:1rem;}
.vip-btn{background:linear-gradient(135deg,#ffd700,#ff6b35);color:#1a1a2e;font-size:1rem;font-weight:700;padding:1rem;border:none;border-radius:12px;cursor:pointer;transition:all 0.2s;margin-top:1.5rem;width:100%;}
.vip-btn:active{transform:scale(0.97);}
.vip-options{display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;margin-bottom:1.5rem;}
.vip-option{background:rgba(255,255,255,0.05);border:2px solid rgba(255,255,255,0.1);border-radius:12px;padding:1rem 0.5rem;text-align:center;cursor:pointer;transition:all 0.2s;}
.vip-option.a{border-color:#ffd700;background:rgba(255,215,0,0.1);}
.vip-option .duration{font-size:0.85rem;color:#fff;font-weight:600;margin-bottom:0.3rem;}
.vip-option .price{font-size:1.2rem;color:#ffd700;font-weight:700;}
.vip-option .price span{font-size:0.65rem;color:rgba(255,255,255,0.4);}
.vip-option .save{font-size:0.6rem;color:#ff6b35;margin-top:0.3rem;font-weight:600;}
.vip-pay{display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;margin-bottom:1.5rem;}
.vip-pay-opt{background:rgba(255,255,255,0.05);border:2px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.8rem;display:flex;flex-direction:column;align-items:center;gap:0.3rem;cursor:pointer;transition:all 0.2s;}
.vip-pay-opt.a{border-color:#ffd700;background:rgba(255,215,0,0.1);}
.vip-pay-opt .ic{font-size:1.5rem;}
.vip-pay-opt .lb{font-size:0.65rem;color:rgba(255,255,255,0.6);}
.toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.85);color:#fff;padding:0.8rem 1.5rem;border-radius:10px;font-size:0.85rem;z-index:99999;backdrop-filter:blur(10px);pointer-events:none;opacity:0;transition:opacity 0.3s;white-space:nowrap;}
.toast.show{opacity:1;}
</style>
</head>
<body>

<!-- 手机模拟器 -->
<div class="phone">
  <div class="app" id="app">

    <!-- 状态栏 -->
    <div class="status" id="status-bar">
      <span class="time" id="status-time">00:00</span>
      <span class="center">
        <span id="carrier">中国移动</span>
        <span id="net-type">5G</span>
      </span>
      <span class="icons">
        <span id="signal">📶</span>
        <span id="wifi">📶</span>
        <span id="battery">🔋</span>
        <span id="battery-pct">100%</span>
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
        <div class="user-desc" id="ub-desc">登录</div>
      </div>
    </div>

    <!-- 搜索 -->
    <div class="sch"><div class="sch-i">🔍 搜索你想要的服务</div></div>

    <!-- 首页内容 -->
    <div class="views" id="views">
      <!-- 首页 -->
      <div class="page active" id="page-home">
        <div class="grid">
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">☯️</span>
            <span class="lb">八字排盘</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">🌙</span>
            <span class="lb">紫微斗数</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">🎎</span>
            <span class="lb">生肖运势</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">📅</span>
            <span class="lb">黄道吉日</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">💑</span>
            <span class="lb">姻缘配对</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">🏠</span>
            <span class="lb">风水布局</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">🎓</span>
            <span class="lb">起名改名</span>
          </div>
          <div class="item" onclick="showToast(\'功能开发中...\')">
            <span class="ic">📖</span>
            <span class="lb">周公解梦</span>
          </div>
        </div>

        <div class="sec">
          <h3>热门测算</h3>
          <span class="mo" onclick="switchTab(\'more\',this)">查看更多 ›</span>
        </div>

        <div class="zx-list">
          <div class="zx-item" onclick="showToast(\'功能开发中...\')">
            <span class="zx-icon">☯️</span>
            <div class="zx-info">
              <div class="zx-title">今日财神方位</div>
              <div class="zx-desc">根据八字五行，测算今日财神方位，助您财运亨通</div>
            </div>
            <span class="zx-arrow">›</span>
          </div>
          <div class="zx-item" onclick="showToast(\'功能开发中...\')">
            <span class="zx-icon">🌙</span>
            <div class="zx-info">
              <div class="zx-title">紫微斗数命盘</div>
              <div class="zx-desc">十二宫位详解，人生运势一目了然</div>
            </div>
            <span class="zx-arrow">›</span>
          </div>
        </div>
      </div>

      <!-- 生肖运势 -->
      <div class="page" id="page-shengxiao">
        <div class="back-btn" onclick="switchTab(\'home\',document.querySelectorAll(\'.ft .t\')[0])">
          <span>‹</span>
          <span>返回</span>
        </div>
        <div class="sec">
          <h3>十二生肖运势</h3>
        </div>
        <div class="zb-list">
          <div class="zb-card" onclick="showToast(\'功能开发中...\')">
            <div class="zb-title">🐭 生肖鼠</div>
            <div class="zb-desc">今日运势：财运亨通，事业顺利。桃花运旺盛，单身者有望脱单。</div>
            <span class="zb-tag">财运</span>
            <span class="zb-tag">事业</span>
          </div>
          <div class="zb-card" onclick="showToast(\'功能开发中...\')">
            <div class="zb-title">🐮 生肖牛</div>
            <div class="zb-desc">今日运势：稳中求进，不宜冒进。注意家人健康。</div>
            <span class="zb-tag">健康</span>
            <span class="zb-tag">家庭</span>
          </div>
        </div>
      </div>

      <!-- 占卜 -->
      <div class="page" id="page-zhanbu">
        <div class="back-btn" onclick="switchTab(\'home\',document.querySelectorAll(\'.ft .t\')[0])">
          <span>‹</span>
          <span>返回</span>
        </div>
        <div class="sec">
          <h3>占卜问卦</h3>
        </div>
        <div class="zs-list">
          <div class="zs-card" onclick="showToast(\'功能开发中...\')">
            <div class="zs-title">🎴 塔罗牌占卜</div>
            <div class="zs-desc">抽取一张塔罗牌，解读你的运势走向</div>
          </div>
          <div class="zs-card" onclick="showToast(\'功能开发中...\')">
            <div class="zs-title">☯️ 易经占卦</div>
            <div class="zs-desc">六爻占卦，探寻天机</div>
          </div>
        </div>
      </div>

      <!-- 更多 -->
      <div class="page" id="page-more">
        <div class="back-btn" onclick="switchTab(\'home\',document.querySelectorAll(\'.ft .t\')[0])">
          <span>‹</span>
          <span>返回</span>
        </div>
        <div class="sec">
          <h3>全部服务</h3>
        </div>
        <div class="zx-list">
          <div class="zx-item" onclick="showToast(\'功能开发中...\')">
            <span class="zx-icon">🔮</span>
            <div class="zx-info">
              <div class="zx-title">六爻占卜</div>
              <div class="zx-desc">传统六爻卦象解读</div>
            </div>
            <span class="zx-arrow">›</span>
          </div>
          <div class="zx-item" onclick="showToast(\'功能开发中...\')">
            <span class="zx-icon">📿</span>
            <div class="zx-info">
              <div class="zx-title">灵签占卜</div>
              <div class="zx-desc">观音灵签、关帝灵签</div>
            </div>
            <span class="zx-arrow">›</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部标签栏 -->
    <div class="ft" id="ft">
      <div class="t a" onclick="switchTab(\'home\',this)">
        <span class="ti">🏠</span>
        <span>首页</span>
      </div>
      <div class="t" onclick="switchTab(\'shengxiao\',this)">
        <span class="ti">🐭</span>
        <span>生肖</span>
      </div>
      <div class="t" onclick="switchTab(\'zhanbu\',this)">
        <span class="ti">🔮</span>
        <span>占卜</span>
      </div>
      <div class="t" onclick="switchTab(\'more\',this)">
        <span class="ti">📋</span>
        <span>更多</span>
      </div>
      <div class="t" onclick="checkLogin()">
        <span class="ti">👤</span>
        <span>我的</span>
      </div>
    </div>

    <!-- 用户中心页面 -->
    <div class="uc-page" id="uc-page">
      <div class="uc-hdr">
        <div class="uc-back" onclick="closeUserCenter()">‹</div>
        <div class="uc-title">个人中心</div>
        <div class="uc-spacer"></div>
      </div>
      <div class="uc-body">
        <div class="uc-card">
          <div class="uc-avatar" id="uc-avatar">👤</div>
          <div class="uc-name" id="uc-name">未登录</div>
          <div class="uc-phone" id="uc-phone">请登录后查看</div>
          <div id="uc-vip-status" style="margin-top:0.5rem;font-size:0.75rem;color:rgba(255,255,255,0.4);">未开通会员</div>
          <div class="uc-stats">
            <div class="uc-stat">
              <div class="uc-stat-v" id="uc-free">0</div>
              <div class="uc-stat-l">免费次数</div>
            </div>
            <div class="uc-stat">
              <div class="uc-stat-v" id="uc-count">0</div>
              <div class="uc-stat-l">测算次数</div>
            </div>
            <div class="uc-stat">
              <div class="uc-stat-v" id="uc-days">0</div>
              <div class="uc-stat-l">会员天数</div>
            </div>
          </div>
        </div>

        <div class="uc-menu">
          <div class="uc-menu-i" onclick="openVip()">
            <span class="ic">⭐</span>
            <span class="lb">开通会员</span>
            <span class="ar">›</span>
          </div>
          <div class="uc-menu-i" onclick="showToast(\'功能开发中...\')">
            <span class="ic">📊</span>
            <span class="lb">测算历史</span>
            <span class="ar">›</span>
          </div>
          <div class="uc-menu-i" onclick="showToast(\'功能开发中...\')">
            <span class="ic">💰</span>
            <span class="lb">我的积分</span>
            <span class="ar">›</span>
          </div>
          <div class="uc-menu-i" onclick="showToast(\'功能开发中...\')">
            <span class="ic">⚙️</span>
            <span class="lb">设置</span>
            <span class="ar">›</span>
          </div>
          <div class="uc-menu-i" onclick="doLogout()">
            <span class="ic">🚪</span>
            <span class="lb">退出登录</span>
            <span class="ar">›</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 会员开通页面 -->
    <div class="vip-page" id="vip-page">
      <div class="vip-hdr">
        <div class="vip-back" onclick="closeVip()">‹</div>
        <div class="vip-title">开通会员</div>
        <div class="vip-spacer"></div>
      </div>
      <div class="vip-body">
        <div class="vip-card">
          <div class="vip-badge">⭐ 会员专属</div>
          <div class="vip-name" id="vip-name">免费会员</div>
          <div class="vip-price" id="vip-price">¥0<span>/月</span></div>
          <div class="vip-features">
            <div class="vip-feature"><span class="check">✓</span><span>3次免费测算</span></div>
            <div class="vip-feature"><span class="check">✓</span><span>基础命理分析</span></div>
            <div class="vip-feature"><span class="check">✓</span><span>每日运势推送</span></div>
          </div>
        </div>

        <div class="sec">
          <h3>选择时长</h3>
        </div>

        <div class="vip-options">
          <div class="vip-option" onclick="selectVipDuration(1, this)">
            <div class="duration">1个月</div>
            <div class="price">¥29<span>/月</span></div>
          </div>
          <div class="vip-option a" onclick="selectVipDuration(3, this)">
            <div class="duration">3个月</div>
            <div class="price">¥25<span>/月</span></div>
            <div class="save">省¥12</div>
          </div>
          <div class="vip-option" onclick="selectVipDuration(12, this)">
            <div class="duration">12个月</div>
            <div class="price">¥19<span>/月</span></div>
            <div class="save">省¥120</div>
          </div>
        </div>

        <div class="sec">
          <h3>支付方式</h3>
        </div>

        <div class="vip-pay">
          <div class="vip-pay-opt a" onclick="selectPay(\'wechat\', this)">
            <span class="ic">💚</span>
            <span class="lb">微信支付</span>
          </div>
          <div class="vip-pay-opt" onclick="selectPay(\'alipay\', this)">
            <span class="ic">💙</span>
            <span class="lb">支付宝</span>
          </div>
          <div class="vip-pay-opt" onclick="selectPay(\'qq\', this)">
            <span class="ic">💜</span>
            <span class="lb">QQ钱包</span>
          </div>
        </div>

        <button class="vip-btn" onclick="doVipPay()">立即开通</button>
      </div>
    </div>

    <!-- 登录/注册弹窗 -->
    <div class="auth-overlay" id="auth-overlay">
      <div class="auth-hdr">
        <div class="auth-back" onclick="closeAuth()">✕</div>
        <div class="auth-title">欢迎来到玄机算命网</div>
        <div class="auth-spacer"></div>
      </div>
      <div class="auth-body">
        <div class="auth-logo">
          <h2>玄机算命网</h2>
          <p>汇聚千年智慧 · 解读命运玄机</p>
        </div>

        <div class="auth-tabs">
          <div class="auth-tab a" onclick="switchAuthTab(\'login\',this)">验证码登录</div>
          <div class="auth-tab" onclick="switchAuthTab(\'password\',this)">密码登录</div>
          <div class="auth-tab" onclick="switchAuthTab(\'register\',this)">注册账号</div>
        </div>

        <!-- 验证码登录 -->
        <div class="auth-form" id="form-login">
          <input type="tel" class="auth-input" id="login-phone" placeholder="请输入手机号" maxlength="11">
          <div class="row">
            <input type="tel" class="auth-input" id="login-code" placeholder="请输入验证码" maxlength="6">
            <button onclick="sendCode(\'login\',this)">获取验证码</button>
          </div>
          <button class="auth-btn" onclick="doLogin()">登录</button>
          <div class="auth-link" onclick="switchAuthTab(\'forgot\',document.querySelector(\'.auth-tab:nth-child(2)\'))">忘记密码？</div>
        </div>

        <!-- 密码登录 -->
        <div class="auth-form" id="form-password" style="display:none;">
          <input type="tel" class="auth-input" id="password-phone" placeholder="请输入手机号" maxlength="11">
          <input type="password" class="auth-input" id="password-pwd" placeholder="请输入密码">
          <button class="auth-btn" onclick="doPasswordLogin()">登录</button>
          <div class="auth-link" onclick="switchAuthTab(\'forgot\',document.querySelector(\'.auth-tab:nth-child(2)\'))">忘记密码？</div>
        </div>

        <!-- 注册 -->
        <div class="auth-form" id="form-register" style="display:none;">
          <input type="tel" class="auth-input" id="reg-phone" placeholder="请输入手机号" maxlength="11">
          <div class="row">
            <input type="tel" class="auth-input" id="reg-code" placeholder="请输入验证码" maxlength="6">
            <button onclick="sendCode(\'register\',this)">获取验证码</button>
          </div>
          <input type="password" class="auth-input" id="reg-password" placeholder="请设置密码（至少6位）">
          <button class="auth-btn" onclick="doRegister()">注册并登录</button>
        </div>

        <!-- 忘记密码 -->
        <div class="auth-form" id="form-forgot" style="display:none;">
          <input type="tel" class="auth-input" id="forgot-phone" placeholder="请输入手机号" maxlength="11">
          <div class="row">
            <input type="tel" class="auth-input" id="forgot-code" placeholder="请输入验证码" maxlength="6">
            <button onclick="sendCode(\'forgot\',this)">获取验证码</button>
          </div>
          <input type="password" class="auth-input" id="forgot-password" placeholder="请设置新密码（至少6位）">
          <button class="auth-btn" onclick="doForgotPassword()">重置密码</button>
        </div>

        <!-- 第三方登录 -->
        <div style="margin-top:2rem;text-align:center;">
          <div style="font-size:0.7rem;color:rgba(255,255,255,0.3);margin-bottom:1rem;">——— 第三方登录 ———</div>
          <div style="display:flex;justify-content:center;gap:1.5rem;">
            <div onclick="doTencentLogin()" style="cursor:pointer;font-size:2rem;">💚</div>
            <div onclick="doQQLogin()" style="cursor:pointer;font-size:2rem;">💜</div>
            <div onclick="doGithubLogin()" style="cursor:pointer;font-size:2rem;">🖤</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast提示 -->
    <div class="toast" id="toast"></div>

  </div>
</div>

<script>
var API_BASE = \'\';
var currentUser = null;
var vipDuration = 3;
var vipPayMethod = \'wechat\';

// 初始化
function init(){
    console.log(\'init called\');
    
    // 自动检测API地址
    if(window.location.hostname === \'localhost\' || window.location.hostname === \'127.0.0.1\'){
        API_BASE = \'http://localhost:5000\';
    } else {
        API_BASE = window.location.origin;
    }
    console.log(\'API_BASE:\', API_BASE);
    
    // 恢复登录状态
    var saved = localStorage.getItem(\'xjsm_user\');
    if(saved){
        try {
            currentUser = JSON.parse(saved);
            updateUserBar();
        } catch(e) {
            console.error(\'Parse user error:\', e);
        }
    }
    
    // 更新状态栏
    updateStatus();
    setInterval(updateStatus, 10000);
    
    // 模拟电池变化
    setInterval(updateBattery, 10000);
}

// 更新状态栏
function updateStatus(){
    var now = new Date();
    var time = (now.getHours() < 10 ? \'0\' : \'\') + now.getHours() + \':\' + (now.getMinutes() < 10 ? \'0\' : \'\') + now.getMinutes();
    document.getElementById(\'status-time\').textContent = time;
    
    var battery = document.getElementById(\'battery-pct\');
    var pct = parseInt(battery.textContent);
    if(pct > 20 && Math.random() > 0.5){
        pct--;
    } else if(pct < 95) {
        pct++;
    }
    battery.textContent = pct + \'%\';
}

function updateBattery(){
    // 电池模拟
}

// 切换标签
function switchTab(tab, el){
    console.log(\'switchTab:\', tab);
    
    // 隐藏所有页面
    document.querySelectorAll(\'.page\').forEach(function(p){
        p.classList.remove(\'active\');
    });
    
    // 显示目标页面
    var targetMap = {
        \'home\': \'page-home\',
        \'shengxiao\': \'page-shengxiao\',
        \'zhanbu\': \'page-zhanbu\',
        \'more\': \'page-more\'
    };
    
    var targetId = targetMap[tab];
    if(targetId){
        document.getElementById(targetId).classList.add(\'active\');
    }
    
    // 更新标签样式
    document.querySelectorAll(\'.ft .t\').forEach(function(t){
        t.classList.remove(\'a\');
    });
    if(el){
        el.classList.add(\'a\');
    }
}

// 检查登录
function checkLogin(){
    console.log(\'checkLogin called, currentUser:\', currentUser);
    if(currentUser && currentUser.phone){
        console.log(\'User is logged in, opening user center...\');
        openUserCenter();
    } else {
        console.log(\'User not logged in, opening auth...\');
        openAuth();
    }
}

// 打开登录
function openAuth(){
    console.log(\'openAuth called\');
    document.getElementById(\'auth-overlay\').classList.add(\'active\');
    document.body.style.overflow = \'hidden\';
}

// 关闭登录
function closeAuth(){
    console.log(\'closeAuth called\');
    document.getElementById(\'auth-overlay\').classList.remove(\'active\');
    document.body.style.overflow = \'auto\';
}

// 切换登录标签
function switchAuthTab(tab, el){
    console.log(\'switchAuthTab:\', tab);
    
    // 更新标签样式
    document.querySelectorAll(\'.auth-tab\').forEach(function(t){
        t.classList.remove(\'a\');
    });
    if(el){
        el.classList.add(\'a\');
    }
    
    // 显示对应表单
    document.getElementById(\'form-login\').style.display = \'none\';
    document.getElementById(\'form-password\').style.display = \'none\';
    document.getElementById(\'form-register\').style.display = \'none\';
    document.getElementById(\'form-forgot\').style.display = \'none\';
    
    var formMap = {
        \'login\': \'form-login\',
        \'password\': \'form-password\',
        \'register\': \'form-register\',
        \'forgot\': \'form-forgot\'
    };
    
    var formId = formMap[tab];
    if(formId){
        document.getElementById(formId).style.display = \'flex\';
    }
}

// 发送验证码
function sendCode(type, btn){
    console.log(\'sendCode:\', type);
    
    var phone = \'\';
    if(type === \'login\'){
        phone = document.getElementById(\'login-phone\').value.trim();
    } else if(type === \'register\'){
        phone = document.getElementById(\'reg-phone\').value.trim();
    } else if(type === \'forgot\'){
        phone = document.getElementById(\'forgot-phone\').value.trim();
    }
    
    if(!phone || phone.length !== 11){
        showToast(\'请输入正确的手机号\');
        return;
    }
    
    // 调用API
    fetch(API_BASE + \'/api/sendCode\', {
        method: \'POST\',
        headers: {\'Content-Type\': \'application/json\'},
        body: JSON.stringify({phone: phone})
    })
    .then(function(res){return res.json();})
    .then(function(data){
        if(data.code === 200){
            showToast(\'验证码已发送\');
            
            // 倒计时
            var seconds = 60;
            btn.disabled = true;
            btn.textContent = seconds + \'s\';
            var timer = setInterval(function(){
                seconds--;
                btn.textContent = seconds + \'s\';
                if(seconds <= 0){
                    clearInterval(timer);
                    btn.disabled = false;
                    btn.textContent = \'获取验证码\';
                }
            }, 1000);
        } else {
            showToast(data.msg || \'发送失败\');
        }
    })
    .catch(function(err){
        console.error(\'Send code error:\', err);
        showToast(\'网络错误\');
    });
}

// 验证码登录
function doLogin(){
    console.log(\'doLogin called\');
    
    var phone = document.getElementById(\'login-phone\').value.trim();
    var code = document.getElementById(\'login-code\').value.trim();
    
    if(!phone || !code){
        showToast(\'请输入手机号和验证码\');
        return;
    }
    
    fetch(API_BASE + \'/api/login\', {
        method: \'POST\',
        headers: {\'Content-Type\': \'application/json\'},
        body: JSON.stringify({phone: phone, code: code})
    })
    .then(function(res){return res.json();})
    .then(function(data){
        if(data.code === 200){
            currentUser = data.data;
            localStorage.setItem(\'xjsm_user\', JSON.stringify(currentUser));
            updateUserBar();
            closeAuth();
            showToast(\'登录成功\');
        } else {
            showToast(data.msg || \'登录失败\');
        }
    })
    .catch(function(err){
        console.error(\'Login error:\', err);
        showToast(\'网络错误\');
    });
}

// 密码登录
function doPasswordLogin(){
    console.log(\'doPasswordLogin called\');
    
    var phone = document.getElementById(\'password-phone\').value.trim();
    var password = document.getElementById(\'password-pwd\').value;
    
    if(!phone || !password){
        showToast(\'请输入手机号和密码\');
        return;
    }
    
    fetch(API_BASE + \'/api/password_login\', {
        method: \'POST\',
        headers: {\'Content-Type\': \'application/json\'},
        body: JSON.stringify({phone: phone, password: password})
    })
    .then(function(res){return res.json();})
    .then(function(data){
        if(data.code === 200){
            currentUser = data.data;
            localStorage.setItem(\'xjsm_user\', JSON.stringify(currentUser));
            updateUserBar();
            closeAuth();
            showToast(\'登录成功\');
        } else {
            showToast(data.msg || \'登录失败\');
        }
    })
    .catch(function(err){
        console.error(\'Password login error:\', err);
        showToast(\'网络错误\');
    });
}

// 注册
function doRegister(){
    console.log(\'doRegister called\');
    
    var phone = document.getElementById(\'reg-phone\').value.trim();
    var code = document.getElementById(\'reg-code\').value.trim();
    var password = document.getElementById(\'reg-password\').value;
    
    if(!phone || !code || !password){
        showToast(\'请填写完整信息\');
        return;
    }
    
    if(password.length < 6){
        showToast(\'密码至少6位\');
        return;
    }
    
    fetch(API_BASE + \'/api/register\', {
        method: \'POST\',
        headers: {\'Content-Type\': \'application/json\'},
        body: JSON.stringify({phone: phone, code: code, password: password})
    })
    .then(function(res){return res.json();})
    .then(function(data){
        if(data.code === 200){
            currentUser = data.data;
            localStorage.setItem(\'xjsm_user\', JSON.stringify(currentUser));
            updateUserBar();
            closeAuth();
            openUserCenter();
            showToast(\'注册成功\');
        } else {
            showToast(data.msg || \'注册失败\');
        }
    })
    .catch(function(err){
        console.error(\'Register error:\', err);
        showToast(\'网络错误\');
    });
}

// 忘记密码
function doForgotPassword(){
    console.log(\'doForgotPassword called\');
    
    var phone = document.getElementById(\'forgot-phone\').value.trim();
    var code = document.getElementById(\'forgot-code\').value.trim();
    var newPassword = document.getElementById(\'forgot-password\').value;
    
    if(!phone || !code || !newPassword){
        showToast(\'请填写完整信息\');
        return;
    }
    
    if(newPassword.length < 6){
        showToast(\'密码至少6位\');
        return;
    }
    
    fetch(API_BASE + \'/api/forgot_password\', {
        method: \'POST\',
        headers: {\'Content-Type\': \'application/json\'},
        body: JSON.stringify({phone: phone, code: code, new_password: newPassword})
    })
    .then(function(res){return res.json();})
    .then(function(data){
        if(data.code === 200){
            showToast(\'密码重置成功，请登录\');
            switchAuthTab(\'login\', document.querySelector(\'.auth-tab:first-child\'));
        } else {
            showToast(data.msg || \'重置失败\');
        }
    })
    .catch(function(err){
        console.error(\'Forgot password error:\', err);
        showToast(\'网络错误\');
    });
}

// 第三方登录（Mock）
function doTencentLogin(){
    console.log(\'doTencentLogin called\');
    showToast(\'微信登录开发中...\');
}

function doQQLogin(){
    console.log(\'doQQLogin called\');
    showToast(\'QQ登录开发中...\');
}

function doGithubLogin(){
    console.log(\'doGithubLogin called\');
    showToast(\'GitHub登录开发中...\');
}

// 打开用户中心
function openUserCenter(){
    console.log(\'openUserCenter called\');
    if(!currentUser){
        openAuth();
        return;
    }
    
    // 显示用户信息
    document.getElementById(\'uc-name\').textContent = currentUser.name;
    document.getElementById(\'uc-phone\').textContent = currentUser.phone.substring(0,3) + \'****\' + currentUser.phone.substring(7);
    document.getElementById(\'uc-free\').textContent = currentUser.free_count || 3;
    document.getElementById(\'uc-avatar\').textContent = currentUser.avatar || \'👤\';
    
    // 显示VIP状态
    var vipStatus = document.getElementById(\'uc-vip-status\');
    if(currentUser.is_vip){
        var exp = new Date(currentUser.vip_expire * 1000).toLocaleDateString();
        vipStatus.textContent = \'⭐ \' + (currentUser.vip_type || \'会员\') + \'（有效期至：\' + exp + \'）\';
        vipStatus.style.color = \'#ffd700\';
        
        // 计算剩余天数
        var days = Math.ceil((currentUser.vip_expire - Date.now()/1000) / 86400);
        document.getElementById(\'uc-days\').textContent = days;
    } else {
        vipStatus.textContent = \'未开通会员\';
        vipStatus.style.color = \'rgba(255,255,255,0.4)\';
        document.getElementById(\'uc-days\').textContent = \'0\';
    }
    
    document.getElementById(\'uc-page\').classList.add(\'active\');
    document.body.style.overflow = \'hidden\';
}

// 关闭用户中心
function closeUserCenter(){
    console.log(\'closeUserCenter called\');
    document.getElementById(\'uc-page\').classList.remove(\'active\');
    document.body.style.overflow = \'auto\';
}

// 退出登录
function doLogout(){
    console.log(\'doLogout called\');
    currentUser = null;
    localStorage.removeItem(\'xjsm_user\');
    updateUserBar();
    closeUserCenter();
    showToast(\'已退出登录\');
}

// 打开VIP页面
function openVip(){
    console.log(\'openVip called\');
    if(!currentUser){
        showToast(\'请先登录\');
        return;
    }
    document.getElementById(\'vip-page\').classList.add(\'active\');
    document.body.style.overflow = \'hidden\';
    
    // 如果已经是VIP，显示当前会员信息
    if(currentUser.is_vip){
        var exp = new Date(currentUser.vip_expire * 1000).toLocaleDateString();
        document.getElementById(\'vip-name\').textContent = currentUser.vip_type || \'会员\';
        document.getElementById(\'vip-price\').innerHTML = \'¥0<span>/已开通</span>\';
    }
}

// 关闭VIP页面
function closeVip(){
    console.log(\'closeVip called\');
    document.getElementById(\'vip-page\').classList.remove(\'active\');
    document.body.style.overflow = \'auto\';
}

// 选择VIP时长
function selectVipDuration(months, el){
    console.log(\'selectVipDuration:\', months);
    vipDuration = months;
    
    // 更新UI
    document.querySelectorAll(\'.vip-option\').forEach(function(opt){
        opt.classList.remove(\'a\');
    });
    el.classList.add(\'a\');
    
    // 更新价格显示
    var pricePerMonth = 29;
    if(months == 3) pricePerMonth = 25;
    if(months == 12) pricePerMonth = 19;
    var total = pricePerMonth * months;
    document.getElementById(\'vip-price\').innerHTML = \'¥\' + total + \'<span>/\' + months + \'个月</span>\';
}

// 选择支付方式
function selectPay(method, el){
    console.log(\'selectPay:\', method);
    vipPayMethod = method;
    
    // 更新UI
    document.querySelectorAll(\'.vip-pay-opt\').forEach(function(opt){
        opt.classList.remove(\'a\');
    });
    el.classList.add(\'a\');
}

// 开通VIP
function doVipPay(){
    console.log(\'doVipPay called, duration:\', vipDuration, \'pay:\', vipPayMethod);
    
    if(!currentUser){
        showToast(\'请先登录\');
        return;
    }
    
    // 计算价格
    var pricePerMonth = 29;
    if(vipDuration == 3) pricePerMonth = 25;
    if(vipDuration == 12) pricePerMonth = 19;
    var total = pricePerMonth * vipDuration;
    
    showToast(\'正在跳转支付...\');
    
    // 模拟支付（实际项目中应调用支付API）
    setTimeout(function(){
        // 调用后端API开通会员
        fetch(API_BASE + \'/api/upgrade_vip\', {
            method: \'POST\',
            headers: {\'Content-Type\': \'application/json\'},
            body: JSON.stringify({
                phone: currentUser.phone,
                duration: vipDuration,
                pay_method: vipPayMethod,
                amount: total
            })
        })
        .then(function(res){return res.json();})
        .then(function(data){
            if(data.code === 200){
                // 更新当前用户信息
                currentUser.is_vip = true;
                currentUser.vip_expire = data.data.vip_expire;
                currentUser.vip_type = data.data.vip_type;
                localStorage.setItem(\'xjsm_user\', JSON.stringify(currentUser));
                
                // 更新用户中心显示
                updateUserBar();
                var vipStatus = document.getElementById(\'uc-vip-status\');
                var exp = new Date(currentUser.vip_expire * 1000).toLocaleDateString();
                vipStatus.textContent = \'⭐ \' + currentUser.vip_type + \'（有效期至：\' + exp + \'）\';
                vipStatus.style.color = \'#ffd700\';
                
                showToast(\'会员开通成功！\');
                closeVip();
            } else {
                showToast(data.msg || \'支付失败\');
            }
        })
        .catch(function(err){
            console.error(\'Pay error:\', err);
            showToast(\'网络错误\');
        });
    }, 1500);
}

// 更新用户栏
function updateUserBar(){
    console.log(\'updateUserBar called, currentUser:\', currentUser);
    if(currentUser && currentUser.phone){
        document.getElementById(\'ub-name\').textContent = currentUser.name;
        document.getElementById(\'ub-desc\').textContent = \'免费次数：\' + (currentUser.free_count || 3);
        document.getElementById(\'ub-avatar\').textContent = currentUser.avatar || \'👤\';
    } else {
        document.getElementById(\'ub-name\').textContent = \'点击登录\';
        document.getElementById(\'ub-desc\').textContent = \'登录后享受更多服务\';
        document.getElementById(\'ub-avatar\').textContent = \'👤\';
    }
}

// 显示Toast
function showToast(msg){
    console.log(\'showToast:\', msg);
    var toast = document.getElementById(\'toast\');
    toast.textContent = msg;
    toast.classList.add(\'show\');
    setTimeout(function(){
        toast.classList.remove(\'show\');
    }, 2000);
}

// 页面加载完成后初始化
document.addEventListener(\'DOMContentLoaded\', init);
</script>

</body>
</html>'''

# 写入文件
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ 完整的index.html已重新生成")
print("  - 包含所有CSS样式（包括.vip-page）")
print("  - 包含所有JavaScript函数（包括openVip/closeVip/doVipPay）")
print("  - 包含所有HTML元素（包括vip-page）")
print("  - 文件大小:", len(html_content), "字符")
