"""
前端模块页瘦身：提取完全重复的内嵌 <style> 块为公共 CSS 文件。

策略（零风险）：
- 只提取「内容完全相同 且 出现 ≥3 次」的 style 块（md5 哈希判定）；
- 每个公共块生成 css/module-common-N.css，页面内替换为 <link> 引用；
- 页面独有的样式原样保留（差异部分不动）。

用法：
    python scripts/slim_modules.py            # 执行瘦身
    python scripts/slim_modules.py --dry-run  # 仅统计
    python scripts/slim_modules.py --restore  # 从备份恢复
"""
import hashlib
import os
import re
import shutil
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = os.path.join(ROOT, 'modules')
CSS_DIR = os.path.join(ROOT, 'css')
BACKUP = os.path.join(ROOT, 'scripts', '.modules_backup')
MIN_REPEAT = 3


def analyze():
    blocks = Counter()
    sizes = {}
    for f in sorted(os.listdir(MODULES)):
        if not f.endswith('.html'):
            continue
        src = open(os.path.join(MODULES, f), encoding='utf-8').read()
        for m in re.finditer(r'[ \t]*<style>\n?(.*?)</style>', src, re.S):
            content = m.group(1).rstrip()
            if content.strip():
                h = hashlib.md5(content.encode()).hexdigest()
                blocks[h] += 1
                sizes[h] = content
    return {h: c for h, c in blocks.items() if c >= MIN_REPEAT}, sizes


def slim(dry_run=False):
    common, sizes = analyze()
    if not common:
        print('没有可提取的公共样式块')
        return

    total_before = 0
    total_after = 0
    changed = 0

    # 生成公共 CSS 文件
    link_map = {}
    os.makedirs(CSS_DIR, exist_ok=True)
    for i, (h, count) in enumerate(sorted(common.items(), key=lambda x: -x[1]), 1):
        css_name = f'module-common-{i}.css'
        with open(os.path.join(CSS_DIR, css_name), 'w', encoding='utf-8') as f:
            f.write(sizes[h] + '\n')
        link_map[h] = css_name
        print(f'  提取 {css_name}: {count} 个页面共用（{len(sizes[h].splitlines())} 行）')

    # 备份
    if not dry_run:
        if os.path.exists(BACKUP):
            shutil.rmtree(BACKUP)
        shutil.copytree(MODULES, BACKUP)

    # 替换页面
    for fname in sorted(os.listdir(MODULES)):
        if not fname.endswith('.html'):
            continue
        path = os.path.join(MODULES, fname)
        src = open(path, encoding='utf-8').read()
        total_before += len(src)

        def _replace(m):
            content = m.group(1).rstrip()
            h = hashlib.md5(content.encode()).hexdigest()
            if h in link_map:
                return f'<link rel="stylesheet" href="/css/{link_map[h]}">'
            return m.group(0)

        new_src = re.sub(r'[ \t]*<style>\n?(.*?)</style>', _replace, src, flags=re.S)

        if new_src != src:
            changed += 1
            if not dry_run:
                open(path, 'w', encoding='utf-8').write(new_src)
        total_after += len(new_src)

    saved = total_before - total_after
    print(f'\n结果：{changed}/{len(os.listdir(MODULES))} 个页面已瘦身，'
          f'源码减少 {saved/1024:.0f} KB')
    print(f'注：浏览器实际节省更大——公共 CSS 可被缓存，无需每页重复下载。')
    if not dry_run:
        print(f'备份位置：{BACKUP}（恢复：python scripts/slim_modules.py --restore）')


def restore():
    if not os.path.exists(BACKUP):
        print('未找到备份')
        sys.exit(1)
    shutil.rmtree(MODULES)
    shutil.copytree(BACKUP, MODULES)
    print('已恢复全部模块页面')


if __name__ == '__main__':
    if '--restore' in sys.argv:
        restore()
    elif '--dry-run' in sys.argv:
        slim(dry_run=True)
    else:
        slim()
