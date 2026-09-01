"""
冒烟测试：验证重构后所有核心 API 契约与原版一致。

运行：python -m pytest tests/test_smoke.py -v
或：  python tests/test_smoke.py
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用测试环境（避免污染真实数据）
os.environ['FLASK_ENV'] = 'testing'

import pytest

from app import create_app
from config import TestConfig


@pytest.fixture()
def app(tmp_path, monkeypatch):
    """每个测试用独立数据目录，避免相互污染。

    两层路径都要覆盖：
    1. TestConfig 类属性 —— repositories（走 app.config）读取；
    2. 蓝图模块级常量（SHARES_FILE 等，模块导入时固化）—— monkeypatch 重定向。
    """
    data_dir = tmp_path / 'data'
    data_dir.mkdir(exist_ok=True)
    d = str(data_dir)

    cfg = TestConfig
    # 覆盖路径类配置到临时目录（repositories 层）
    for key in ('USERS_FILE', 'TOKENS_FILE', 'CAPTCHA_FILE', 'OAUTH_STATE_FILE',
                'FAVORITES_FILE', 'DIVINATION_FILE', 'NOTIFICATIONS_FILE',
                'DATASETS_FILE'):
        setattr(cfg, key, os.path.join(d, key.split('_')[0].lower() + '.json'))
    cfg.DATA_DIR = d
    monkeypatch.setenv('ANALYTICS_DB_PATH', os.path.join(d, 'analytics.db'))

    # 蓝图模块级常量重定向（模块导入时固化，setattr 类配置不生效）
    import app.api.content as _content
    import app.api.datasets as _datasets
    import app.api.profile as _profile
    for name in ('SHARES_FILE', 'REPORTS_FILE', 'DIVINATION_FILE',
                 'NOTIFICATIONS_FILE', 'CONTACTS_FILE', 'DATASETS_FILE'):
        monkeypatch.setattr(_content, name, os.path.join(d, {
            'SHARES_FILE': 'shares.json', 'REPORTS_FILE': 'reports.json',
            'DIVINATION_FILE': 'divination_history.json',
            'NOTIFICATIONS_FILE': 'notifications.json',
            'CONTACTS_FILE': 'contacts.json', 'DATASETS_FILE': 'datasets.json',
        }[name]))
    monkeypatch.setattr(_datasets, 'CATEGORIES_FILE', os.path.join(d, 'categories.json'))
    monkeypatch.setattr(_datasets, 'DATA_DIR', d)
    monkeypatch.setattr(_content, 'DATA_DIR', d)
    monkeypatch.setattr(_profile, 'DATA_DIR', d)
    monkeypatch.setattr(_profile, 'FAVORITES_FILE', os.path.join(d, 'favorites.json'))
    monkeypatch.setattr(_profile, 'PRIVACY_FILE', os.path.join(d, 'privacy.json'))

    # 为被重定向的数据文件创建初始空内容
    # （真实环境中由蓝图模块导入时的 ensure 块创建；patch 后需在临时目录补建，
    #   路由读取逻辑沿袭原版、对缺失文件无容错）
    for fname in ('shares.json', 'reports.json', 'divination_history.json',
                  'notifications.json', 'contacts.json', 'datasets.json',
                  'categories.json', 'favorites.json', 'privacy.json'):
        fp = os.path.join(d, fname)
        if not os.path.exists(fp):
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)

    _app = create_app(cfg)
    _app.config.update({'TESTING': True})
    yield _app
    shutil.rmtree(data_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------- 系统类 ----------

def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] == 'ok'   # 原版契约：status 字段而非 success


def test_version(client):
    r = client.get('/api/version')
    assert r.status_code == 200


def test_static_index(client):
    r = client.get('/')
    assert r.status_code == 200


# ---------- 认证类 ----------

def test_register_and_login(client):
    r = client.post('/api/register', json={
        'username': 'testuser01', 'password': '123456',
        'email': 'test@example.com', 'avatar_type': 'emoji', 'avatar_preset': '🔮',
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data['success'] is True, data
    assert 'token' in data

    # 重复注册应失败
    r2 = client.post('/api/register', json={
        'username': 'testuser01', 'password': '123456'})
    assert r2.get_json()['success'] is False

    # 登录
    r3 = client.post('/api/login', json={
        'username': 'testuser01', 'password': '123456'})
    assert r3.get_json()['success'] is True

    # 错误密码
    r4 = client.post('/api/login', json={
        'username': 'testuser01', 'password': 'wrong'})
    assert r4.get_json()['success'] is False


def test_profile_requires_auth(client):
    r = client.get('/api/profile')
    assert r.status_code in (200, 401)  # 未登录：旧契约返回 401 或 success=False
    if r.status_code == 200:
        assert r.get_json()['success'] is False


def test_profile_with_auth(client):
    reg = client.post('/api/register', json={
        'username': 'profileuser', 'password': '123456'})
    token = reg.get_json()['token']
    r = client.get('/api/profile', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert r.get_json()['success'] is True


# ---------- 验证码类 ----------

def test_captcha_generate_and_verify(client):
    r = client.get('/api/captcha/generate')
    assert r.status_code == 200
    data = r.get_json()
    assert data['success'] is True
    assert 'captcha_id' in data and 'captcha_image' in data


def test_slider_generate(client):
    r = client.get('/api/slider/generate')
    assert r.status_code == 200
    data = r.get_json()
    assert data['success'] is True
    assert 'slider_id' in data


def test_sms_demo_mode_not_leak_code(client):
    """安全回归：演示模式不得把验证码明文回传给前端。"""
    r = client.post('/api/sms/send', json={'phone': '13800138000'})
    assert r.status_code == 200
    data = r.get_json()
    assert data['success'] is True
    # 重构后：无论是否演示模式，code 字段一律为 None（旧版明文回传，属安全漏洞）
    assert data.get('code') is None


# ---------- 算命类 ----------

def test_fortune_bazi(client):
    r = client.post('/api/fortune/bazi', json={
        'name': '张三', 'gender': 'male',
        'birth_date': '1990-05-15', 'birth_time': '14:30'})
    assert r.status_code == 200
    data = r.get_json()
    assert data['success'] is True, data.get('message')


def test_fortune_xingming(client):
    r = client.post('/api/fortune/xingming', json={'name': '张三'})
    assert r.status_code == 200
    assert r.get_json()['success'] is True


def test_fortune_shengxiao(client):
    r = client.post('/api/fortune/shengxiao', json={
        'zodiac': '龙', 'year': 2026})
    assert r.status_code == 200
    assert r.get_json()['success'] is True


def test_fortune_huangli(client):
    r = client.get('/api/fortune/huangli?date=2026-09-01')
    assert r.status_code == 200


def test_fortune_tarot_cards(client):
    r = client.get('/api/fortune/tarot/cards')
    assert r.status_code == 200


def test_fortune_health(client):
    r = client.get('/api/fortune/health')
    assert r.status_code == 200


def test_fortune_universal_analyze(client):
    r = client.post('/api/fortune/analyze', json={
        'module': '面相分析', 'params': {'input': '测试'}})
    assert r.status_code in (200, 400)  # 降级策略下也应 200；参数错 400 可接受
    if r.status_code == 200:
        assert r.get_json()['success'] is True


# ---------- 内容类 ----------

def test_favorites_requires_auth(client):
    r = client.get('/api/favorites')
    assert r.status_code in (200, 401)
    if r.status_code == 200:
        assert r.get_json()['success'] is False


def test_about(client):
    r = client.get('/api/about')
    assert r.status_code == 200
    assert r.get_json()['success'] is True


def test_contacts_crud(client):
    reg = client.post('/api/register', json={
        'username': 'contactuser', 'password': '123456'})
    token = reg.get_json()['token']
    h = {'Authorization': f'Bearer {token}'}

    r = client.post('/api/contacts', headers=h, json={
        'name': '测试联系人', 'gender': 'male', 'birth_date': '1990-01-01'})
    assert r.status_code == 200
    assert r.get_json()['success'] is True

    r2 = client.get('/api/contacts', headers=h)
    assert r2.get_json()['success'] is True


def test_divination_history(client):
    reg = client.post('/api/register', json={
        'username': 'historyuser', 'password': '123456'})
    token = reg.get_json()['token']
    h = {'Authorization': f'Bearer {token}'}
    r = client.get('/api/divination-history', headers=h)
    assert r.status_code == 200
    assert r.get_json()['success'] is True


# ---------- VIP 类 ----------

def test_vip_status(client):
    reg = client.post('/api/register', json={
        'username': 'vipuser', 'password': '123456'})
    token = reg.get_json()['token']
    r = client.get('/api/vip/status',
                   headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert r.get_json()['success'] is True


def test_vip_checkin(client):
    reg = client.post('/api/register', json={
        'username': 'checkinuser', 'password': '123456'})
    token = reg.get_json()['token']
    r = client.post('/api/vip/checkin',
                    headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert r.get_json()['success'] is True


# ---------- 管理端鉴权（安全回归） ----------

def test_admin_analytics_requires_token(client):
    """未带令牌访问管理端应被拒绝（旧版完全无鉴权）。"""
    r = client.get('/api/admin/analytics/overview')
    assert r.status_code in (401, 503)


# ---------- OAuth ----------

def test_oauth_status(client):
    r = client.get('/api/oauth/status')
    assert r.status_code == 200
    assert r.get_json()['success'] is True


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
