#!/usr/bin/env python3
"""
批量给所有 HTML 页面添加返回首页按钮
- 根目录页面（profile.html, login.html 等）：在 <body> 后加 .page-header + back-btn
- modules/*.html：检查是否已有 back-btn，没有则加上
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')

BACK_BTN_CSS = """
    .back-btn {
        background: none;
        border: none;
        color: #ffd700;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 0.5rem;
    }
    .page-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: linear-gradient(180deg, rgba(15,12,41,0.98), rgba(26,26,46,0.95));
        border-bottom: 1px solid rgba(255,215,0,0.15);
    }
    .page-header h1 {
        font-size: 1.2rem;
        color: #ffd700;
        font-weight: 600;
    }
"""

PAGE_HEADER_HTML = """<div class="page-header">
        <button class="back-btn" onclick="window.location.href='/'">←</button>
        <h1>{title}</h1>
    </div>
    <div class="content-area">"""

CONTENT_AREA_CLOSE = """    </div><!-- /content-area -->"""


def get_page_title(filepath):
    """从 HTML 中提取 title"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'<title>(.*?)</title>', content)
    if m:
        # 去掉 " - 玄机算命网" 后缀
        title = re.sub(r'\s*-\s*玄机算命网.*', '', m.group(1))
        return title
    return '玄机算命'


def fix_root_page(filepath):
    """修复根目录页面（profile.html, login.html 等）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 已有 page-header，跳过
    if 'page-header' in content:
        print(f'  SKIP (已有 page-header): {os.path.basename(filepath)}')
        return False

    title = get_page_title(filepath)

    # 在 </head> 后、<body> 后插入 page-header
    # 先加 CSS（如果还没有）
    if 'back-btn' not in content:
        # 在 </style> 或 </head> 前插入 CSS
        css_block = f'<style>{BACK_BTN_CSS}</style>'
        # 找到 </head> 前的位置插入
        content = re.sub(r'</head>', f'{css_block}\n</head>', content, count=1)

    # 在 <body> 标签后插入 page-header
    header_html = PAGE_HEADER_HTML.format(title=title)
    content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + '\n' + header_html, content, count=1)

    # 在 </body> 前加 </div><!-- /content-area -->
    content = re.sub(r'</body>', '</div>\n    </body>', content, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  FIXED: {os.path.basename(filepath)}')
    return True


def fix_module_page(filepath):
    """修复 modules/*.html 页面"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 已有 back-btn，检查 onclick 是否正确
    if 'back-btn' in content:
        if "window.location.href='/'" in content or "history.back()" in content:
            print(f'  OK (已有返回按钮): {os.path.basename(filepath)}')
            return False
        else:
            # 有 back-btn 但 onclick 不正确，修复
            content = re.sub(r'onclick="[^"]*"', 'onclick="window.location.href=\'/\'"', content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'  FIXED (修复 onclick): {os.path.basename(filepath)}')
            return True

    # 没有 back-btn，尝试在 <body> 后加
    title = get_page_title(filepath)

    # 加 CSS
    if '<style>' in content and 'back-btn' not in content:
        content = re.sub(r'<style>', f'<style>\n{BACK_BTN_CSS}', content, count=1)

    # 加 page-header
    header_html = PAGE_HEADER_HTML.format(title=title)
    content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + '\n' + header_html, content, count=1)

    # 加 </div><!-- /content-area --> 在 </body> 前
    content = re.sub(r'</body>', '</div>\n    </body>', content, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  FIXED (新增返回按钮): {os.path.basename(filepath)}')
    return True


def main():
    print('=== 批量添加返回按钮 ===\n')

    # 1. 修复根目录页面
    root_pages = [
        'profile.html',
        'login.html',
        'register.html',
        'forgot-password.html',
        'reset-password.html',
        'more.html',
        'index.html',  # 首页不需要返回按钮，跳过
    ]
    print('--- 根目录页面 ---')
    for page in root_pages:
        filepath = os.path.join(BASE_DIR, page)
        if page == 'index.html':
            print(f'  SKIP (首页): {page}')
            continue
        if os.path.exists(filepath):
            fix_root_page(filepath)
        else:
            print(f'  NOT FOUND: {page}')

    # 2. 修复 modules/*.html
    print('\n--- 模块页面 (modules/*.html) ---')
    if os.path.exists(MODULES_DIR):
        html_files = sorted([f for f in os.listdir(MODULES_DIR) if f.endswith('.html')])
        print(f'共 {len(html_files)} 个文件')
        fixed = 0
        for fname in html_files:
            filepath = os.path.join(MODULES_DIR, fname)
            if fix_module_page(filepath):
                fixed += 1
        print(f'\n模块页面修复完成，共修复 {fixed} 个')
    else:
        print(f'目录不存在: {MODULES_DIR}')

    print('\n=== 全部完成 ===')


if __name__ == '__main__':
    main()
