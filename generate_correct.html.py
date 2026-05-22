#!/usr/bin/env python3
# -*- coding: utf-8 -*-

html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover">
<title>玄机算命网</title>
<style>
*}{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;overflow:hidden;width:100vw;height:100vh;}
/* ... 其他CSS ... */
.test{outline:none;}
</style>
</head>
<body>
<div>测试页面</div>
<script>
function test(){
    var el = document.querySelector('.test');
    el.classList.add('active');
}
</script>
</body>
</html>"""

# 保存
with open('/workspace/test_final.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('测试文件已生成')
print('检查内容:')
with open('/workspace/test_final.html', 'r', encoding='utf-8') as f:
    content = f.read()
    print('  scalable:', 'scalable' in content)
    print('  outline:', 'outline' in content)
    print('  classList:', 'classList' in content)
