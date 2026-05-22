import os, json, sys

def build_html():
    # 逐步构建 HTML
    parts = []
    
    # === 第1部分：HTML头部 + CSS ===
    p1 = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>玄机算命网</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
        body { font-family:sans-serif; background:#0a0a1a; color:#fff; }
        .phone-simulator { width:100vw; height:100vh; display:flex; justify-content:center; align-items:center; background:#000; }
        .app { width:100%; max-width:420px; height:100vh; display:flex; flex-direction:column; background:linear-gradient(180deg,#1a1a2e,#0a0a1a); position:relative; overflow:hidden; }
        .ios-status-bar { display:flex; justify-content:space-between; padding:0.3rem 1rem; background:rgba(0,0,0,0.5); font-size:0.75rem; }
        .module-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.6rem; padding:0.5rem 1rem; }
        .module-item { background:rgba(255,255,255,0.05); border-radius:12px; padding:0.6rem; text-align:center; cursor:pointer; border:1px solid rgba(255,215,0,0.1); }
        .page { display:none; }
        .page.active { display:flex; flex-direction:column; }
    </style>
</head>
<body>
<div class="phone-simulator">
<div class="app">
    <div class="ios-status-bar">
        <span>中国移动</span>
        <span id="statusTime">11:16</span>
        <span>4G</span>
        <span id="battText">78%</span>
    </div>
    <div style="text-align:center; padding:1rem; background:rgba(0,0,0,0.6);">
        <h1>🔮 玄机算命网</h1>
    </div>
    <div class="page active" id="page-home">
        <div class="module-grid">
'''
    parts.append(p1)
    
    # === 第2部分：32个功能模块 ===
    modules = [
        ('📊','八字算命'), ('⭐','紫微斗数'), ('🀄','塔罗牌'), ('☯','易经占卜'),
        ('📝','姓名测试'), ('🏠','风水布局'), ('👤','面相分析'), ('✋','手相解读'),
        ('💕','爱情配对'), ('💰','财运分析'), ('❤️','健康运势'), ('🌙','周公解梦'),
        ('🐉','生肖运势'), ('💑','八字合婚'), ('🤔','抉择占卜'), ('📅','黄历查询'),
        ('🎋','时辰八字'), ('🤖','AI智能算命'), ('🔢','数字命理'), ('🌟','星座运势'),
        ('👶','子女缘分'), ('🏡','家居风水'), ('📆','今日运势'), ('🎲','六爻占卜'),
        ('🌀','奇门遁甲'), ('🌊','大六壬'), ('🌸','梅花易数'), ('🌙','农历转换'),
        ('🙏','财神方位'), ('🃏','韦特塔罗'), ('👥','算命社区'),
        ('💼','事业运势'), ('🏠','阴宅风水'), ('🔮','奇门遁甲'), ('📿','起名改名'),
    ]
    
    for i, (icon, name) in enumerate(modules):
        parts.append(f'            <div class="module-item">${icon}<br><small>{name}</small></div>\n')
        if (i+1) % 4 == 0 and i < len(modules)-1:
            parts.append('        </div>\n        <div class="module-grid">\n')
    
    # 关闭最后一个 grid
    parts.append('''        </div>
        
        <div style="padding:1rem;">
            <h3 style="color:#ffd700; margin-bottom:0.5rem;">✨ 今日推荐</h3>
            <div style="background:rgba(255,215,0,0.1); border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
                <h4 style="color:#ffd700;">📊 免费八字精批</h4>
                <p style="font-size:0.8rem; color:rgba(255,255,255,0.7);">根据出生年月日时，精准排盘分析。</p>
            </div>
            <div style="background:rgba(255,215,0,0.1); border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
                <h4 style="color:#ffd700;">⭐ 紫微斗数排盘</h4>
                <p style="font-size:0.8rem; color:rgba(255,255,255,0.7);">千年帝王之学，十四主星深度解读。</p>
            </div>
        </div>
        
        <div style="padding:1rem;">
            <h3 style="color:#ffd700; margin-bottom:0.5rem;">📚 算命知识库</h3>
            <details style="background:rgba(255,255,255,0.05); border-radius:12px; padding:0.8rem; margin-bottom:0.5rem;">
                <summary style="cursor:pointer; font-size:0.85rem;">📖 八字命理基础知识</summary>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.6); line-height:1.8; margin-top:0.5rem;">
                    <p><strong>什么是八字？</strong>八字即生辰八字，用年、月、日、时四柱干支表示。</p>
                    <p><strong>五行生克：</strong>金生水、水生木、木生火、火生土、土生金。</p>
                    <p><strong>十神体系：</strong>正官、偏官、正印、偏印、正财、偏财、食神、伤官、比肩、劫财。</p>
                </div>
            </details>
            <details style="background:rgba(255,255,255,0.05); border-radius:12px; padding:0.8rem; margin-bottom:.5rem;">
                <summary style="cursor:pointer; font-size:0.85rem;">☯ 易经八卦入门</summary>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.6); line-height:1.8; margin-top:0.5rem;">
                    <p><strong>八卦：</strong>乾☰、坤☷、震☳、巽☴、坎☵、离☲、艮☶、兑☱。</p>
                    <p><strong>占卜方法：</strong>金钱卦、蓍草占、梅花易数。</p>
                </div>
            </details>
            <details style="background:rgba(255,255,255,0.05); border-radius:12px; padding:0.8rem; margin-bottom:0.5rem;">
                <summary style="cursor:pointer; font-size:0.85rem;">🏠 风水学基础</summary>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.6); line-height:1.8; margin-top:0.5rem;">
                    <p><strong>风水核心：</strong>藏风聚气，趋吉避凶。</p>
                    <p><strong>家居要点：</strong>入户门不对卫生间、床头不靠窗、厨房不居中宫。</p>
                </div>
            </details>
        </div>
        
        <div style="padding:1rem; font-size:0.7rem; color:rgba(255,255,255,0.4); text-align:center;">
            © 2026 玄机算命网 · 仅供娱乐参考
        </div>
    </div>
    
    <div class="tab-bar" style="display:flex; justify-content:space-around; padding:0.5rem; background:rgba(0,0,0,0.8); position:fixed; bottom:0; width:100%; max-width:420px;">
        <div style="text-align:center; color:#ffd700; cursor:pointer;">🏠<br><small>首页</small></div>
        <div style="text-align:center; cursor:pointer;">🐉<br><small>生肖</small></div>
        <div style="text-align:center; cursor:pointer;">🔮<br><small>占卜</small></div>
        <div style="text-align:center; cursor:pointer;">📚<br><small>知识</small></div>
    </div>
</div>
</div>
</body>
</html>''')
    
    full_html = ''.join(parts)
    print(f'HTML 构建完成，共 {len(full_html)} 字符')
    
    with open('/workspace/index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    print('index.html 写入完成')

if __name__ == '__main__':
    build_html()
