#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover">
<title>玄机算命网</title>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#1a1a2e">
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;overflow:hidden;width:100vw;height:100vh;}
.phone-frame{width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;background:linear-gradient(135deg,#0a0a0a,#1a1a2e,#0a0a0a);}
.app{width:100%;max-width:420px;height:100vh;display:flex;flex-direction:column;background:linear-gradient(180deg,#0f0c29,#1a1a2e 30%,#16213e 70%,#0a0a1a);position:relative;overflow:hidden;box-shadow:0 0 60px rgba(255,215,0,0.08);}
.status-bar{display:flex;justify-content:space-between;align-items:center;padding:0.25rem 1rem;background:rgba(0,0,0,0.65);font-size:0.72rem;color:#fff;flex-shrink:0;height:27px;z-index:999;}
.status-bar .t{font-weight:700;font-size:0.82rem;}
.signal{display:flex;align-items:flex-end;gap:1.5px;height:13px;margin-right:4px;}
.signal i{display:block;width:3px;background:#4cd964;border-radius:1px;transition:all 0.3s;}
.signal i:nth-child(1){height:4px;}
.signal i:nth-child(2){height:6px;}
.signal i:nth-child(3){height:8px;}
.signal i:nth-child(4){height:11px;}
.signal i.w{background:#ff3b30;}
.signal i.m{background:#ffcc00;}
.signal i.o{background:rgba(255,255,255,0.2);}
.battery{display:flex;align-items:center;gap:3px;margin-left:4px;}
.bat-body{width:21px;height:10px;border:1.5px solid #fff;border-radius:2px;position:relative;display:flex;align-items:center;padding:1.5px;}
.bat-body:after{content:'';position:absolute;right:-3px;top:2.5px;width:1.5px;height:4px;background:#fff;border-radius:0 1px 1px 0;}
.bat-fill{height:100%;border-radius:1px;background:#4cd964;transition:all 0.5s;}
.bat-fill.low{background:#ff3b30;}
.bat-fill.mid{background:#ffcc00;}
.bat-txt{font-size:0.6rem;min-width:24px;text-align:right;}
.header{text-align:center;padding:0.7rem 1rem 0.5rem;background:linear-gradient(180deg,rgba(0,0,0,0.7),transparent);border-bottom:1px solid rgba(255,215,0,0.12);flex-shrink:0;}
.header h1{font-size:1.25rem;font-weight:800;background:linear-gradient(90deg,#ffd700,#ff6b35,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:2px;}
.header .sub{font-size:0.63rem;color:rgba(255,255,255,0.4);margin-top:2px;}
.stats{display:flex;justify-content:center;align-items:center;gap:0.7rem;padding:0.3rem 1rem;font-size:0.65rem;color:rgba(255,255,255,0.55);background:rgba(255,215,0,0.05);flex-shrink:0;}
.stats .dot{width:5px;height:5px;border-radius:50%;background:#4cd964;animation:pulse 1.5s infinite;}
@keyframes pulse{0%{opacity:1;}100%{opacity:0.4;}}
.notice{display:flex;align-items:center;gap:0.4rem;padding:0.3rem 1rem;font-size:0.64rem;color:#ffd700;background:rgba(255,215,0,0.07);overflow:hidden;flex-shrink:0;border-bottom:1px solid rgba(255,215,0,0.06);}
.notice span{white-space:nowrap;animation:scroll 22s linear infinite;}
@keyframes scroll{0%{transform:translateX(100%);}100%{transform:translateX(-100%);}}
.views{position:relative;flex:1;overflow:hidden;}
.page{position:absolute;top:0;left:0;width:100%;height:100%;overflow-y:auto;display:none;flex-direction:column;-webkit-overflow-scrolling:touch;}
.page.active{display:flex;}
.page::-webkit-scrollbar{display:none;}
.search{padding:0.55rem 1rem;flex-shrink:0;}
.search-inner{display:flex;align-items:center;gap:0.5rem;background:rgba(255,255,255,0.06);border-radius:20px;padding:0.5rem 1rem;font-size:0.76rem;color:rgba(255,255,255,0.35);border:1px solid rgba(255,255,255,0.04);}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.5rem;padding:0.5rem 1rem;flex-shrink:0;}
.item{display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(255,255,255,0.045);border-radius:12px;padding:0.65rem 0.15rem;gap:0.3rem;cursor:pointer;border:1px solid rgba(255,215,0,0.06);transition:all 0.15s;position:relative;overflow:hidden;}
.item:active{transform:scale(0.93);background:rgba(255,215,0,0.12);}
.item .ic{font-size:1.5rem;}
.item .lb{font-size:0.62rem;color:rgba(255,255,255,0.75);text-align:center;line-height:1.2;font-weight:500;}
.sec{padding:0.8rem 1rem 0.4rem;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.sec h3{font-size:0.9rem;color:#ffd700;font-weight:700;display:flex;align-items:center;gap:0.35rem;}
.sec h3:before{content:'';display:inline-block;width:3px;height:13px;background:linear-gradient(180deg,#ffd700,#ff6b35);border-radius:2px;}
.sec .more{font-size:0.68rem;color:rgba(255,255,255,0.35);}
.card{margin:0.5rem 1rem;padding:0.9rem;background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,107,53,0.06));border-radius:12px;border:1px solid rgba(255,215,0,0.15);flex-shrink:0;}
.card h4{font-size:0.83rem;color:#ffd700;margin-bottom:0.5rem;}
.card p{font-size:0.73rem;color:rgba(255,255,255,0.65);line-height:1.7;}
.kb-list{padding:0.5rem 1rem;flex-shrink:0;}
.kb{background:rgba(255,255,255,0.04);border-radius:12px;margin-bottom:0.55rem;overflow:hidden;border:1px solid rgba(255,255,255,0.05);}
.kb-h{display:flex;justify-content:space-between;align-items:center;padding:0.75rem 1rem;cursor:pointer;}
.kb-t{font-size:0.8rem;color:rgba(255,255,255,0.85);font-weight:600;}
.kb-ar{font-size:0.65rem;color:rgba(255,255,255,0.35);transition:transform 0.3s;}
.kb.expanded .kb-ar{transform:rotate(180deg);}
.kb-b{max-height:0;overflow:hidden;transition:max-height 0.35s ease,padding 0.3s;padding:0 1rem;}
.kb.expanded .kb-b{max-height:600px;padding:0 1rem 0.9rem;}
.kb-c{font-size:0.72rem;color:rgba(255,255,255,0.58);line-height:1.75;}
.kb-c p{margin-bottom:0.45rem;}
.tag{display:inline-block;padding:2px 7px;background:rgba(255,215,0,0.08);color:#ffd700;border-radius:5px;font-size:0.58rem;margin:2px 2px 2px 0;}
.z-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.55rem;padding:0.5rem 1rem;}
.z-item{display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(255,255,255,0.05);border-radius:12px;padding:0.75rem 0.2rem;gap:0.25rem;cursor:pointer;border:1px solid rgba(255,215,0,0.06);transition:all 0.15s;}
.z-item:active{transform:scale(0.93);background:rgba(255,215,0,0.12);}
.z-item .em{font-size:1.7rem;}
.z-item .nm{font-size:0.7rem;color:rgba(255,255,255,0.8);font-weight:600;}
.z-item .rk{font-size:0.58rem;color:rgba(255,255,255,0.4;}
.d-list{padding:0.5rem 1rem;}
.d-item{display:flex;align-items:center;gap:0.75rem;padding:0.85rem;margin-bottom:0.55rem;background:rgba(255,255,255,0.05);border-radius:12px;border:1px solid rgba(255,255,255,0.05);cursor:pointer;transition:all 0.15s;}
.d-item:active{background:rgba(255,215,0,0.08);transform:scale(0.975);}
.d-ic{font-size:1.9rem;}
.d-info{flex:1;}
.d-nm{font-size:0.83rem;color:rgba(255,255,255,0.88);font-weight:600;}
.d-ds{font-size:0.66rem;color:rgba(255,255,255,0.48);margin-top:3px;}
.d-ar{color:rgba(255,255,255,0.28);font-size:0.75rem;}
.tab-bar{display:flex;justify-content:space-around;align-items:center;padding:0.3rem 0 0.5rem;flex-shrink:0;background:rgba(0,0,0,0.82);backdrop-filter:blur(28px);border-top:1px solid rgba(255,255,255,0.07);z-index:999;}
.tab{display:flex;flex-direction:column;align-items:center;gap:0.12rem;color:rgba(255,255,255,0.3);font-size:0.56rem;cursor:pointer;padding:0.2rem 0.85rem;border-radius:8px;transition:all 0.15s;}
.tab .ti{font-size:1.15rem;transition:all 0.15s;}
.tab.active{color:#ffd700;}
.tab.active .ti{transform:scale(1.08);}
hr{height:1px;background:rgba(255,255,255,0.05);margin:0.25rem 1rem;border:none;flex-shrink:0;}
.toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);color:#fff;padding:0.75rem 1.4rem;border-radius:10px;font-size:0.83rem;z-index:99999;pointer-events:none;animation:tin 0.25s ease;}
@keyframes tin{from{opacity:0;transform:translate(-50%,-50%) scale(0.9);}to{opacity:1;transform:translate(-50%,-50%) scale(1);}}
</style>
</head>
<body>
<div class="phone-frame">
<div class="app">
  <div class="status-bar">
    <span id="carrier">中国移动</span>
    <span class="t" id="clk">11:46</span>
    <div style="display:flex;align-items:center;">
      <div class="signal" id="sig"><i></i><i></i><i></i><i></i></div>
      <span id="ntype" style="font-size:0.6rem;opacity:0.65;margin:0 2px;">4G</span>
      <div class="battery">
        <div class="bat-body"><div class="bat-fill" id="bfill" style="width:78%;"></div></div>
        <span class="bat-txt" id="btxt">78%</span>
      </div>
    </div>
  </div>
  <div class="header">
    <h1>玄机算命网</h1>
    <div class="sub">测命理 · 知天命 · 改运势</div>
  </div>
  <div class="stats">
    <div class="dot"></div>
    <span>在线 <strong id="oc" style="color:#ffd700;">13,842</strong> 人</span>
    <span style="margin-left:auto;font-size:0.6rem;opacity:0.35;">今日测算 45,231次</span>
  </div>
  <div class="notice"><span>📢</span><span>新用户免费测算3次 · 关注公众号领积分 · 大师一对一解读 · 每日签到送VIP</span></div>
  <div class="views">
    <!-- 首页 -->
    <div class="page active" id="pg-home">
      <div class="search"><div class="search-inner" onclick="toast('搜索开发ing')">🔍 搜索算命、八字、风水...</div></div>
      <div class="sec"><h3>热门测算</h3><span class="more">全部 ></span></div>
      <div class="grid">
        <div class="item" onclick="openMod('八字算命')"><span class="ic">📊</span><span class="lb">八字算命</span></div>
        <div class="item" onclick="openMod('紫微斗数')"><span class="ic">⭐</span><span class="lb">紫微斗数</span></div>
        <div class="item" onclick="openMod('塔罗牌')"><span class="ic">🀄</span><span class="lb">塔罗牌</span></div>
        <div class="item" onclick="openMod('易经占卜')"><span class="ic">☯</span><span class="lb">易经占卜</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openMod('姓名测试')"><span class="ic">📝</span><span class="lb">姓名测试</span></div>
        <div class="item" onclick="openMod('风水布局')"><span class="ic">🏠</span><span class="lb">风水布局</span></div>
        <div class="item" onclick="openMod('面相分析')"><span class="ic">👤</span><span class="lb">面相分析</span></div>
        <div class="item" onclick="openMod('手相解读')"><span class="ic">✋</span><span class="lb">手相解读</span></div>
      </div>
      <hr>
      <div class="sec"><h3>今日运势</h3><span class="more">详情 ></span></div>
      <div class="card">
        <h4>📅 今日综合运势</h4>
        <p>综合运：★★★★☆ 82分<br>爱情运：★★★☆☆ 75分<br>事业运：★★★★★ 88分<br>财运：★★★☆☆ 70分<br>健康运：★★★★★ 90分</p>
        <p style="margin-top:0.5rem;font-size:0.68rem;color:rgba(255,255,255,0.5);">宜：签约 出行 求财 | 忌：争吵 高风险投资</p>
      </div>
      <hr>
      <div class="sec"><h3>更多功能</h3><span class="more">全部 ></span></div>
      <div class="grid">
        <div class="item" onclick="openMod('爱情配对')"><span class="ic">💕</span><span class="lb">爱情配对</span></div>
        <div class="item" onclick="openMod('财运分析')"><span class="ic">💰</span><span class="lb">财运分析</span></div>
        <div class="item" onclick="openMod('健康运势')"><span class="ic">❤️</span><span class="lb">健康运势</span></div>
        <div class="item" onclick="openMod('周公解梦')"><span class="ic">🌙</span><span class="lb">周公解梦</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openMod('生肖运势')"><span class="ic">🐉</span><span class="lb">生肖运势</span></div>
        <div class="item" onclick="openMod('八字合婚')"><span class="ic">💑</span><span class="lb">八字合婚</span></div>
        <div class="item" onclick="openMod('AI算命')"><span class="ic">🤖</span><span class="lb">AI智能算命</span></div>
        <div class="item" onclick="openMod('星座运势')"><span class="ic">🌟</span><span class="lb">星座运势</span></div>
      </div>
      <div class="grid" style="padding-top:0;">
        <div class="item" onclick="openMod('六爻占卜')"><span class="ic">🎲</span><span class="lb">六爻占卜</span></div>
        <div class="item" onclick="openMod('奇门遁甲')"><span class="ic">🌀</span><span class="lb">奇门遁甲</span></div>
        <div class="item" onclick="openMod('梅花易数')"><span class="ic">🌸</span><span class="lb">梅花易数</span></div>
        <div class="item" onclick="openMod('黄历查询')"><span class="ic">📅</span><span class="lb">黄历查询</span></div>
      </div>
      <hr>
      <div class="sec"><h3>命理知识</h3><span class="more">更多 ></span></div>
      <div class="kb-list">
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">📚 八字命理基础</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p>八字即生辰八字，是一个人出生时的干支历日期。年干支为年柱，月干支为月柱，日干支为日柱，时干支为时柱；共四柱八字。</p><p><strong style="color:#ffd700;">十天干：</strong>甲、乙、丙、丁、戊、己、庚、辛、壬、癸</p><p><strong style="color:#ffd700;">十二地支：</strong>子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥</p><span class="tag">基础</span><span class="tag">八字</span></div></div>
        </div>
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">⭐ 紫微斗数入门</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p>紫微斗数源于道家，是中国传统命理学最重要的支派之一。以人出生年月日时确定十二宫位置，构成命盘。</p><p><strong style="color:#ffd700;">十四主星：</strong>紫微、天机、太阳、武曲、天同、廉贞、天府、太阴、贪狼、巨门、天相、天梁、七杀、破军</p><span class="tag">紫微</span><span class="tag">命盘</span></div></div>
        </div>
      </div>
      <div style="padding:1.2rem;text-align:center;color:rgba(255,255,255,0.3);font-size:0.65rem;">玄机算命网 · 专业命理平台</div>
    </div>
    <!-- 生肖页 -->
    <div class="page" id="pg-zodiac">
      <div class="search"><div class="search-inner" onclick="toast('搜索生肖')">🔍 搜索生肖...</div></div>
      <div class="sec"><h3>十二生肖</h3></div>
      <div class="z-grid">
        <div class="z-item" onclick="toast('鼠')"><span class="em">🐭</span><span class="nm">鼠</span><span class="rk">第一名</span></div>
        <div class="z-item" onclick="toast('牛')"><span class="em">🐮</span><span class="nm">牛</span><span class="rk">第二名</span></div>
        <div class="z-item" onclick="toast('虎')"><span class="em">🐯</span><span class="nm">虎</span><span class="rk">第三名</span></div>
        <div class="z-item" onclick="toast('兔')"><span class="em">🐰</span><span class="nm">兔</span><span class="rk">第四名</span></div>
        <div class="z-item" onclick="toast('龙')"><span class="em">🐲</span><span class="nm">龙</span><span class="rk">第五名</span></div>
        <div class="z-item" onclick="toast('蛇')"><span class="em">🐍</span><span class="nm">蛇</span><span class="rk">第六名</span></div>
        <div class="z-item" onclick="toast('马')"><span class="em">🐴</span><span class="nm">马</span><span class="rk">第七名</span></div>
        <div class="z-item" onclick="toast('羊')"><span class="em">🐑</span><span class="nm">羊</span><span class="rk">第八名</span></div>
        <div class="z-item" onclick="toast('猴')"><span class="em">🐵</span><span class="nm">猴</span><span class="rk">第九名</span></div>
        <div class="z-item" onclick="toast('鸡')"><span class="em">🐔</span><span class="nm">鸡</span><span class="rk">第十名</span></div>
        <div class="z-item" onclick="toast('狗')"><span class="em">🐶</span><span class="nm">狗</span><span class="rk">十一名</span></div>
        <div class="z-item" onclick="toast('猪')"><span class="em">🐷</span><span class="nm">猪</span><span class="rk">十二名</span></div>
      </div>
      <div style="padding:0.8rem;font-size:0.72rem;color:rgba(255,255,255,0.55);line-height:1.8;">
        <div style="background:rgba(255,215,0,0.07);border-radius:10px;padding:0.7rem;">
          <strong style="color:#ffd700;">本周排行：</strong><br>
          🥇 龙：贵人运强<br>
          🥈 鼠：财运亨通<br>
          🥉 蛇：桃花运旺
        </div>
      </div>
    </div>
    <!-- 占卜页 -->
    <div class="page" id="pg-div">
      <div class="search"><div class="search-inner" onclick="toast('搜索占卜')">🔍 搜索占卜...</div></div>
      <div class="sec"><h3>选择占卜方式</h3></div>
      <div class="d-list">
        <div class="d-item" onclick="openMod('塔罗牌')"><span class="d-ic">🀄</span><div class="d-info"><div class="d-nm">塔罗牌占卜</div><div class="d-ds">78张牌 · 爱情/事业/运势</div></div><span class="d-ar">›</span></div>
        <div class="d-item" onclick="openMod('易经占卜')"><span class="d-ic">☯</span><div class="d-info"><div class="d-nm">易经六十四卦</div><div class="d-ds">群经之首 · 阴阳变化</div></div><span class="d-ar">›</span></div>
        <div class="d-item" onclick="openMod('六爻占卜')"><span class="d-ic">🎲</span><div class="d-info"><div class="d-nm">六爻占卜</div><div class="d-ds">三钱起卦 · 预测吉凶</div></div><span class="d-ar">›</span></div>
        <div class="d-item" onclick="openMod('梅花易数')"><span class="d-ic">🌸</span><div class="d-info"><div class="d-nm">梅花易数</div><div class="d-ds">数字/时间/方位起卦</div></div><span class="d-ar">›</span></div>
        <div class="d-item" onclick="openMod('奇门遁甲')"><span class="d-ic">🌀</span><div class="d-info"><div class="d-nm">奇门遁甲</div><div class="d-ds">帝王之术 · 择吉决策</div></div><span class="d-ar">›</span></div>
        <div class="d-item" onclick="openMod('大六壬')"><span class="d-ic">🌊</span><div class="d-info"><div class="d-nm">大六壬占卜</div><div class="d-ds">三式之一 · 精准预测</div></div><span class="d-ar">›</span></div>
      </div>
    </div>
    <!-- 知识页 -->
    <div class="page" id="pg-kb">
      <div class="search"><div class="search-inner" onclick="toast('搜索知识')">🔍 搜索知识...</div></div>
      <div class="sec"><h3>知识库</h3><span class="more">共128篇</span></div>
      <div class="kb-list">
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">📚 八字命理大全</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p><strong style="color:#ffd700;">一、什么是八字</strong></p><p>八字是一个人出生时的干支历日期，共四柱八个字，用以推算命运。</p><p><strong style="color:#ffd700;">二、五行生克</strong></p><p>相生：金生水、水生木、木生火、火生土、土生金</p><p>相克：金克木、木克土、土克水、水克火、火克金</p><span class="tag">八字</span><span class="tag">基础</span></div></div>
        </div>
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">⭐ 紫微斗数详解</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p>紫微斗数以星宿配合十二宫推算命运，是重要的命理学支派。</p><p><strong style="color:#ffd700;">十二宫：</strong>命宫、兄弟、夫妻、子女、财帛、疾厄、迁移、交友、官禄、田宅、福德、父母</p><span class="tag">紫微</span><span class="tag">星曜</span></div></div>
        </div>
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">☯ 易经六十四卦</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p>《易经》是群经之首，大道之源。八卦相叠成六十四卦。</p><p><strong style="color:#ffd700;">八卦：</strong>乾、坤、震、巽、坎、离、艮、兑</p><p><strong style="color:#ffd700;">精选卦象：</strong>乾为天（自强不息）、坤为地（厚德载物）</p><span class="tag">易经</span><span class="tag">卦象</span></div></div>
        </div>
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">🏠 风水学入门</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p>风水核心是"气"，气乘风则散，界水则止。讲究阴阳平衡、五行相生。</p><p><strong style="color:#ffd700;">家居风水要点：</strong>大门朝向、客厅布局、卧室方位、厨房位置</p><span class="tag">风水</span><span class="tag">家居</span></div></div>
        </div>
        <div class="kb" onclick="this.classList.toggle('expanded')">
          <div class="kb-h"><span class="kb-t">👤 面相手相大全</span><span class="kb-ar">▼</span></div>
          <div class="kb-b"><div class="kb-c"><p><strong style="color:#ffd700;">面相十二宫：</strong>命宫、财帛、兄弟、田宅、男女、奴仆、妻妾、疾厄、迁移、官禄、福德、父母</p><p><strong style="color:#ffd700;">手相三主线：</strong>生命线、智慧线、感情线</p><span class="tag">面相</span><span class="tag">手相</span></div></div>
        </div>
      </div>
    </div>
  </div>
  <div class="tab-bar">
    <div class="tab active" onclick="switchTab('home',this)"><span class="ti">🏠</span>首页</div>
    <div class="tab" onclick="switchTab('zodiac',this)"><span class="ti">🐉</span>生肖</div>
    <div class="tab" onclick="switchTab('div',this)"><span class="ti">🔮</span>占卜</div>
    <div class="tab" onclick="switchTab('kb',this)"><span class="ti">📚</span>知识</div>
  </div>
</div>
</div>
<script>
function updateClock(){var d=new Date(),h=d.getHours().toString().padStart(2,'0'),m=d.getMinutes().toString().padStart(2,'0');document.getElementById('clk').textContent=h+':'+m;}
setInterval(updateClock,1000);updateClock();
var bat=78;
function updateBat(){document.getElementById('bfill').style.width=bat+'%';document.getElementById('btxt').textContent=bat+'%';var f=document.getElementById('bfill');f.classList.remove('low','mid');if(bat<=20)f.classList.add('low');else if(bat<=50)f.classList.add('mid');}
if(navigator.getBattery){navigator.getBattery().then(function(b){bat=Math.round(b.level*100);updateBat();b.addEventListener('levelchange',function(){bat=Math.round(b.level*100);updateBat();});});}else{setInterval(function(){bat=Math.max(15,Math.min(100,bat+(Math.random()>0.5?1:-1)));updateBat();},30000);}
updateBat();
function updateSig(){var bars=document.querySelectorAll('#sig i');var r=Math.random();bars.forEach(function(b,i){b.classList.remove('w','m','o');if(r<0.12&&i>1)b.classList.add('o');else if(r<0.3&&i>2)b.classList.add('m');});}
setInterval(updateSig,5000);updateSig();
if(navigator.connection){navigator.connection.addEventListener('change',function(){var e=navigator.connection.effectiveType;document.getElementById('ntype').textContent=e==='4g'?'4G':e==='3g'?'3G':e==='2g'?'2G':'5G';});}
function updateOC(){document.getElementById('oc').textContent=(13000+Math.floor(Math.random()*1000)).toLocaleString();}
setInterval(updateOC,8000);updateOC();
function switchTab(p,t){document.querySelectorAll('.page').forEach(function(x){x.classList.remove('active');});document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('active');});var pg=document.getElementById('pg-'+p);if(pg)pg.classList.add('active');if(t)t.classList.add('active');}
function toast(m){var t=document.createElement('div');t.className='toast';t.textContent=m;document.body.appendChild(t);setTimeout(function(){t.remove();},2000);}
function openMod(n){toast(n+' - 开发中...');}
</script>
</body>
</html>"""

with open('/workspace/index.html','w',encoding='utf-8') as f:
    f.write(html)

print('OK: written', len(html), 'bytes')
