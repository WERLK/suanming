#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加会员开通功能到玄机算命网
"""

import json

# 读取现有代码
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 在CSS中添加会员开通页面的样式
vip_css = """
    .vip-page{position:fixed;top:0;left:0;width:100%;height:100%;background:linear-gradient(180deg,#0f0c29,#1a1a2e 50%,#0a0a1a);display:none;flex-direction:column;z-index:9999;overflow-y:auto;}
    .vip-page.active{display:flex;}
    .vip-hdr{display:flex;justify-content:space-between;align-items:center;padding:1rem;flex-shrink:0;}
    .vip-back{font-size:1.3rem;color:rgba(255,255,255,0.5);cursor:pointer;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;}
    .vip-title{font-size:1.1rem;color:#fff;font-weight:700;}
    .vip-spacer{width:40px;}
    .vip-body{padding:1.5rem;flex:1;}
    .vip-card{background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,107,53,0.08));border-radius:16px;padding:2rem;margin-bottom:1.5rem;border:2px solid rgba(255,215,0,0.3);text-align:center;position:relative;overflow:hidden;}
    .vip-card:before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,215,0,0.1) 0%,transparent 70%);animation:vip-glow 3s ease-in-out infinite;}
    @keyframes vip-glow{0%,100%{transform:scale(1);opacity:0.5;}50%{transform:scale(1.1);opacity:0.8;}}
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
"""

# 2. 在</style>前插入VIP CSS
html = html.replace('  </style>', vip_css + '  </style>')

# 3. 添加会员开通页面HTML
vip_html = """
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
            <div class="vip-pay-opt a" onclick="selectPay('wechat', this)">
              <span class="ic">💚</span>
              <span class="lb">微信支付</span>
            </div>
            <div class="vip-pay-opt" onclick="selectPay('alipay', this)">
              <span class="ic">💙</span>
              <span class="lb">支付宝</span>
            </div>
            <div class="vip-pay-opt" onclick="selectPay('qq', this)">
              <span class="ic">💜</span>
              <span class="lb">QQ钱包</span>
            </div>
          </div>

          <button class="vip-btn" onclick="doVipPay()">立即开通</button>
        </div>
      </div>
"""

# 4. 在用户中心页面后插入VIP页面
html = html.replace('<div class="uc-page', vip_html + '\n    <div class="uc-page')

# 5. 在用户中心菜单中添加"开通会员"选项
vip_menu_item = """          <div class="uc-menu-i" onclick="openVip()">
            <span class="ic">⭐</span>
            <span class="lb">开通会员</span>
            <span class="ar">›</span>
          </div>"""

html = html.replace('</div>\n\n    <div class="auth-overlay"', vip_menu_item + '\n    </div>\n\n    <div class="auth-overlay"')

# 6. 添加JavaScript函数
vip_js = """
    var vipDuration = 3;  // 默认3个月
    var vipPayMethod = 'wechat';  // 默认微信支付

    function openVip(){
        console.log('openVip called');
        if(!currentUser){
            showToast('请先登录');
            return;
        }
        document.getElementById('vip-page').classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // 如果已经是VIP，显示当前会员信息
        if(currentUser.is_vip){
            var exp = new Date(currentUser.vip_expire * 1000).toLocaleDateString();
            document.getElementById('vip-name').textContent = currentUser.vip_type || '会员';
            document.getElementById('vip-price').innerHTML = '¥0<span>/已开通</span>';
        }
    }

    function closeVip(){
        console.log('closeVip called');
        document.getElementById('vip-page').classList.remove('active');
        document.body.style.overflow = 'auto';
    }

    function selectVipDuration(months, el){
        console.log('selectVipDuration:', months);
        vipDuration = months;
        
        // 更新UI
        document.querySelectorAll('.vip-option').forEach(function(opt){
            opt.classList.remove('a');
        });
        el.classList.add('a');
        
        // 更新价格显示
        var pricePerMonth = 29;
        if(months == 3) pricePerMonth = 25;
        if(months == 12) pricePerMonth = 19;
        var total = pricePerMonth * months;
        document.getElementById('vip-price').innerHTML = '¥' + total + '<span>/' + months + '个月</span>';
    }

    function selectPay(method, el){
        console.log('selectPay:', method);
        vipPayMethod = method;
        
        // 更新UI
        document.querySelectorAll('.vip-pay-opt').forEach(function(opt){
            opt.classList.remove('a');
        });
        el.classList.add('a');
    }

    function doVipPay(){
        console.log('doVipPay called, duration:', vipDuration, 'pay:', vipPayMethod);
        
        if(!currentUser){
            showToast('请先登录');
            return;
        }
        
        // 计算价格
        var pricePerMonth = 29;
        if(vipDuration == 3) pricePerMonth = 25;
        if(vipDuration == 12) pricePerMonth = 19;
        var total = pricePerMonth * vipDuration;
        
        showToast('正在跳转支付...');
        
        // 模拟支付（实际项目中应调用支付API）
        setTimeout(function(){
            // 调用后端API开通会员
            fetch(API_BASE + '/api/upgrade_vip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
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
                    localStorage.setItem('xjsm_user', JSON.stringify(currentUser));
                    
                    // 更新用户中心显示
                    updateUserBar();
                    var vipStatus = document.getElementById('uc-vip-status');
                    var exp = new Date(currentUser.vip_expire * 1000).toLocaleDateString();
                    vipStatus.textContent = '⭐ ' + currentUser.vip_type + '（有效期至：' + exp + '）';
                    vipStatus.style.color = '#ffd700';
                    
                    showToast('会员开通成功！');
                    closeVip();
                } else {
                    showToast(data.msg || '支付失败');
                }
            })
            .catch(function(err){
                console.error('Pay error:', err);
                showToast('网络错误');
            });
        }, 1500);
    }
"""

# 7. 在</script>前插入VIP JS
html = html.replace('  </script>', vip_js + '  </script>')

# 写入文件
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ 前端会员开通功能已添加")
print("  - 新增VIP开通页面样式")
print("  - 新增会员时长选择（1/3/12个月）")
print("  - 新增支付方式选择（微信/支付宝/QQ）")
print("  - 新增openVip/closeVip/doVipPay等函数")
