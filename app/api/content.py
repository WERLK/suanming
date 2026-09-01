"""内容路由：收藏/分享/报告/占卜历史/联系人/帮助/关于"""

from datetime import datetime

from flask import Blueprint, jsonify, request

import fcntl
import json
import os
import random
import string


from app.api.deps import _get_auth_user, load_users, save_users
from config import DATA_DIR, DIVINATION_FILE, FAVORITES_FILE

bp = Blueprint('content', __name__)

@bp.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户收藏列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        user_favorites = favorites.get(user['id'], [])
        
        return jsonify({
            'success': True,
            'favorites': user_favorites
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        module_name = data.get('module_name', '')
        
        if not module_id or not module_name:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        if user['id'] not in favorites:
            favorites[user['id']] = []
        
        # 检查是否已收藏
        for item in favorites[user['id']]:
            if item['module_id'] == module_id:
                return jsonify({'success': False, 'message': '已经收藏过了'}), 400
        
        # 添加收藏
        favorites[user['id']].append({
            'module_id': module_id,
            'module_name': module_name,
            'add_time': datetime.now().isoformat()
        })
        
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '收藏成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    """取消收藏"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        
        if not module_id:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        if user['id'] not in favorites:
            return jsonify({'success': False, 'message': '收藏不存在'}), 400
        
        # 移除收藏
        favorites[user['id']] = [item for item in favorites[user['id']] if item['module_id'] != module_id]
        
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '取消收藏成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 分享记录 ==========
SHARES_FILE = os.path.join(DATA_DIR, 'shares.json')

# 确保分享文件存在
if not os.path.exists(SHARES_FILE):
    with open(SHARES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@bp.route('/api/shares', methods=['GET'])
def get_shares():
    """获取分享记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(SHARES_FILE, 'r', encoding='utf-8') as f:
            shares = json.load(f)
        
        user_shares = shares.get(user['id'], [])
        
        return jsonify({
            'success': True,
            'shares': user_shares
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/shares', methods=['POST'])
def add_share():
    """添加分享记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        module_name = data.get('module_name', '')
        share_platform = data.get('platform', '')  # wechat/weibo/qq/other
        
        with open(SHARES_FILE, 'r', encoding='utf-8') as f:
            shares = json.load(f)
        
        if user['id'] not in shares:
            shares[user['id']] = []
        
        shares[user['id']].append({
            'module_id': module_id,
            'module_name': module_name,
            'platform': share_platform,
            'share_time': datetime.now().isoformat()
        })
        
        with open(SHARES_FILE, 'w', encoding='utf-8') as f:
            json.dump(shares, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '分享记录已保存'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 报告功能 ==========
REPORTS_FILE = os.path.join(DATA_DIR, 'reports.json')

# 确保报告文件存在
if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@bp.route('/api/reports', methods=['GET'])
def get_reports():
    """获取用户报告列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        user_reports = reports.get(user['id'], [])
        
        return jsonify({
            'success': True,
            'reports': user_reports
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/reports', methods=['POST'])
def save_report():
    """保存算命报告"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        module_name = data.get('module_name', '')
        input_data = data.get('input_data', {})
        result_data = data.get('result_data', '')
        
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        if user['id'] not in reports:
            reports[user['id']] = []
        
        reports[user['id']].append({
            'id': 'report_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'module_id': module_id,
            'module_name': module_name,
            'input_data': input_data,
            'result_data': result_data,
            'save_time': datetime.now().isoformat()
        })
        
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '报告保存成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """删除报告"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        if user['id'] not in reports:
            return jsonify({'success': False, 'message': '报告不存在'}), 400
        
        # 删除报告
        reports[user['id']] = [r for r in reports[user['id']] if r['id'] != report_id]
        
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '报告删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 占卜历史 ==========
DIVINATION_FILE = os.path.join(DATA_DIR, 'divination_history.json')

if not os.path.exists(DIVINATION_FILE):
    with open(DIVINATION_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@bp.route('/api/divination-history', methods=['GET'])
def get_divination_history():
    """获取用户占卜历史，支持分类/标签/关键词筛选"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        category = request.args.get('category', '').strip()
        tag = request.args.get('tag', '').strip()
        search = request.args.get('search', '').strip()
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        user_histories = histories.get(user['id'], [])

        # 筛选
        if category:
            user_histories = [h for h in user_histories if h.get('category_id') == category]
        if tag:
            user_histories = [h for h in user_histories if tag in (h.get('tags') or [])]
        if search:
            keyword = search.lower()
            user_histories = [
                h for h in user_histories
                if keyword in (h.get('module_name', '') or '').lower()
                or keyword in (str(h.get('input_data', ''))).lower()
                or keyword in (str(h.get('result_data', ''))).lower()
            ]

        user_histories.sort(key=lambda x: x.get('create_time', ''), reverse=True)
        
        return jsonify({'success': True, 'histories': user_histories}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/divination-history/<history_id>', methods=['GET'])
def get_divination_detail(history_id):
    """获取单个占卜历史详情"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        user_histories = histories.get(user['id'], [])
        for h in user_histories:
            if h['id'] == history_id:
                return jsonify({'success': True, 'history': h}), 200
        
        return jsonify({'success': False, 'message': '记录不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/divination-history/<history_id>', methods=['DELETE'])
def delete_divination_history(history_id):
    """删除占卜历史"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        if user['id'] in histories:
            histories[user['id']] = [h for h in histories[user['id']] if h['id'] != history_id]
            with open(DIVINATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(histories, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 通知设置 ==========
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')

# 确保通知文件存在
if not os.path.exists(NOTIFICATIONS_FILE):
    with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@bp.route('/api/help/<topic>', methods=['GET'])
def get_help_topic(topic):
    """获取帮助主题内容"""
    try:
        help_topics = {
            'register': {
                'title': '如何注册账号？',
                'content': '点击首页"注册"按钮，输入用户名、密码、邮箱或手机号，完成验证后即可注册成功。'
            },
            'login': {
                'title': '如何登录账号？',
                'content': '点击首页"登录"按钮，输入用户名/邮箱/手机号和密码即可登录。支持记住密码功能。'
            },
            'fortune': {
                'title': '算命结果准确吗？',
                'content': '算命结果仅供参考，不可全信。命运掌握在自己手中，算命只是提供一种思路和方向。'
            },
            'vip': {
                'title': '如何获得VIP会员？',
                'content': '每天登录自动随机获得1-6小时VIP会员时长，每日签到还可额外获得积分和VIP时长奖励。'
            },
            'avatar': {
                'title': '如何上传头像？',
                'content': '进入个人中心，点击头像区域，选择图片上传即可。系统会自动审核头像内容。'
            },
            'contact': {
                'title': '如何联系客服？',
                'content': '发送邮件至 support@xuanji.com，我们的客服团队会在24小时内回复您。'
            }
        }
        
        if topic in help_topics:
            return jsonify({
                'success': True,
                'topic': help_topics[topic]
            }), 200
        else:
            return jsonify({'success': False, 'message': '帮助主题不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 关于我们 ==========
@bp.route('/api/about', methods=['GET'])
def get_about():
    """获取关于我们信息"""
    try:
        about_info = {
            'site_name': '玄机算命网',
            'version': '1.0.0',
            'description': '传承千年智慧，揭秘命运玄机。我们致力于为用户提供专业、准确的算命服务。',
            'contact_email': 'support@xuanji.com',
            'website': 'https://xuanji.com',
            'icp': '京ICP备XXXXXXXX号-1',
            'police_icp': '京公网安备 XXXXXXXXXXXXX号',
            'copyright': '© 2026 玄机算命网 版权所有'
        }
        
        return jsonify({
            'success': True,
            'about': about_info
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 亲友档案库 ==========
CONTACTS_FILE = os.path.join(DATA_DIR, 'contacts.json')

if not os.path.exists(CONTACTS_FILE):
    with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    """获取联系人列表，支持搜索和关系筛选"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        search = request.args.get('search', '').strip()
        relation = request.args.get('relation', '').strip()

        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                contacts_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        user_contacts = contacts_data.get(user['id'], [])

        # 筛选
        if search:
            user_contacts = [c for c in user_contacts if search.lower() in c.get('name', '').lower()]
        if relation:
            user_contacts = [c for c in user_contacts if c.get('relation') == relation]

        # 按创建时间倒序
        user_contacts.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({'success': True, 'contacts': user_contacts}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/contacts/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    """获取单个联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                contacts_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        for c in contacts_data.get(user['id'], []):
            if c['id'] == contact_id:
                return jsonify({'success': True, 'contact': c}), 200

        return jsonify({'success': False, 'message': '联系人不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/contacts', methods=['POST'])
def add_contact():
    """添加联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        name = (data.get('name', '') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入姓名'}), 400

        birthday = data.get('birthday', '')
        gender = data.get('gender', '')
        relation = data.get('relation', '')
        notes = data.get('notes', '')

        now = datetime.now().isoformat()
        contact = {
            'id': 'contact_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'name': name,
            'birthday': birthday,
            'gender': gender,
            'relation': relation,
            'notes': notes,
            'created_at': now,
            'updated_at': now
        }

        with open(CONTACTS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                contacts_data = json.load(f)
                if user['id'] not in contacts_data:
                    contacts_data[user['id']] = []
                contacts_data[user['id']].append(contact)
                f.seek(0)
                f.truncate()
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '添加成功', 'contact': contact}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/contacts/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """更新联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()

        with open(CONTACTS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                contacts_data = json.load(f)

                user_contacts = contacts_data.get(user['id'], [])
                found = False
                for c in user_contacts:
                    if c['id'] == contact_id:
                        if 'name' in data:
                            c['name'] = data['name'].strip()
                        if 'birthday' in data:
                            c['birthday'] = data['birthday']
                        if 'gender' in data:
                            c['gender'] = data['gender']
                        if 'relation' in data:
                            c['relation'] = data['relation']
                        if 'notes' in data:
                            c['notes'] = data['notes']
                        c['updated_at'] = datetime.now().isoformat()
                        found = True
                        break

                if not found:
                    return jsonify({'success': False, 'message': '联系人不存在'}), 404

                f.seek(0)
                f.truncate()
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '更新成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """删除联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CONTACTS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                contacts_data = json.load(f)

                if user['id'] in contacts_data:
                    contacts_data[user['id']] = [
                        c for c in contacts_data[user['id']] if c['id'] != contact_id
                    ]

                f.seek(0)
                f.truncate()
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 自定义数据表格 ==========
DATASETS_FILE = os.path.join(DATA_DIR, 'datasets.json')

if not os.path.exists(DATASETS_FILE):
    with open(DATASETS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)



@bp.route('/api/divination-history/<history_id>/classify', methods=['PUT'])
def classify_history(history_id):
    """设置历史记录的分类和标签"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        category_id = data.get('category_id', '')
        tags = data.get('tags', [])

        with open(DIVINATION_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                histories = json.load(f)

                if user['id'] in histories:
                    for h in histories[user['id']]:
                        if h['id'] == history_id:
                            h['category_id'] = category_id
                            h['tags'] = tags
                            f.seek(0)
                            f.truncate()
                            json.dump(histories, f, ensure_ascii=False, indent=2)
                            return jsonify({'success': True, 'message': '分类设置成功'}), 200

                return jsonify({'success': False, 'message': '记录不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 占卜历史（增强：支持筛选） ==========
# 覆盖原有的 GET /api/divination-history，增加 category/tag/search 参数
# 注意：此路由在之前已注册，这里通过修改原函数逻辑来实现增强
# 由于 Flask 不支持同一路由重复注册，需要修改上方已有的 get_divination_history 函数

# ===== 临时文件上传端点（运维用）=====