#!/usr/bin/env python3
"""
module_list.json 与 modules/ 目录同步校验。

问题背景：module_list.json 在根目录与 modules/ 下各有一份副本（历史上
手工维护），且清单与实际 HTML 文件已脱节（清单 204 条 vs 实际 257 页）。

本脚本：
1. 以根目录 module_list.json 为唯一真源（source of truth）；
2. 同步副本到 modules/module_list.json；
3. 报告清单与实际文件的差异（缺失/多余）。

用法：python scripts/sync_module_list.py [--fix]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_LIST = os.path.join(ROOT, 'module_list.json')
COPY_LIST = os.path.join(ROOT, 'modules', 'module_list.json')
MODULES_DIR = os.path.join(ROOT, 'modules')


def main():
    entries = json.load(open(MAIN_LIST, encoding='utf-8'))
    print(f'清单条目: {len(entries)}')

    # 同步副本
    if os.path.exists(COPY_LIST):
        copy = json.load(open(COPY_LIST, encoding='utf-8'))
        if copy != entries:
            if '--fix' in sys.argv:
                json.dump(entries, open(COPY_LIST, 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=2)
                print('副本已同步 ✓')
            else:
                print('副本不一致（加 --fix 修复）')

    # 与实际文件对比
    listed = {e['file'] for e in entries if 'file' in e}
    actual = {f for f in os.listdir(MODULES_DIR) if f.endswith('.html')}
    missing_in_list = sorted(actual - listed)
    missing_on_disk = sorted(listed - actual)
    if missing_in_list:
        print(f'磁盘有但清单缺失: {len(missing_in_list)} 个（新页面未登记）')
        if '--fix' in sys.argv:
            # 自动补登（category 待人工归类，暂归"其他功能"）
            for f in missing_in_list:
                name = os.path.splitext(f)[0].rsplit('_', 1)[0]
                entries.append({'category': '其他功能', 'name': name,
                                'file': f, 'path': f'/modules/{f}'})
            json.dump(entries, open(MAIN_LIST, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=2)
            json.dump(entries, open(COPY_LIST, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=2)
            print(f'已补登 {len(missing_in_list)} 条（归类"其他功能"，建议人工复核分类）')
    if missing_on_disk:
        print(f'清单有但磁盘缺失: {len(missing_on_disk)} 个（僵尸条目）')


if __name__ == '__main__':
    main()
