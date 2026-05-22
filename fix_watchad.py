#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 index.html 里的 watchAd() 函数替换成有乐付 / Tapjoy 可接版本
"""

NEW_WATCH_AD = r"""function watchAd() {
    console.log('watchAd called');
    if (!currentUser) {
        showToast('请先登录');
        return;
    }

    showToast('广告加载中...');

    // ===== 有乐付 Youlefu Offerwall — 个人可接 =====
    // 官网：https://www.youlefu.com/
    // 接入文档：https://doc.youlefu.com/
    // 注册后获取 pub_id，替换下方 YOUR_PUB_ID
    // ============================================================

    if (typeof YLF === 'undefined') {
        var sdk = document.createElement('script');
        sdk.src = 'https://cdn.youlefu.com/youlifu.js';
        sdk.onload = function() { startYoulefu(); };
        sdk.onerror = function() {
            console.log('有乐付SDK加载失败，使用模拟模式');
            mockAd();
        };
        document.head.appendChild(sdk);
    } else {
        startYoulefu();
    }

    function startYoulefu() {
        var PUB_ID = 'YOUR_PUB_ID';  // ← 替换成你的有乐付 pub_id

        if (PUB_ID === 'YOUR_PUB_ID') {
            showToast('未配置广告平台，使用模拟模式');
            mockAd();
            return;
        }

        window.YLF && window.YLF.show({
            pubId: PUB_ID,
            userId: currentUser.phone,
            onReward: function(reward) {
                // 用户完成 offer → 调用后端发奖
                grantAdReward();
            },
            onClose: function() {
                showToast('已关闭广告');
            }
        });
    }

    function grantAdReward() {
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
            console.error('Watch ad error:', err);
            showToast('网络错误');
        });
    }

    function mockAd() {
        // 未配置 SDK 时使用模拟模式
        setTimeout(function() {
            grantAdReward();
        }, 1500);
    }
}"""

import re

with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 function watchAd()，一直替换到其后的下一个 function xxx() {
pattern = r'function watchAd\(\) \{[^<]*?function \w+\(\) \{'
# 用非贪婪匹配，直接定位到 closing } 和下一个 function
# 更可靠的办法：按行找

lines = content.split('\n')
new_lines = []
i = 0
skip = False
brace_count = 0
while i < len(lines):
    line = lines[i]
    if 'function watchAd()' in line:
        # 开始跳过，直到匹配的 } 结束
        skip = True
        brace_count = 0
    if skip:
        # 统计大括号，找到函数结束位置
        brace_count += line.count('{') - line.count('}')
        if brace_count <= 0 and i > 0:
            skip = False
            # 插入新函数
            new_lines.append(NEW_WATCH_AD)
            # 不 append 当前行（旧函数最后一行）
            i += 1
            continue
    else:
        new_lines.append(line)
    i += 1

if len(new_lines) < 100:
    # 按行匹配失败，直接字符串替换
    # 找到 watchAd 函数的起止位置
    start = content.find('function watchAd() {')
    if start != -1:
        # 找到对应的结束大括号
        end = start
        depth = 0
        in_fn = False
        i = start
        while i < len(content):
            if content[i] == '{':
                depth += 1
                in_fn = True
            elif content[i] == '}':
                depth -= 1
                if in_fn and depth == 0:
                    end = i + 1
                    break
            i += 1
        if end > start:
            new_content = content[:start] + NEW_WATCH_AD + content[end:]
            with open('/workspace/index.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ watchAd() 已替换，位置 {start}~{end}")
        else:
            print("❌ 找不到 watchAd() 的结束大括号")
    else:
        print("❌ 找不到 function watchAd")
else:
    new_content = '\n'.join(new_lines)
    with open('/workspace/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ watchAd() 已通过行匹配替换")
