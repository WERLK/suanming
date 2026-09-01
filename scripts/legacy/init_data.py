#!/usr/bin/env python3
"""Initialize all data files for the project. Creates empty structures, no default accounts."""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

FILES = {
    'users.json': [],
    'tokens.json': {},
    'captcha_store.json': {},
    'favorites.json': {},
    'shares.json': {},
    'reports.json': {},
    'divination_history.json': {},
    'notifications.json': {},
    'privacy.json': {},
}

os.makedirs(DATA_DIR, exist_ok=True)

for filename, default in FILES.items():
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        print(f'Created: {filepath}')
    else:
        print(f'Exists:  {filepath}')

print('\nAll data files initialized. No default accounts created.')
