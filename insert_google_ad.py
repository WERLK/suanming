#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insert startGoogleAd() function into index.html
Place it between the mockAd() call and startYoulefu()
"""

with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The Google AdSense section to insert
GOOGLE_FN = r"""
    // ===== 模式 B：Google AdSense / AdMob =====
    // 个人可申请：https://www.google.com/adsense/start/
    // 激励视频需要 AdMob + App 壳（Capacitor/Cordova）
    // 纯 Web 可用 AdSense 展示广告（非激励）
    //
    // 如需激励视频，需先用 Capacitor 打包成 App：
    //   npm install @capacitor/core @capacitor/cli
    //   npx cap init
    //   npm install cordova-plugin-admob-free
    //
    function startGoogleAd() {
        // 纯 Web 模式：展示 AdSense 展示广告（非激励）
        // 要激励视频请用 App 壳 + AdMob

        if (typeof googletag === 'undefined') {
            var s = document.createElement('script');
            s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
            s.onload = function() { startGoogleAd(); };
            s.onerror = function() {
                console.log('Google AdSense SDK 加载失败，使用模拟模式');
                mockAd();
            };
            document.head.appendChild(s);
            return;
        }

        // 已加载 AdSense SDK
        showToast('广告加载中...');

        // 激励视频需要 AdMob（App 壳）
        // 这里用模拟代替
        showToast('AdMob 需要 App 壳，使用模拟模式');
        mockAd();
    }
"""

# Insert after "var AD_MODE = 'mock';  // ← 改成 'google' 或 'youlfu' 切到真实广告"
# and before the mockAd() call

old = "    if (AD_MODE === 'mock') {\n        mockAd();\n        return;\n    }"
new = '    if (AD_MODE === \'mock\') {\n        mockAd();\n        return;\n    }\n\n    if (AD_MODE === \'google\') {\n        startGoogleAd();\n        return;\n    }'

if old in content:
    content = content.replace(old, new)
    print("✅ 插入了 google 模式分支")
else:
    print("⚠️ 找不到 mockAd() 调用位置，尝试其他方式")
    # Try to find the watchAd function and add the branch
    idx = content.find('function watchAd()')
    if idx != -1:
        # Find the position after the opening brace + initial setup
        pos = content.find('showToast(\'广告加载中...\');', idx)
        if pos != -1:
            pos = content.find('\n', pos) + 1
            insert = '''    if (AD_MODE === 'mock') { mockAd(); return; }
    if (AD_MODE === 'google') { startGoogleAd(); return; }
    if (AD_MODE === 'youlfu') { startYoulefu(); return; }

'''
            content = content[:pos] + '' + content[pos:]
            print("✅ 通过位置插入了模式分支")
        else:
            print("❌ 找不到插入点")

# Now add the startGoogleAd() function before startYoulefu()
old2 = '    function startYoulefu() {'
new2 = GOOGLE_FN + '\n    function startYoulefu() {'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("✅ 插入了 startGoogleAd() 函数")
else:
    print("⚠️ 找不到 startYoulefu() 位置")
    # Try to add before the Youlefu section comment
    idx = content.find('// ===== 模式 C：有乐付 Youlefu Offerwall')
    if idx != -1:
        content = content[:idx] + GOOGLE_FN + '\n' + content[idx:]
        print("✅ 在 Youlefu 注释前插入了 startGoogleAd()")

# Write back
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ index.html 已更新")
print("  - AD_MODE='mock' → 模拟模式（现在可用）")
print("  - AD_MODE='google' → Google AdSense（需 App 壳）")
print("  - AD_MODE='youlfu' → 有乐付（需申请 pub_id）")
