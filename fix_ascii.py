#!/usr/bin/env python3
"""
ASCII-only fix script for Alibaba Cloud server.
Run: python3 /tmp/fix_ascii.py
Fixes: cross-process file lock for captcha_store.json (gunicorn -w 4 bug)
"""
import os, re

APP = '/root/suanming/api/app.py'

with open(APP, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ---- Fix 1: Add fcntl import ----
if 'import fcntl\n' not in lines:
    for i, line in enumerate(lines):
        if line.strip() == 'import time':
            lines.insert(i + 1, 'import fcntl\n')
            print('[OK] fcntl import added')
            break

# ---- Fix 2: Replace _load_captcha_store ----
LOAD_START = None
LOAD_END = None
for i, line in enumerate(lines):
    if line.strip().startswith('def _load_captcha_store():'):
        LOAD_START = i
    if LOAD_START is not None and LOAD_END is None and line.strip().startswith('def _save_captcha_store('):
        LOAD_END = i

if LOAD_START and LOAD_END:
    new_load = [
        'def _load_captcha_store():\n',
        '    """Load captcha store with fcntl file lock (multi-process safe)"""\n',
        '    if not os.path.exists(CAPTCHA_FILE):\n',
        '        return {}\n',
        '    try:\n',
        "        with open(CAPTCHA_FILE, 'r', encoding='utf-8') as f:\n",
        '            fcntl.flock(f.fileno(), fcntl.LOCK_SH)\n',
        '            try:\n',
        '                return json.load(f)\n',
        '            finally:\n',
        '                fcntl.flock(f.fileno(), fcntl.LOCK_UN)\n',
        '    except (json.JSONDecodeError, IOError):\n',
        '        return {}\n',
    ]
    lines[LOAD_START:LOAD_END] = new_load
    print('[OK] _load_captcha_store replaced')

# ---- Fix 3: Replace _save_captcha_store ----
SAVE_START = None
SAVE_END = None
for i, line in enumerate(lines):
    if line.strip().startswith('def _save_captcha_store('):
        SAVE_START = i
    if SAVE_START is not None and SAVE_END is None and i > SAVE_START and line.strip().startswith('def _get_captcha_entry('):
        SAVE_END = i

if SAVE_START and SAVE_END:
    new_save = [
        'def _save_captcha_store(store):\n',
        '    """Save captcha store with fcntl file lock (multi-process safe)"""\n',
        '    now = datetime.now().isoformat()\n',
        "    store = {k: v for k, v in store.items() if v.get('expire_time', '') > now}\n",
        '    fd = os.open(CAPTCHA_FILE, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)\n',
        '    try:\n',
        '        fcntl.flock(fd, fcntl.LOCK_EX)\n',
        "        os.write(fd, json.dumps(store, ensure_ascii=False).encode('utf-8'))\n",
        '    finally:\n',
        '        fcntl.flock(fd, fcntl.LOCK_UN)\n',
        '        os.close(fd)\n',
    ]
    lines[SAVE_START:SAVE_END] = new_save
    print('[OK] _save_captcha_store replaced')

# ---- Write back ----
with open(APP, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('[DONE] app.py fixed - safe to restart gunicorn')
print('Next: systemctl restart suanming')
