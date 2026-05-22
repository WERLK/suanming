#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>玄机算命网 - 专业命理测算平台</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#1a1a2e">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
        body { background:#000; color:#fff; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; width:100vw; height:100vh; overflow:hidden; }
        
        /* 手机模拟器外壳 */
        .phone-simulator {
            width:100vw; height:100vh;
            display:flex; justify-content:center; align-items:center;
            background:linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
            padding:0; margin:0;
        }
        .app {
            width:100%; max-width:420px;
            height:100vh;
            display:flex; flex-direction:column;
            background:linear-gradient(180deg, #0f0c29 0%, #1a1a2e 30%, #16213e 70%, #0a0a1a 100%);
            position:relative; overflow:hidden;
            box-shadow:0 0 50px rgba(255,215,0,0.1);
        }
        
        /* iOS状态栏 */
        .ios-status-bar {
            display:flex; justify-content:space-between; align-items:center;
            padding:0.3rem 1rem;
            background:rgba(0,0,0,0.6);
            backdrop-filter:blur(20px);
            font-size:0.75rem; color:#fff;
            flex-shrink:0; z-index:1000;
            height:28px;
        }
        .ios-status-bar .time { font-weight:700; font-size:0.85rem; }
        .ios-status-bar .center { font-size:0.7rem; opacity:0.8; }
        .ios-status-bar .right-icons { display:flex; align-items:center; gap:5px; }
        
        /* 信号格 */
        .signal-container { display:flex; align-items:flex-end; gap:1.5px; height:14px; margin-right:4px; }
        .signal-bar { width:3px; background:#4cd964; border-radius:1px; transition:all 0.3s; }
        .signal-bar:nth-child(1) { height:4px; }
        .signal-bar:nth-child(2) { height:6px; }
        .signal-bar:nth-child(3) { height:8px; }
        .signal-bar:nth-child(4) { height:11px; }
        .signal-bar.weak { background:#ff3b30; }
        .signal-bar.medium { background:#ffcc00; }
        .signal-bar.off { background:rgba(255,255,255,0.2); }
        
        /* 电池 */
        .battery-container { display:flex; align-items:center; gap:3px; margin-left:4px; }
        .battery-body {
            width:22px; height:11px;
            border:1.5px solid #fff; border-radius:2px;
            position:relative; display:flex; align-items:center;
            padding:1.5px;
        }
        .battery-body::after {
            content:''; position:absolute; right:-3.5px; top:3px;
            width:1.5px; height:4px;
            background:#fff; border-radius:0 1px 1px 0;
        }
        .battery-fill { height:100%; border-radius:1px; background:#4cd964; transition:all 0.5s; }
        .battery-fill.low { background:#ff3b30; }
        .battery-fill.medium { background:#ffcc00; }
        .battery-text { font-size:0.62rem; min-width:25px; text-align:right; }
        
        /* 顶部标题区 */
        .app-header {
            text-align:center; padding:0.8rem 1rem 0.6rem;
            background:linear-gradient(180deg, rgba(0,0,0,0.7) 0%, transparent 100%);
            backdrop-filter:blur(20px);
            border-bottom:1px solid rgba(255,215,0,0.15);
            flex-shrink:0;
        }
        .app-header h1 {
            font-size:1.3rem; font-weight:800;
            background:linear-gradient(90deg, #ffd700, #ff6b35, #ffd700, #ff6b35);
            background-size:300% 100%;
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            animation:goldShimmer 4s ease infinite;
            letter-spacing:3px;
        }
        @keyframes goldShimmer {
            0% { background-position:0% 50%; }
            50% { background-position:100% 50%; }
            100% { background-position:0% 50%; }
        }
        .app-header .subtitle { font-size:0.65rem; color:rgba(255,255,255,0.45); margin-top:3px; letter-spacing:1px; }
        
        /* 在线人数条 */
        .online-stats {
            display:flex; justify-content:center; align-items:center; gap:0.8rem;
            padding:0.35rem 1rem;
            font-size:0.68rem; color:rgba(255,255,255,0.6);
            background:rgba(255,215,0,0.06);
            flex-shrink:0;
        }
        .online-dot { width:6px; height:6px; border-radius:50%; background:#4cd964; animation:pulse 1.5s infinite; }
        @keyframes pulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(0.8); } }
        
        /* 公告滚动条 */
        .notice-bar {
            display:flex; align-items:center; gap:0.5rem;
            padding:0.35rem 1rem;
            font-size:0.68rem;
            background:linear-gradient(90deg, rgba(255,215,0,0.1), rgba(255,107,53,0.08), rgba(255,215,0,0.1));
            color:#ffd700; overflow:hidden; flex-shrink:0;
            border-top:1px solid rgba(255,215,0,0.08);
            border-bottom:1px solid rgba(255,215,0,0.08);
        }
        .notice-scroll { white-space:nowrap; animation:scrollNotice 25s linear infinite; font-size:0.65rem; }
        @keyframes scrollNotice { 0% { transform:translateX(100%); } 100% { transform:translateX(-100%); } }
        
        /* 页面容器 */
        .page-container {
            flex:1; position:relative; overflow:hidden;
        }
        .page {
            position:absolute; top:0; left:0; width:100%; height:100%;
            overflow-y:auto; overflow-x:hidden;
            display:none; flex-direction:column;
            -webkit-overflow-scrolling:touch;
            scrollbar-width:none;
        }
        .page.active { display:flex; }
        .page::-webkit-scrollbar { display:none; }
        
        /* 搜索栏 */
        .search-bar { padding:0.6rem 1rem; flex-shrink:0; }
        .search-inner {
            display:flex; align-items:center; gap:0.5rem;
            background:rgba(255,255,255,0.07);
            border-radius:20px; padding:0.55rem 1rem;
            font-size:0.78rem; color:rgba(255,255,255,0.4);
            border:1px solid rgba(255,255,255,0.05);
            transition:all 0.2s;
        }
        .search-inner:active { background:rgba(255,255,255,0.12); }
        
        /* 功能模块网格 */
        .module-grid {
            display:grid; grid-template-columns:repeat(4, 1fr);
            gap:0.55rem; padding:0.5rem 1rem;
            flex-shrink:0;
        }
        .module-item {
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            background:linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
            border-radius:14px; padding:0.7rem 0.2rem; gap:0.35rem;
            cursor:pointer;
            border:1px solid rgba(255,215,0,0.08);
            transition:all 0.2s;
            position:relative; overflow:hidden;
        }
        .module-item::before {
            content:''; position:absolute; top:0; left:0; right:0;
            height:1px;
            background:linear-gradient(90deg, transparent, rgba(255,215,0,0.3), transparent);
        }
        .module-item:active { transform:scale(0.93); background:rgba(255,215,0,0.12); }
        .module-item .icon { font-size:1.6rem; }
        .module-item .label { font-size:0.63rem; color:rgba(255,255,255,0.8); text-align:center; line-height:1.25; font-weight:500; }
        .module-item.hot::after {
            content:'HOT'; position:absolute; top:3px; right:3px;
            font-size:0.45rem; background:linear-gradient(135deg, #ff3b30, #ff6b35);
            padding:1px 4px; border-radius:6px; color:#fff; font-weight:700;
        }
        .module-item.new::after {
            content:'NEW'; position:absolute; top:3px; right:3px;
            font-size:0.45rem; background:linear-gradient(135deg, #30d158, #30d1ff);
            padding:1px 4px; border-radius:6px; color:#fff; font-weight:700;
        }
        
        /* 区域标题 */
        .section-header {
            display:flex; justify-content:space-between; align-items:center;
            padding:0.9rem 1rem 0.5rem; flex-shrink:0;
        }
        .section-header h3 {
            font-size:0.95rem; color:#ffd700; font-weight:700;
            display:flex; align-items:center; gap:0.4rem;
        }
        .section-header h3::before {
            content:''; display:inline-block; width:3px; height:14px;
            background:linear-gradient(180deg, #ffd700, #ff6b35);
            border-radius:2px;
        }
        .section-more { font-size:0.7rem; color:rgba(255,255,255,0.4); }
        
        /* 今日运势卡片 */
        .today-fortune-card {
            margin:0.5rem 1rem;
            padding:1rem;
            background:linear-gradient(135deg, rgba(255,215,0,0.12), rgba(255,107,53,0.08));
            border-radius:14px;
            border:1px solid rgba(255,215,0,0.18);
            flex-shrink:0;
        }
        .today-fortune-card h4 { font-size:0.88rem; color:#ffd700; margin-bottom:0.6rem; display:flex; align-items:center; gap:0.4rem; }
        .fortune-badge {
            display:inline-block; padding:2px 8px; border-radius:8px;
            font-size:0.65rem; font-weight:600;
        }
        .fortune-badge.good { background:rgba(76,217,100,0.2); color:#4cd964; }
        .fortune-badge.bad { background:rgba(255,59,48,0.2); color:#ff3b30; }
        .fortune-badge.medium { background:rgba(255,204,0,0.2); color:#ffcc00; }
        .fortune-star { color:#ffd700; font-size:0.85rem; }
        
        /* 知识库卡片 */
        .kb-list { padding:0.5rem 1rem; flex-shrink:0; }
        .kb-card {
            background:rgba(255,255,255,0.04);
            border-radius:14px; margin-bottom:0.6rem;
            overflow:hidden;
            border:1px solid rgba(255,255,255,0.06);
            transition:all 0.3s;
        }
        .kb-card-header {
            display:flex; justify-content:space-between; align-items:center;
            padding:0.8rem 1rem; cursor:pointer;
            background:rgba(255,255,255,0.02);
        }
        .kb-card-header:hover { background:rgba(255,255,255,0.05); }
        .kb-card-title { font-size:0.82rem; color:rgba(255,255,255,0.9); font-weight:600; }
        .kb-card-arrow { font-size:0.7rem; color:rgba(255,255,255,0.4); transition:transform 0.3s; }
        .kb-card.expanded .kb-card-arrow { transform:rotate(180deg); }
        .kb-card-body {
            max-height:0; overflow:hidden;
            transition:max-height 0.4s ease, padding 0.3s ease;
            padding:0 1rem;
        }
        .kb-card.expanded .kb-card-body { max-height:800px; padding:0 1rem 1rem; }
        .kb-card-content { font-size:0.73rem; color:rgba(255,255,255,0.6); line-height:1.8; }
        .kb-card-content p { margin-bottom:0.5rem; }
        .kb-tag { display:inline-block; padding:2px 8px; background:rgba(255,215,0,0.1); color:#ffd700; border-radius:6px; font-size:0.6rem; margin:2px; }
        
        /* 底部标签栏 */
        .tab-bar {
            display:flex; justify-content:space-around; align-items:center;
            padding:0.35rem 0 0.55rem;
            flex-shrink:0;
            background:rgba(0,0,0,0.85);
            backdrop-filter:blur(30px);
            border-top:1px solid rgba(255,255,255,0.08);
            z-index:1000;
        }
        .tab-item {
            display:flex; flex-direction:column; align-items:center; gap:0.15rem;
            color:rgba(255,255,255,0.35);
            font-size:0.58rem; cursor:pointer;
            padding:0.25rem 0.9rem; border-radius:10px;
            transition:all 0.2s;
        }
        .tab-item .tab-icon { font-size:1.2rem; transition:all 0.2s; }
        .tab-item.active { color:#ffd700; }
        .tab-item.active .tab-icon { transform:scale(1.1); }
        .tab-item:active { background:rgba(255,215,0,0.1); }
        
        /* 生肖页面 */
        .zodiac-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.6rem; padding:0.5rem 1rem; }
        .zodiac-item {
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            background:rgba(255,255,255,0.05); border-radius:14px; padding:0.8rem 0.3rem; gap:0.3rem;
            cursor:pointer; border:1px solid rgba(255,215,0,0.08); transition:all 0.2s;
        }
        .zodiac-item:active { transform:scale(0.93); background:rgba(255,215,0,0.15); }
        .zodiac-item .emoji { font-size:1.8rem; }
        .zodiac-item .name { font-size:0.72rem; color:rgba(255,255,255,0.85); font-weight:600; }
        .zodiac-item .rank { font-size:0.6rem; color:rgba(255,255,255,0.45); }
        
        /* 占卜页面 */
        .divination-list { padding:0.5rem 1rem; }
        .divination-item {
            display:flex; align-items:center; gap:0.8rem;
            padding:0.9rem; margin-bottom:0.6rem;
            background:rgba(255,255,255,0.05); border-radius:14px;
            border:1px solid rgba(255,255,255,0.06); cursor:pointer;
            transition:all 0.2s;
        }
        .divination-item:active { background:rgba(255,215,0,0.1); transform:scale(0.98); }
        .divination-icon { font-size:2rem; }
        .divination-info { flex:1; }
        .divination-name { font-size:0.85rem; color:rgba(255,255,255,0.9); font-weight:600; }
        .divination-desc { font-size:0.68rem; color:rgba(255,255,255,0.5); margin-top:3px; }
        .divination-arrow { color:rgba(255,255,255,0.3); font-size:0.8rem; }
        
        /* Toast提示 */
        .toast {
            position:fixed; top:50%; left:50%;
            transform:translate(-50%,-50%);
            background:rgba(0,0,0,0.88); color:#fff;
            padding:0.8rem 1.5rem; border-radius:12px;
            font-size:0.85rem; z-index:99999;
            pointer-events:none;
            animation:toastIn 0.3s ease;
        }
        @keyframes toastIn { from { opacity:0; transform:translate(-50%,-50%) scale(0.9); } to { opacity:1; transform:translate(-50%,-50%) scale(1); } }
        
        /* 骨头加载动画 */
        .loading-bone {
            width:30px; height:30px; border:3px solid rgba(255,215,0,0.2);
            border-top-color:#ffd700; border-radius:50%;
            animation:spin 0.8s linear infinite;
            margin:1rem auto;
        }
        @keyframes spin { to { transform:rotate(360deg); } }
        
        /* 分割线 */
        .divider { height:1px; background:rgba(255,255,255,0.06); margin:0.3rem 1rem; flex-shrink:0; }
        
        /* 运势详情 */
        .fortune-detail { padding:0.5rem 1rem; }
        .fortune-row {
            display:flex; justify-content:space-between; align-items:center;
            padding:0.6rem 0; border-bottom:1px solid rgba(255,255,255,0.04);
        }
        .fortune-row:last-child { border-bottom:none; }
        .fortune-label { font-size:0.78rem; color:rgba(255,255,255,0.6); }
        .fortune-bar-bg {
            flex:1; height:6px; background:rgba(255,255,255,0.08);
            border-radius:3px; margin:0 0.8rem; overflow:hidden;
        }
        .fortune-bar-fill { height:100%; border-radius:3px; transition:width 1s ease; }
        .fortune-value { font-size:0.72rem; font-weight:600; min-width:35px; text-align:right; }
    </style>
</head>
<body>
<div class="phone-simulator">
<div class="app">
    <!-- iOS状态栏 -->
    <div class="ios-status-bar">
        <span class="carrier" id="carrierName">中国移动</span>
        <span class="time" id="statusTime">11:39</span>
        <div class="right-icons">
            <div class="signal-container" id="signalBars">
                <div class="signal-bar"></div>
                <div class="signal-bar"></div>
                <div class="signal-bar"></div>
                <div class="signal-bar"></div>
            </div>
            <span id="netType" style="font-size:0.62rem;opacity:0.7;margin:0 2px;">4G</span>
            <div class="battery-container">
                <div class="battery-body">
                    <div class="battery-fill" id="battFill" style="width:78%;"></div>
                </div>
                <span class="battery-text" id="battText">78%</span>
            </div>
        </div>
    </div>
    
    <!-- 顶部标题 -->
    <div class="app-header">
        <h1>玄机算命网</h1>
        <div class="subtitle">测命理 · 知天命 · 改运势 · 掌人生</div>
    </div>
    
    <!-- 在线统计 -->
    <div class="online-stats">
        <div class="online-dot"></div>
        <span>当前在线：<strong id="onlineCount" style="color:#ffd700;font-weight:700;">13,582</strong> 人</span>
        <span style="margin-left:auto;font-size:0.62rem;color:rgba(255,255,255,0.35);">今日测算 42,167 次</span>
    </div>
    
    <!-- 公告 -->
    <div class="notice-bar">
        <span>📢</span>
        <div class="notice-scroll">🎉 新用户注册免费测算3次 · 关注公众号【玄机算命】领688积分 · 大师一对一在线解读 · 每日签到送积分可兑换测算 · 邀请好友得VIP会员</div>
    </div>
    
    <!-- 页面容器 -->
    <div class="page-container">
        <!-- 首页 -->
        <div class="page active" id="page-home">
            <div class="search-bar">
                <div class="search-inner" onclick="showToast('搜索功能开发中')">🔍 搜索算命、八字、风水、生肖...</div>
            </div>
            
            <!-- 热门功能 -->
            <div class="section-header"><h3>热门测算</h3><span class="section-more">全部 &gt;</span></div>
            <div class="module-grid">
                <div class="module-item hot" onclick="openModule('八字算命')"><span class="icon">📊</span><span class="label">八字算命</span></div>
                <div class="module-item hot" onclick="openModule('紫微斗数')"><span class="icon">⭐</span><span class="label">紫微斗数</span></div>
                <div class="module-item hot" onclick="openModule('塔罗牌')"><span class="icon">🀄</span><span class="label">塔罗牌</span></div>
                <div class="module-item hot" onclick="openModule('易经占卜')"><span class="icon">☯</span><span class="label">易经占卜</span></div>
            </div>
            <div class="module-grid" style="padding-top:0;">
                <div class="module-item hot" onclick="openModule('姓名测试')"><span class="icon">📝</span><span class="label">姓名测试</span></div>
                <div class="module-item hot" onclick="openModule('风水布局')"><span class="icon">🏠</span><span class="label">风水布局</span></div>
                <div class="module-item" onclick="openModule('面相分析')"><span class="icon">👤</span><span class="label">面相分析</span></div>
                <div class="module-item" onclick="openModule('手相解读')"><span class="icon">✋</span><span class="label">手相解读</span></div>
            </div>
            
            <div class="divider"></div>
            
            <!-- 今日运势 -->
            <div class="section-header"><h3>今日运势播报</h3><span class="section-more">查看详情 &gt;</span></div>
            <div class="today-fortune-card">
                <h4>📅 今日综合运势 <span class="fortune-badge good">宜</span></h4>
                <div class="fortune-detail">
                    <div class="fortune-row">
                        <span class="fortune-label">综合运势</span>
                        <div class="fortune-bar-bg"><div class="fortune-bar-fill" style="width:82%;background:linear-gradient(90deg,#4cd964,#30d158);"></div></div>
                        <span class="fortune-value" style="color:#4cd964;">82分</span>
                    </div>
                    <div class="fortune-row">
                        <span class="fortune-label">爱情运势</span>
                        <div class="fortune-bar-bg"><div class="fortune-bar-fill" style="width:75%;background:linear-gradient(90deg,#ff6b35,#ffd700);"></div></div>
                        <span class="fortune-value" style="color:#ff6b35;">75分</span>
                    </div>
                    <div class="fortune-row">
                        <span class="fortune-label">事业运势</span>
                        <div class="fortune-bar-bg"><div class="fortune-bar-fill" style="width:88%;background:linear-gradient(90deg,#30d1ff,#5856d6);"></div></div>
                        <span class="fortune-value" style="color:#30d1ff;">88分</span>
                    </div>
                    <div class="fortune-row">
                        <span class="fortune-label">财运指数</span>
                        <div class="fortune-bar-bg"><div class="fortune-bar-fill" style="width:70%;background:linear-gradient(90deg,#ffd700,#ff6b35);"></div></div>
                        <span class="fortune-value" style="color:#ffd700;">70分</span>
                    </div>
                    <div class="fortune-row">
                        <span class="fortune-label">健康指数</span>
                        <div class="fortune-bar-bg"><div class="fortune-bar-fill" style="width:90%;background:linear-gradient(90deg,#4cd964,#30d158);"></div></div>
                        <span class="fortune-value" style="color:#4cd964;">90分</span>
                    </div>
                </div>
                <div style="margin-top:0.6rem;font-size:0.7rem;color:rgba(255,255,255,0.55);line-height:1.6;">
                    💡 今日宜：签约、出行、求财、拜访贵人<br>
                    ⚠️ 今日忌：争吵、投资高风险项目、远行
                </div>
            </div>
            
            <div class="divider"></div>
            
            <!-- 更多功能 -->
            <div class="section-header"><h3>更多功能</h3><span class="section-more">全部 &gt;</span></div>
            <div class="module-grid">
                <div class="module-item" onclick="openModule('爱情配对')"><span class="icon">💕</span><span class="label">爱情配对</span></div>
                <div class="module-item" onclick="openModule('财运分析')"><span class="icon">💰</span><span class="label">财运分析</span></div>
                <div class="module-item" onclick="openModule('健康运势')"><span class="icon">❤️</span><span class="label">健康运势</span></div>
                <div class="module-item" onclick="openModule('周公解梦')"><span class="icon">🌙</span><span class="label">周公解梦</span></div>
            </div>
            <div class="module-grid" style="padding-top:0;">
                <div class="module-item" onclick="openModule('生肖运势')"><span class="icon">🐉</span><span class="label">生肖运势</span></div>
                <div class="module-item" onclick="openModule('八字合婚')"><span class="icon">💑</span><span class="label">八字合婚</span></div>
                <div class="module-item" onclick="openModule('抉择占卜')"><span class="icon">🤔</span><span class="label">抉择占卜</span></div>
                <div class="module-item" onclick="openModule('黄历查询')"><span class="icon">📅</span><span class="label">黄历查询</span></div>
            </div>
            <div class="module-grid" style="padding-top:0;">
                <div class="module-item new" onclick="openModule('AI智能算命')"><span class="icon">🤖</span><span class="label">AI智能算命</span></div>
                <div class="module-item new" onclick="openModule('星座运势')"><span class="icon">🌟</span><span class="label">星座运势</span></div>
                <div class="module-item" onclick="openModule('数字命理')"><span class="icon">🔢</span><span class="label">数字命理</span></div>
                <div class="module-item" onclick="openModule('事业运势')"><span class="icon">💼</span><span class="label">事业运势</span></div>
            </div>
            <div class="module-grid" style="padding-top:0;">
                <div class="module-item" onclick="openModule('子女缘分')"><span class="icon">👶</span><span class="label">子女缘分</span></div>
                <div class="module-item" onclick="openModule('家居风水')"><span class="icon">🏡</span><span class="label">家居风水</span></div>
                <div class="module-item" onclick="openModule('今日运势')"><span class="icon">📆</span><span class="label">今日运势</span></div>
                <div class="module-item" onclick="openModule('六爻占卜')"><span class="icon">🎲</span><span class="label">六爻占卜</span></div>
            </div>
            
            <div class="divider"></div>
            
            <!-- 高阶功能 -->
            <div class="section-header"><h3>高阶占卜</h3><span class="section-more">全部 &gt;</span></div>
            <div class="module-grid">
                <div class="module-item new" onclick="openModule('奇门遁甲')"><span class="icon">🌀</span><span class="label">奇门遁甲</span></div>
                <div class="module-item" onclick="openModule('大六壬')"><span class="icon">🌊</span><span class="label">大六壬</span></div>
                <div class="module-item" onclick="openModule('梅花易数')"><span class="icon">🌸</span><span class="label">梅花易数</span></div>
                <div class="module-item" onclick="openModule('小六壬')"><span class="icon">🎋</span><span class="label">小六壬</span></div>
            </div>
            <div class="module-grid" style="padding-top:0;">
                <div class="module-item" onclick="openModule('财神方位')"><span class="icon">🙏</span><span class="label">财神方位</span></div>
                <div class="module-item" onclick="openModule('韦特塔罗')"><span class="icon">🃏</span><span class="label">韦特塔罗</span></div>
                <div class="module-item" onclick="openModule('农历转换')"><span class="icon">🌙</span><span class="label">农历转换</span></div>
                <div class="module-item" onclick="openModule('择日吉凶')"><span class="icon">📿</span><span class="label">择日吉凶</span></div>
            </div>
            
            <div class="divider"></div>
            
            <!-- 知识库预览 -->
            <div class="section-header"><h3>命理知识库</h3><span class="section-more">更多 &gt;</span></div>
            <div class="kb-list">
                <div class="kb-card" onclick="toggleKbCard(this)">
                    <div class="kb-card-header">
                        <span class="kb-card-title">📚 八字命理基础知识</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p>八字，即生辰八字，是一个人出生时的干支历日期。年干和年支组成年柱，月干和月支组成月柱，日干和日支组成日柱，时干和时支组成时柱；一共四柱，四个干和四个支共八个字，故称八字。</p>
                            <p><strong style="color:#ffd700;">十天干：</strong>甲、乙、丙、丁、戊、己、庚、辛、壬、癸</p>
                            <p><strong style="color:#ffd700;">十二地支：</strong>子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥</p>
                            <p><strong style="color:#ffd700;">五行相生：</strong>金生水、水生木、木生火、火生土、土生金</p>
                            <p><strong style="color:#ffd700;">五行相克：</strong>金克木、木克土、土克水、水克火、火克金</p>
                            <span class="kb-tag">基础入门</span><span class="kb-tag">五行</span><span class="kb-tag">天干地支</span>
                        </div>
                    </div>
                </div>
                <div class="kb-card" onclick="toggleKbCard(this)">
                    <div class="kb-card-header">
                        <span class="kb-card-title">🔮 紫微斗数入门指南</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p>紫微斗数源于道家，是中国传统命理学最重要的支派之一。以人出生的年、月、日、时确定十二宫的位置，构成命盘，结合各宫的星群组合，推算一个人的命运。</p>
                            <p><strong style="color:#ffd700;">主星：</strong>紫微、天机、太阳、武曲、天同、廉贞（北斗）；天府、太阴、贪狼、巨门、天相、天梁、七杀、破军（南斗）</p>
                            <p><strong style="color:#ffd700;">十二宫：</strong>命宫、兄弟宫、夫妻宫、子女宫、财帛宫、疾厄宫、迁移宫、仆役宫、官禄宫、田宅宫、福德宫、父母宫</p>
                            <span class="kb-tag">紫微斗数</span><span class="kb-tag">命盘</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="padding:1.5rem 1rem;text-align:center;color:rgba(255,255,255,0.35);font-size:0.7rem;">
                <p>🌟 玄机算命网 · 专业命理测算平台</p>
                <p style="margin-top:0.3rem;">联系客服 · 意见反馈 · 关于我们</p>
            </div>
        </div>
        
        <!-- 生肖页面 -->
        <div class="page" id="page-zodiac">
            <div class="search-bar">
                <div class="search-inner" onclick="showToast('搜索生肖')">🔍 搜索你的生肖...</div>
            </div>
            <div class="section-header"><h3>十二生肖运势</h3></div>
            <div class="zodiac-grid">
                <div class="zodiac-item" onclick="showToast('鼠-运势开发中')"><span class="emoji">🐭</span><span class="name">鼠</span><span class="rank">排名第一</span></div>
                <div class="zodiac-item" onclick="showToast('牛-运势开发中')"><span class="emoji">🐮</span><span class="name">牛</span><span class="rank">排名第二</span></div>
                <div class="zodiac-item" onclick="showToast('虎-运势开发中')"><span class="emoji">🐯</span><span class="name">虎</span><span class="rank">排名第三</span></div>
                <div class="zodiac-item" onclick="showToast('兔-运势开发中')"><span class="emoji">🐰</span><span class="name">兔</span><span class="rank">排名第四</span></div>
                <div class="zodiac-item" onclick="showToast('龙-运势开发中')"><span class="emoji">🐲</span><span class="name">龙</span><span class="rank">排名第五</span></div>
                <div class="zodiac-item" onclick="showToast('蛇-运势开发中')"><span class="emoji">🐍</span><span class="name">蛇</span><span class="rank">排名第六</span></div>
                <div class="zodiac-item" onclick="showToast('马-运势开发中')"><span class="emoji">🐴</span><span class="name">马</span><span class="rank">排名第七</span></div>
                <div class="zodiac-item" onclick="showToast('羊-运势开发中')"><span class="emoji">🐑</span><span class="name">羊</span><span class="rank">排名第八</span></div>
                <div class="zodiac-item" onclick="showToast('猴-运势开发中')"><span class="emoji">🐵</span><span class="name">猴</span><span class="rank">排名第九</span></div>
                <div class="zodiac-item" onclick="showToast('鸡-运势开发中')"><span class="emoji">🐔</span><span class="name">鸡</span><span class="rank">排名第十</span></div>
                <div class="zodiac-item" onclick="showToast('狗-运势开发中')"><span class="emoji">🐶</span><span class="name">狗</span><span class="rank">排名十一</span></div>
                <div class="zodiac-item" onclick="showToast('猪-运势开发中')"><span class="emoji">🐷</span><span class="name">猪</span><span class="rank">排名十二</span></div>
            </div>
            <div style="padding:1rem;font-size:0.73rem;color:rgba(255,255,255,0.55);line-height:1.8;">
                <div style="background:rgba(255,215,0,0.08);border-radius:12px;padding:0.8rem;margin-top:0.5rem;">
                    <h4 style="color:#ffd700;margin-bottom:0.5rem;">📅 本周生肖运势排行</h4>
                    <p>🥇 龙：本周贵人运强，事业有突破</p>
                    <p>🥈 鼠：财运亨通，适合投资理财</p>
                    <p>🥉 蛇：桃花运旺，感情有进展</p>
                    <p>4️⃣ 牛：健康运佳，注意休息</p>
                    <p>5️⃣ 兔：学业运好，考试顺利</p>
                </div>
            </div>
        </div>
        
        <!-- 占卜页面 -->
        <div class="page" id="page-divination">
            <div class="search-bar">
                <div class="search-inner" onclick="showToast('搜索占卜类型')">🔍 搜索占卜方式...</div>
            </div>
            <div class="section-header"><h3>选择占卜方式</h3></div>
            <div class="divination-list">
                <div class="divination-item" onclick="openModule('塔罗牌')">
                    <span class="divination-icon">🀄</span>
                    <div class="divination-info">
                        <div class="divination-name">塔罗牌占卜</div>
                        <div class="divination-desc">78张牌解读命运奥秘 · 爱情/事业/运势</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('易经占卜')">
                    <span class="divination-icon">☯</span>
                    <div class="divination-info">
                        <div class="divination-name">易经六十四卦</div>
                        <div class="divination-desc">群经之首 · 阴阳变化 · 决策参考</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('六爻占卜')">
                    <span class="divination-icon">🎲</span>
                    <div class="divination-info">
                        <div class="divination-name">六爻占卜</div>
                        <div class="divination-desc">三钱起卦 · 六亲配六神 · 预测吉凶</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('梅花易数')">
                    <span class="divination-icon">🌸</span>
                    <div class="divination-info">
                        <div class="divination-name">梅花易数</div>
                        <div class="divination-desc">宋代邵雍创立 · 数字/时间/方位起卦</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('奇门遁甲')">
                    <span class="divination-icon">🌀</span>
                    <div class="divination-info">
                        <div class="divination-name">奇门遁甲</div>
                        <div class="divination-desc">帝王之术 · 择吉/风水/决策</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('大六壬')">
                    <span class="divination-icon">🌊</span>
                    <div class="divination-info">
                        <div class="divination-name">大六壬占卜</div>
                        <div class="divination-desc">三式之一 · 以月将加时起课</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('韦特塔罗')">
                    <span class="divination-icon">🃏</span>
                    <div class="divination-info">
                        <div class="divination-name">韦特塔罗牌</div>
                        <div class="divination-desc">最流行的塔罗体系 · 22张大阿卡纳</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
                <div class="divination-item" onclick="openModule('小六壬')">
                    <span class="divination-icon">🎋</span>
                    <div class="divination-info">
                        <div class="divination-name">小六壬速断</div>
                        <div class="divination-desc">左手掐指一算 · 快速简便</div>
                    </div>
                    <span class="divination-arrow">›</span>
                </div>
            </div>
        </div>
        
        <!-- 知识库页面 -->
        <div class="page" id="page-knowledge">
            <div class="search-bar">
                <div class="search-inner" onclick="showToast('搜索知识库')">🔍 搜索命理知识...</div>
            </div>
            <div class="section-header"><h3>命理知识库</h3><span class="section-more">共128篇文章</span></div>
            <div class="kb-list">
                <div class="kb-card" style="border-color:rgba(255,215,0,0.2);">
                    <div class="kb-card-header" onclick="toggleKbCard(this.parentElement)">
                        <span class="kb-card-title">📚 八字命理入门大全</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <h4 style="color:#ffd700;margin-bottom:0.5rem;">一、什么是八字</h4>
                            <p>八字，即生辰八字，是一个人出生时的干支历日期。年干和年支组成年柱，月干和月支组成月柱，日干和日支组成日柱，时干和时支组成时柱；一共四柱，四个干和四个支共八个字，故称八字，亦称四柱。</p>
                            <h4 style="color:#ffd700;margin:0.8rem 0 0.5rem;">二、天干地支</h4>
                            <p><strong>十天干：</strong>甲(jiǎ)、乙(yǐ)、丙(bǐng)、丁(dīng)、戊(wù)、己(jǐ)、庚(gēng)、辛(xīn)、壬(rén)、癸(guǐ)</p>
                            <p><strong>十二地支：</strong>子(zǐ)、丑(chǒu)、寅(yín)、卯(mǎo)、辰(chén)、巳(sì)、午(wǔ)、未(wèi)、申(shēn)、酉(yǒu)、戌(xū)、亥(hài)</p>
                            <h4 style="color:#ffd700;margin:0.8rem 0 0.5rem;">三、五行生克</h4>
                            <p><strong>五行相生：</strong>金生水、水生木、木生火、火生土、土生金。相生代表生发、促进、助长。</p>
                            <p><strong>五行相克：</strong>金克木、木克土、土克水、水克火、火克金。相克代表制约、克制、战胜。</p>
                            <h4 style="color:#ffd700;margin:0.8rem 0 0.5rem;">四、十神关系</h4>
                            <p>以日干为中心，与其他天干地支的生克关系定出：比肩、劫财、食神、伤官、正财、偏财、正官、七杀、正印、偏印，称为十神。</p>
                            <span class="kb-tag">基础</span><span class="kb-tag">八字</span><span class="kb-tag">必读</span>
                        </div>
                    </div>
                </div>
                <div class="kb-card">
                    <div class="kb-card-header" onclick="toggleKbCard(this.parentElement)">
                        <span class="kb-card-title">⭐ 紫微斗数详解</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p>紫微斗数，中国传统命理学的重要支派，以星宿配合十二宫的术数算命方法。</p>
                            <p><strong style="color:#ffd700;">十四主星：</strong></p>
                            <p>北斗七星：紫微、天机、太阳、武曲、天同、廉贞、天府</p>
                            <p>南斗七星：太阴、贪狼、巨门、天相、天梁、七杀、破军</p>
                            <p><strong style="color:#ffd700;">十二宫位：</strong>命宫、兄弟、夫妻、子女、财帛、疾厄、迁移、交友、官禄、田宅、福德、父母</p>
                            <span class="kb-tag">紫微斗数</span><span class="kb-tag">星曜</span>
                        </div>
                    </div>
                </div>
                <div class="kb-card">
                    <div class="kb-card-header" onclick="toggleKbCard(this.parentElement)">
                        <span class="kb-card-title">☯ 易经六十四卦解读</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p>《易经》是中国最古老的经典之一，被誉为"群经之首，大道之源"。</p>
                            <p><strong style="color:#ffd700;">八卦：</strong>乾、坤、震、巽、坎、离、艮、兑</p>
                            <p><strong style="color:#ffd700;">六十四卦精选：</strong></p>
                            <p>乾为天：刚健中正，自强不息</p>
                            <p>坤为地：柔顺伸展，厚德载物</p>
                            <p>水雷屯：起始维艰，终于亨通</p>
                            <p>山水蒙：启蒙奋发，循规蹈矩</p>
                            <span class="kb-tag">易经</span><span class="kb-tag">卦象</span>
                        </div>
                    </div>
                </div>
                <div class="kb-card">
                    <div class="kb-card-header" onclick="toggleKbCard(this.parentElement)">
                        <span class="kb-card-title">🏠 风水学入门</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p>风水是中国历史悠久的一门玄术，也称青乌、青囊，较为学术性的说法叫做堪舆。</p>
                            <p><strong style="color:#ffd700;">风水核心要素：</strong></p>
                            <p>1. 气：风水的核心是"气"，气乘风则散，界水则止</p>
                            <p>2. 阴阳：阴阳平衡是风水布局的基本原则</p>
                            <p>3. 五行：金木水火土五行相生相克</p>
                            <p>4. 八卦：用八卦方位来确定吉凶方位</p>
                            <p><strong style="color:#ffd700;">家居风水要点：</strong>大门朝向、客厅布局、卧室方位、厨房位置、卫生间朝向</p>
                            <span class="kb-tag">风水</span><span class="kb-tag">家居</span>
                        </div>
                    </div>
                </div>
                <div class="kb-card">
                    <div class="kb-card-header" onclick="toggleKbCard(this.parentElement)">
                        <span class="kb-card-title">👤 面相手相大全</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p><strong style="color:#ffd700;">面相十二宫：</strong>命宫、财帛宫、兄弟宫、田宅宫、男女宫、奴仆宫、妻妾宫、疾厄宫、迁移宫、官禄宫、福德宫、父母宫</p>
                            <p><strong style="color:#ffd700;">手相三大线：</strong>生命线、智慧线、感情线</p>
                            <p><strong style="color:#ffd700;">富贵手相特征：</strong>手掌厚实、指甲光亮、手指圆长、财运线清晰</p>
                            <span class="kb-tag">面相</span><span class="kb-tag">手相</span>
                        </div>
                    </div>
                </div>
                <div class="kb-card">
                    <div class="kb-card-header" onclick="toggleKbCard(this.parentElement)">
                        <span class="kb-card-title">📅 黄历宜忌知识</span>
                        <span class="kb-card-arrow">▼</span>
                    </div>
                    <div class="kb-card-body">
                        <div class="kb-card-content">
                            <p>黄历，又称老黄历、皇历，是在中国农历基础上产生出来的万年历。</p>
                            <p><strong style="color:#ffd700;">每日宜忌：</strong>宜祭祀、祈福、求嗣、开光、出行、嫁娶、安床等；忌安葬、开市、交易、立券等</p>
                            <p><strong style="color:#ffd700;">择日原则：</strong>以事为纲，以神为目；急事不拘</p>
                            <span class="kb-tag">黄历</span><span class="kb-tag">择日</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 底部标签栏 -->
    <div class="tab-bar">
        <div class="tab-item active" onclick="switchTab('home', this)">
            <span class="tab-icon">🏠</span>
            <span>首页</span>
        </div>
        <div class="tab-item" onclick="switchTab('zodiac', this)">
            <span class="tab-icon">🐉</span>
            <span>生肖</span>
        </div>
        <div class="tab-item" onclick="switchTab('divination', this)">
            <span class="tab-icon">🔮</span>
            <span>占卜</span>
        </div>
        <div class="tab-item" onclick="switchTab('knowledge', this)">
            <span class="tab-icon">📚</span>
            <span>知识</span>
        </div>
    </div>
</div>
</div>

<script>
// 更新状态栏时间
function updateStatusTime() {
    const now = new Date();
    const h = now.getHours().toString().padStart(2, '0');
    const m = now.getMinutes().toString().padStart(2, '0');
    document.getElementById('statusTime').textContent = h + ':' + m;
}
setInterval(updateStatusTime, 1000);
updateStatusTime();

// 电池状态
var batteryLevel = 78;
function initBattery() {
    if (navigator.getBattery) {
        navigator.getBattery().then(function(b) {
            batteryLevel = Math.round(b.level * 100);
            updateBatteryUI(batteryLevel);
            b.addEventListener('levelchange', function() {
                batteryLevel = Math.round(b.level * 100);
                updateBatteryUI(batteryLevel);
            });
        });
    } else {
        batteryLevel = 65 + Math.floor(Math.random() * 30);
        updateBatteryUI(batteryLevel);
        setInterval(function() {
            batteryLevel = Math.max(15, Math.min(100, batteryLevel + (Math.random() > 0.5 ? 1 : -1)));
            updateBatteryUI(batteryLevel);
        }, 30000);
    }
}
function updateBatteryUI(level) {
    var fill = document.getElementById('battFill');
    var text = document.getElementById('battText');
    fill.style.width = level + '%';
    text.textContent = level + '%';
    fill.classList.remove('low', 'medium');
    if (level <= 20) fill.classList.add('low');
    else if (level <= 50) fill.classList.add('medium');
}
initBattery();

// 信号格
function updateSignal() {
    var bars = document.querySelectorAll('#signalBars .signal-bar');
    var rand = Math.random();
    bars.forEach(function(bar, i) {
        bar.classList.remove('weak', 'medium', 'off');
        if (rand < 0.15) {
            if (i > 1) bar.classList.add('off');
        } else if (rand < 0.35) {
            if (i > 2) bar.classList.add('medium');
        }
    });
}
setInterval(updateSignal, 5000);
updateSignal();

// 网络类型
function updateNetType() {
    var nt = document.getElementById('netType');
    if (navigator.connection) {
        var eff = navigator.connection.effectiveType;
        if (eff === '4g') nt.textContent = '4G';
        else if (eff === '3g') nt.textContent = '3G';
        else if (eff === 'slow-2g' || eff === '2g') nt.textContent = '2G';
        else nt.textContent = '5G';
    }
}
updateNetType();

// 在线人数
function updateOnlineCount() {
    var base = 13000 + Math.floor(Math.random() * 1000);
    document.getElementById('onlineCount').textContent = base.toLocaleString();
}
setInterval(updateOnlineCount, 8000);
updateOnlineCount();

// 标签切换
function switchTab(page, el) {
    document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
    document.querySelectorAll('.tab-item').forEach(function(t) { t.classList.remove('active'); });
    var target = document.getElementById('page-' + page);
    if (target) target.classList.add('active');
    if (el) el.classList.add('active');
}
// 知识库卡片展开
function toggleKbCard(card) {
    card.classList.toggle('expanded');
}

// Toast
function showToast(msg) {
    var t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function() { t.remove(); }, 2000);
}

// 模块点击
function openModule(name) {
    showToast(name + ' - 功能开发中，敬请期待...');
}

document.addEventListener('DOMContentLoaded', function() {
    updateStatusTime();
    initBattery();
});
</script>
</body>
</html>"""

with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('DONE: index.html written successfully')
print('File size:', len(content), 'bytes')
