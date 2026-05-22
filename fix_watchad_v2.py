#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replace watchAd() in index.html with 3-mode ad framework:
mock / Google AdSense / Youlefu
"""

import re

with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The new 3-in-1 watchAd function
NEW_FN = r"""function watchAd() {
    console.log('watchAd called, mode=' + AD_MODE);
    if (!currentUser) { showToast('请先登录'); return; }
    showToast('广告加载中...');

    // ==============================
    // AD_MODE: 'mock' | 'google' | 'youlfu'
    // ==============================
    var AD_MODE = 'mock';   // ← 改成 'google' 或 'youlfu' 切到真实广告

    if (AD_MODE === 'mock') {
        mockAd();
        return;
    }

    if (AD_MODE === 'google') {
        startGoogleAd();
        return;
    }

    if (AD_MODE === 'youlfu') {
        startYoulefu();
        return;
    }
}

// ===== 模式 A：Mock（现在就能用）======
function mockAd() {
    showToast('观看广告 15 秒...');
    setTimeout(function() { grantAdReward(); }, 15000);
}

// ===== 模式 B：Google AdSense Rewarded Ads =====
// 接入条件：需要 Google AdMob 账号（个人可申）
// 官网：https://admob.google.com/
// 1. 引 SDK：<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
// 2. 在 onReward 里调 grantAdReward()
function startGoogleAd() {
    if (typeof googletag === 'undefined') {
        var s = document.createElement('script');
        s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
        s.onload = function() { startGoogleAd(); };
        s.onerror = function() { showToast('Google SDK 加载失败，切到模拟'); mockAd(); };
        document.head.appendChild(s);
        return;
    }
    // 真实接入时需要创建 RewardedAd 对象并 show()
    // 参见：https://developers.google.com/ad-manager/mobile-ads-sdk/rewarded-ads
    showToast('Google 广告暂未配置，使用模拟');
    mockAd();
}

// ===== 模式 C：有乐付 Youlefu Offerwall =====
// 个人可接：https://www.youlefu.com/
// 1. 注册 → 创建应用 → 获取 pub_id
// 2. 引 SDK：<script src="https://cdn.youlefu.com/youlifu.js"></script>
function startYoulefu() {
    if (typeof YLF === 'undefined') {
        var s = document.createElement('script');
        s.src = 'https://cdn.youlefu.com/youlifu.js';
        s.onload = function() { startYoulefu(); };
        s.onerror = function() { showToast('有乐付 SDK 加载失败，切到模拟'); mockAd(); };
        document.head.appendChild(s);
        return;
    }
    var PUB_ID = 'YOUR_YOULFU_PUB_ID';  // ← 替换成你的 pub_id
    if (PUB_ID === 'YOUR_YOULFU_PUB_ID') {
        showToast('未配置有乐付 pub_id，使用模拟');
        mockAd();
        return;
    }
    window.YLF && window.YLF.show({
        pubId: PUB_ID,
        userId: currentUser.phone,
        onReward: function(reward) { grantAdReward(); },
        onClose: function() { showToast('已关闭广告'); }
    });
}

// ===== 发奖（三种模式共用）======
function grantAdReward() {
    console.log('grantAdReward');
    fetch(API_BASE + '/api/watch_ad', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone: currentUser.phone })
    })
    .then(function(res){ return res.json(); })
    .then(function(data){
        if (data.code === 200) {
            currentUser.is_vip = true;
            currentUser.vip_expire = data.data.vip_expire;
            currentUser.vip_type = data.data.vip_type;
            localStorage.setItem('xjsm_user', JSON.stringify(currentUser));
            updateUserBar();
            var vipStatus = document.getElementById('uc-vip-status');
            var exp = new Date(currentUser.vip_expire * 1000).toLocaleDateString();
            vipStatus.textContent = '⭐ ' + currentUser.vip_type + '（有效期至：' + exp + '）';
            vipStatus.style.color = '#ffd700';
            showToast('🎉 恭喜获得1天免费会员！');
            closeVip();
        } else {
            showToast(data.msg || '领取失败');
        }
    })
    .catch(function(err){
        console.error('grantAdReward error:', err);
        showToast('网络错误');
    });
}
"""

# Find the old watchAd function and replace it
# Match from "function watchAd()" to the closing "}" before "function updateUserBar"
pattern = r'(function watchAd\(\)\s*\{)(?:[^{}]*|\{(?:[^{}]*|\{(?:[^{}]*|\{[^}]*\})*\})*\})*\}(?=\s*\nfunction updateUserBar)'

# Use a simpler approach: find start and end positions
start = content.find('function watchAd()')
if start == -1:
    print("ERROR: function watchAd() not found!")
    exit(1)

# Find the matching closing brace
# Count braces from start position
pos = start
depth = 0
in_fn = False
end = -1

while pos < len(content):
    if content[pos] == '{':
        depth += 1
        in_fn = True
    elif content[pos] == '}':
        depth -= 1
        if in_fn and depth == 0:
            end = pos + 1
            break
    pos += 1

if end == -1:
    print("ERROR: Could not find end of watchAd()!")
    exit(1)

print(f"Replacing watchAd() at positions {start}-{end}")

new_content = content[:start] + NEW_FN + content[end:]

with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ watchAd() replaced with 3-mode framework (mock / google / youlefu)")
print("   Edit AD_MODE at top of watchAd() to switch modes.")
print("   Youlefu: replace YOUR_YOULFU_PUB_ID with your real pub_id.")
