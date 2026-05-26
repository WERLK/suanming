#!/usr/bin/env python3
"""
批量给所有模块 HTML 添加「上传图片分析」按钮和分析结果区域
"""
import os, re

MODULES_DIR = 'modules'
RESULT_AREA = '''
        <!-- 图片分析区域 -->
        <div class="image-analysis-area" style="margin-top:1rem;display:none;" id="imageAnalysisArea">
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.05),rgba(255,215,0,0.02));border:1px solid rgba(255,215,0,0.1);border-radius:12px;padding:1.5rem;">
                <h3 style="color:#ffd700;margin-bottom:1rem;">📷 图片分析结果</h3>
                <div id="imageAnalysisResult" style="color:rgba(255,255,255,0.85);line-height:1.8;font-size:0.9rem;white-space:pre-wrap;"></div>
                <button type="button" onclick="document.getElementById('imageAnalysisArea').style.display='none';" style="margin-top:1rem;background:rgba(255,215,0,0.2);color:#ffd700;border:1px solid rgba(255,215,0,0.3);border-radius:8px;padding:0.5rem 1rem;cursor:pointer;">关闭</button>
            </div>
        </div>
'''

UPLOAD_BTN = '''        <div style="margin-bottom:1rem;">
            <button type="button" class="submit-btn" style="width:auto;padding:0.8rem 1.5rem;font-size:0.9rem;" onclick="triggerImageUpload('{module_type}')">📷 上传图片分析</button>
        </div>
'''

def add_image_analysis(html, fname):
    """给单个 HTML 文件添加图片分析功能"""
    original = html
    module_type = fname.replace('.html', '').lower()

    # 1. 加 JS 函数（在 </script> 前）
    if 'function triggerImageUpload' not in html:
        js_func = '''
// 触发图片上传
function triggerImageUpload(moduleType) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function() {
        const file = this.files[0];
        if (!file) return;
        window.showToast('正在分析图片...');
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64 = e.target.result;
            fetch('/api/image-analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64, module_type: moduleType })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.showToast('分析完成！');
                    const area = document.getElementById('imageAnalysisArea');
                    const result = document.getElementById('imageAnalysisResult');
                    if (area) area.style.display = 'block';
                    if (result) result.textContent = data.analysis;
                } else {
                    window.showToast('分析失败：' + (data.message || '未知错误'));
                }
            })
            .catch(err => {
                window.showToast('分析失败，请检查网络');
                console.error('图片分析错误：', err);
            });
        };
        reader.readAsDataURL(file);
    };
    input.click();
}
'''
        # 插入到最后一个 </script> 前
        html = re.sub(r'(</script>)', js_func + r'\1', html, count=1)

    # 2. 加「上传图片分析」按钮（在 content-area 内，section 前）
    if 'triggerImageUpload' not in html or '上传图片分析' not in html:
        # 在第一个 section 前插入按钮
        btn = UPLOAD_BTN.format(module_type=module_type)
        html = re.sub(r'(<div class="section"|<div class="knowledge-grid"|<div class="zodiac-grid"|<div class="card-grid")',
                      btn + r'\1', html, count=1)

    # 3. 加分析结果区域（在 content-area 末尾，</div> 前）
    if 'imageAnalysisArea' not in html:
        html = re.sub(r'(</div>\s*</body>)', RESULT_AREA + r'\1', html, count=1)

    return html


ADDED = []
SKIPPED = []

for fname in sorted(os.listdir(MODULES_DIR)):
    if not fname.endswith('.html'):
        continue
    path = os.path.join(MODULES_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    new_html = add_image_analysis(html, fname)

    if new_html != html:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        ADDED.append(fname)
    else:
        SKIPPED.append(fname)

print(f'处理完成：')
print(f'  新增/修改：{len(ADDED)} 个文件')
print(f'  跳过（已有功能）：{len(SKIPPED)} 个文件')
if ADDED:
    print(f'\n新增文件：')
    for f in ADDED[:20]:
        print(f'  {f}')
