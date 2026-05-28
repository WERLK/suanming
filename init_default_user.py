#!/usr/bin/env python3
import json
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

os.makedirs(DATA_DIR, exist_ok=True)

users = []
if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except json.JSONDecodeError:
        users = []

if not users:
    default_user = {
        'id': 'user_default_001',
        'username': 'admin',
        'password': hash_password('admin123'),
        'email': 'admin@xuanji.com',
        'phone': '13800138000',
        'avatar': '',
        'birthday': '',
        'gender': 'male',
        'status': 'active',
        'created_at': '2026-05-28T00:00:00',
        'last_login': ''
    }
    users = [default_user]
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print('Created default user: admin / admin123')
else:
    print(f'Users already exist: {len(users)} users')
