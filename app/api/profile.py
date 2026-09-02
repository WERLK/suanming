"""用户路由：资料/实名认证/头像/通知/隐私设置"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import limiter

from app.api.deps import load_users
from app.api.deps import save_users
from app.extensions import limiter
from app.services.avatar_audit import AvatarAuditor
from app.services.nickname import generate_random_avatar
from app.services.nickname import generate_random_nickname
from app.services.security import verify_token

import base64
import json
import os


from app.api.deps import (_ensure_linked_accounts, _ensure_realname_fields,
                         _ensure_tutorial_field, _get_auth_user)
from config import AVATAR_SAVE_DIR, DATA_DIR, IDCARD_SAVE_DIR, NOTIFICATIONS_FILE

os.makedirs(AVATAR_SAVE_DIR, exist_ok=True)
os.makedirs(IDCARD_SAVE_DIR, exist_ok=True)

bp = Blueprint('profile', __name__)

@bp.route('/api/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        users = load_users()
        user = None
        for u in users:
            if u['id'] == user_id:
                user = u
                break
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        # 懒初始化：已有用户未设置昵称/头像时自动分配
        need_save = False
        if not user.get('nickname'):
            user['nickname'] = generate_random_nickname()
            need_save = True
        # 仅在 avatar_type 完全缺失时初始化（自定义头像的 preset 为空字符串，不应被覆盖）
        if not user.get('avatar_type'):
            user['avatar_type'] = 'emoji'
            user['avatar_preset'] = generate_random_avatar()
            need_save = True
        _ensure_tutorial_field(user)
        _ensure_linked_accounts(user)
        if need_save:
            for i, u in enumerate(users):
                if u['id'] == user['id']:
                    users[i] = user
                    break
            save_users(users)
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'nickname': user.get('nickname', user['username']),
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'avatar_type': user.get('avatar_type', ''),
            'avatar_preset': user.get('avatar_preset', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', ''),
            'create_time': user.get('create_time', ''),
            'last_login': user.get('last_login', ''),
            'vip_level': user.get('vip_level', 'free'),
            'vip_expire': user.get('vip_expire', None),
            'ad_watch_count': user.get('ad_watch_count', 0),
            # 实名认证
            'id_verified': user.get('id_verified', False),
            'id_region': user.get('id_region', ''),
            'real_name': user.get('real_name', ''),
            'id_last4': user.get('id_last4', ''),
            'verify_time': user.get('verify_time', ''),
            'idcard_image': user.get('idcard_image', ''),  # 兼容旧字段
            'idcard_image_front': user.get('idcard_image_front', ''),
            'idcard_image_back': user.get('idcard_image_back', ''),
            'idcard_upload_time': user.get('idcard_upload_time', ''),
            'tutorial_shown': user.get('tutorial_shown', True)
        }
        return jsonify({'success': True, 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '获取用户信息失败'}), 500

@bp.route('/api/profile/tutorial-done', methods=['POST'])
def tutorial_done():
    """标记新手教程已完成（服务端记录，清除浏览器数据也不重复显示）"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        users = load_users()
        updated = False
        for i, u in enumerate(users):
            if u['id'] == user_id:
                u['tutorial_shown'] = True
                users[i] = u
                updated = True
                break
        if not updated:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        save_users(users)
        return jsonify({'success': True, 'message': '已标记'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

@bp.route('/api/notify-subscribe', methods=['POST'])
def notify_subscribe():
    """App上线通知订阅"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': '请输入有效的邮箱地址'}), 400

        source = data.get('source', 'website')
        subscribers_file = os.path.join(DATA_DIR, 'app_subscribers.json')
        subscribers = []
        if os.path.exists(subscribers_file):
            with open(subscribers_file, 'r', encoding='utf-8') as f:
                subscribers = json.load(f)

        # 避免重复
        for s in subscribers:
            if s.get('email') == email:
                return jsonify({'success': True, 'message': '您已订阅过，App上线时将通知您'}), 200

        subscribers.append({
            'email': email,
            'source': source,
            'subscribe_time': datetime.now().isoformat(),
            'notified': False
        })

        with open(subscribers_file, 'w', encoding='utf-8') as f:
            json.dump(subscribers, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '订阅成功！App上线时将通知您'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

@bp.route('/api/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        data = request.get_json()
        users = load_users()
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user_index = i
                break
        if user_index is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        allowed_fields = ['username', 'nickname', 'email', 'phone', 'avatar', 'birthday', 'gender']
        # 唯一性校验：username/email/phone 不得与其他用户冲突（排除自身）
        for unique_field in ('username', 'email', 'phone'):
            new_val = data.get(unique_field, '')
            if new_val:
                new_val = str(new_val).strip()
                for u in users:
                    if u['id'] != user_id and str(u.get(unique_field, '')).strip() == new_val:
                        return jsonify({'success': False, 'message': f'{unique_field} 已被其他用户占用'}), 409
        for field in allowed_fields:
            if field in data:
                users[user_index][field] = data[field]
        save_users(users)
        user = users[user_index]
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'nickname': user.get('nickname', user['username']),
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'avatar_type': user.get('avatar_type', ''),
            'avatar_preset': user.get('avatar_preset', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', '')
        }
        return jsonify({'success': True, 'message': '更新成功', 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '更新用户信息失败'}), 500


@limiter.limit("3 per minute")
@bp.route('/api/profile/verify-realname', methods=['POST'])
def verify_realname():
    """实名认证：提交姓名+身份证号+可选身份证照片，本地校验并存储"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.get_json()
        real_name = (data.get('real_name', '') or '').strip()
        id_number = (data.get('id_number', '') or '').strip()
        idcard_image_front = (data.get('idcard_image_front', '') or data.get('idcard_image', '') or '').strip()  # 正面
        idcard_image_back = (data.get('idcard_image_back', '') or '').strip()   # 反面

        if not real_name or len(real_name) < 2:
            return jsonify({'success': False, 'message': '请输入真实姓名'}), 400
        if not id_number:
            return jsonify({'success': False, 'message': '请输入身份证号'}), 400

        # 身份证校验
        from app.services.idcard import validate_id_card, mask_name, mask_id_last4
        import hashlib

        check = validate_id_card(id_number)
        if not check['valid']:
            return jsonify({'success': False, 'message': check['error']}), 400

        # 查找用户
        users = load_users()
        user_idx = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user = u
                user_idx = i
                break
        if user_idx is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 检查是否已认证
        _ensure_realname_fields(user)
        if user.get('id_verified'):
            # 已认证用户仍可补充上传身份证照片
            updated = False
            if idcard_image_front and not user.get('idcard_image_front'):
                saved_url = _save_idcard_image(user_id, idcard_image_front, 'front')
                if saved_url:
                    user['idcard_image_front'] = saved_url
                    user['idcard_upload_time'] = datetime.now().isoformat()
                    updated = True
            if idcard_image_back and not user.get('idcard_image_back'):
                saved_url = _save_idcard_image(user_id, idcard_image_back, 'back')
                if saved_url:
                    user['idcard_image_back'] = saved_url
                    user['idcard_upload_time'] = datetime.now().isoformat()
                    updated = True
            if updated:
                users[user_idx] = user
                save_users(users)
                front_ok = bool(user.get('idcard_image_front'))
                back_ok = bool(user.get('idcard_image_back'))
                return jsonify({
                    'success': True,
                    'message': f'身份证照片上传成功（正面{"✅" if front_ok else "❌"} 反面{"✅" if back_ok else "❌"}）',
                    'data': {
                        'real_name_masked': mask_name(user.get('real_name', '')),
                        'id_masked': mask_id_last4(user.get('id_last4', '')),
                        'region': user.get('id_region', ''),
                        'verified': True,
                        'idcard_uploaded': front_ok or back_ok,
                        'idcard_image_front': user.get('idcard_image_front', ''),
                        'idcard_image_back': user.get('idcard_image_back', '')
                    }
                }), 200
            return jsonify({'success': False, 'message': '已完成实名认证，无需重复提交或图片格式无效'}), 400

        # 存储认证信息（身份证号只存哈希）
        id_hash = hashlib.sha256(id_number.encode()).hexdigest()
        now = datetime.now().isoformat()
        user['real_name'] = real_name
        user['id_number_hash'] = id_hash
        user['id_last4'] = id_number[-4:]
        user['id_verified'] = True
        user['id_region'] = check['region_name']
        user['id_region_code'] = check['region_code']
        user['verify_time'] = now

        # 处理身份证图片（正反面）
        idcard_uploaded_front = False
        idcard_uploaded_back = False
        if idcard_image_front:
            saved_url = _save_idcard_image(user_id, idcard_image_front, 'front')
            if saved_url:
                user['idcard_image_front'] = saved_url
                user['idcard_upload_time'] = now
                idcard_uploaded_front = True
        if idcard_image_back:
            saved_url = _save_idcard_image(user_id, idcard_image_back, 'back')
            if saved_url:
                user['idcard_image_back'] = saved_url
                user['idcard_upload_time'] = now
                idcard_uploaded_back = True

        # 如果用户生日/性别为空则自动填充
        if not user.get('birthday') and check['birth_date']:
            user['birthday'] = check['birth_date']
        if not user.get('gender') and check['gender']:
            user['gender'] = 'male' if check['gender'] == 'male' else 'female'

        users[user_idx] = user
        save_users(users)

        # 更新分析数据库
        try:
            from app.services.analytics_db import snapshot_user
            snapshot_user(user_id=user_id, username=user['username'],
                         gender=user.get('gender', ''), birth_str=user.get('birthday', ''),
                         vip_level=user.get('vip_level', 'basic'),
                         id_region=user.get('id_region', ''), is_verified=True,
                         has_idcard_image=(idcard_uploaded_front or idcard_uploaded_back))
        except: pass

        parts = []
        if idcard_uploaded_front: parts.append('正面已上传')
        if idcard_uploaded_back: parts.append('反面已上传')
        upload_msg = '，'.join(parts) if parts else ''

        return jsonify({
            'success': True,
            'message': '实名认证成功' + ('（' + upload_msg + '）' if upload_msg else ''),
            'data': {
                'real_name_masked': mask_name(real_name),
                'id_masked': mask_id_last4(id_number),
                'region': check['region_name'],
                'gender': check['gender'],
                'birth_date': check['birth_date'],
                'verified': True,
                'idcard_uploaded': (idcard_uploaded_front or idcard_uploaded_back),
                'idcard_image_front': user.get('idcard_image_front', ''),
                'idcard_image_back': user.get('idcard_image_back', '')
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '认证失败'}), 500


@bp.route('/api/profile/realname-status', methods=['GET'])
def realname_status():
    """查询实名认证状态"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        users = load_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        _ensure_realname_fields(user)
        from app.services.idcard import mask_name, mask_id_last4

        if user.get('id_verified'):
            return jsonify({
                'success': True,
                'verified': True,
                'data': {
                    'real_name_masked': mask_name(user.get('real_name', '')),
                    'id_masked': mask_id_last4(user.get('id_last4', '')),
                    'region': user.get('id_region', ''),
                    'verify_time': user.get('verify_time', ''),
                    'idcard_image_front': user.get('idcard_image_front', ''),
                    'idcard_image_back': user.get('idcard_image_back', ''),
                    'idcard_upload_time': user.get('idcard_upload_time', '')
                }
            }), 200
        else:
            return jsonify({'success': True, 'verified': False, 'message': '未认证'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500


@bp.route('/api/profile/upload-idcard', methods=['POST'])
def upload_idcard():
    """单独上传身份证照片（已认证用户补充上传，支持正反面）"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.get_json()
        idcard_image_front = (data.get('idcard_image_front', '') or data.get('idcard_image', '') or '').strip()
        idcard_image_back = (data.get('idcard_image_back', '') or '').strip()

        if not idcard_image_front and not idcard_image_back:
            return jsonify({'success': False, 'message': '请上传身份证照片（正面或反面）'}), 400

        users = load_users()
        user_idx = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user = u
                user_idx = i
                break
        if user_idx is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        _ensure_realname_fields(user)

        saved_front = None
        saved_back = None
        if idcard_image_front:
            saved_front = _save_idcard_image(user_id, idcard_image_front, 'front')
        if idcard_image_back:
            saved_back = _save_idcard_image(user_id, idcard_image_back, 'back')

        if not saved_front and not saved_back:
            return jsonify({'success': False, 'message': '图片格式无效或超过10MB'}), 400

        now = datetime.now().isoformat()
        if saved_front:
            user['idcard_image_front'] = saved_front
        if saved_back:
            user['idcard_image_back'] = saved_back
        user['idcard_upload_time'] = now
        users[user_idx] = user
        save_users(users)

        return jsonify({
            'success': True,
            'message': '身份证照片上传成功',
            'data': {
                'idcard_image_front': user.get('idcard_image_front', ''),
                'idcard_image_back': user.get('idcard_image_back', ''),
                'idcard_upload_time': now
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

@limiter.limit("3 per minute")  # 忘记密码限制：每分钟 3 次

@bp.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    """上传头像（自动审核）"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'success': False, 'message': '请上传图片'}), 400
        
        # 1. 自动审核头像
        audit_result = AvatarAuditor.audit_avatar(image_data)
        
        if audit_result['result'] == 'block':
            return jsonify({
                'success': False, 'message': f'头像审核未通过：{audit_result["reason"]}',
                'audit_result': audit_result
            }), 400
        
        # 2. 审核通过或需复审，处理图片
        # 移除 base64 前缀
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # 3. 缩放头像到标准尺寸
        avatar_bytes = AvatarAuditor.resize_avatar(image_bytes, size=(200, 200))
        
        # 4. 保存头像文件
        avatar_filename = f"{user['id']}_{int(datetime.now().timestamp())}.jpg"
        avatar_path = os.path.join(AVATAR_SAVE_DIR, avatar_filename)
        
        with open(avatar_path, 'wb') as f:
            f.write(avatar_bytes)
        
        # 5. 更新用户头像路径
        avatar_url = f'/static/avatars/{avatar_filename}'
        
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user['id']:
                user_index = i
                break
        
        if user_index is not None:
            users[user_index]['avatar'] = avatar_url
            save_users(users)
        
        # 6. 返回结果
        response_data = {
            'success': True, 'message': '头像上传成功' if audit_result['result'] == 'pass' else '头像已上传，待人工复审',
            'avatar_url': avatar_url,
            'audit_result': audit_result
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        print(f'[Avatar Upload Error] {traceback.format_exc()}', flush=True)
        return jsonify({'success': False, 'message': '头像上传失败'}), 500

@bp.route('/api/avatar/set-preset', methods=['POST'])
def set_preset_avatar():
    """设置系统预设头像"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result

        data = request.get_json()
        avatar_type = data.get('type', 'emoji')  # emoji | letter | color
        avatar_value = data.get('value', '')

        if not avatar_value:
            return jsonify({'success': False, 'message': '请选择头像'}), 400

        # 更新用户头像
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user['id']:
                user_index = i
                break

        if user_index is not None:
            users[user_index]['avatar_type'] = avatar_type
            users[user_index]['avatar_preset'] = avatar_value
            users[user_index]['avatar'] = None  # 清除自定义头像
            save_users(users)

        return jsonify({
            'success': True,
            'message': '头像设置成功',
            'avatar_type': avatar_type,
            'avatar_value': avatar_value
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '头像设置失败'}), 500

# ========== 收藏功能 ==========
FAVORITES_FILE = os.path.join(DATA_DIR, 'favorites.json')

# 确保收藏文件存在
if not os.path.exists(FAVORITES_FILE):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@bp.route('/api/notifications/settings', methods=['GET'])
def get_notification_settings():
    """获取通知设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        settings = notifications.get(user['id'], {
            'push_enabled': True,
            'email_enabled': True,
            'sms_enabled': False,
            'daily_fortune': True,
            'vip_expire': True,
            'system_notice': True
        })
        
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

@bp.route('/api/notifications/settings', methods=['PUT'])
def update_notification_settings():
    """更新通知设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        if user['id'] not in notifications:
            notifications[user['id']] = {}
        
        # 更新设置
        notifications[user['id']].update(data)
        
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '设置已保存'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

# ========== 隐私设置 ==========
PRIVACY_FILE = os.path.join(DATA_DIR, 'privacy.json')

# 确保隐私文件存在
if not os.path.exists(PRIVACY_FILE):
    with open(PRIVACY_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@bp.route('/api/privacy/settings', methods=['GET'])
def get_privacy_settings():
    """获取隐私设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(PRIVACY_FILE, 'r', encoding='utf-8') as f:
            privacy = json.load(f)
        
        settings = privacy.get(user['id'], {
            'profile_public': True,
            'fortune_public': False,
            'allow_search': True,
            'show_online': False
        })
        
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

@bp.route('/api/privacy/settings', methods=['PUT'])
def update_privacy_settings():
    """更新隐私设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        
        with open(PRIVACY_FILE, 'r', encoding='utf-8') as f:
            privacy = json.load(f)
        
        if user['id'] not in privacy:
            privacy[user['id']] = {}
        
        # 更新设置
        privacy[user['id']].update(data)
        
        with open(PRIVACY_FILE, 'w', encoding='utf-8') as f:
            json.dump(privacy, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '隐私设置已保存'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '操作失败'}), 500

# ========== 帮助中心 ==========

# ---------- 实名认证辅助 ----------

def _save_idcard_image(user_id, image_data, suffix=''):
    """保存身份证图片（自动缩放），返回URL或None
    
    Args:
        user_id: 用户ID
        image_data: base64图片数据
        suffix: 文件名后缀，如 '_front' / '_back'，用于区分正反面
    """
    try:
        # 移除 base64 前缀
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        image_bytes = base64.b64decode(image_data)

        # 限制解码后大小：最大 10MB（压缩前，后续会缩放）
        if len(image_bytes) > 10 * 1024 * 1024:
            return None

        # 用 PIL 缩放身份证图片（保留文字细节，最大宽度 1200px）
        try:
            from PIL import Image
            import io
            Image.MAX_IMAGE_PIXELS = 50_000_000  # 防解压炸弹
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            img = Image.open(io.BytesIO(image_bytes))
            if img.width * img.height > 50_000_000:
                return None
            w, h = img.size
            if w > 1200:
                ratio = 1200.0 / w
                new_w = 1200
                new_h = int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
            # 转 JPEG 保存
            buf = io.BytesIO()
            img_format = img.format or 'JPEG'
            if img_format.upper() == 'PNG' and img.mode in ('RGBA', 'LA', 'P'):
                # PNG 透明通道转白色背景
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            img.save(buf, format='JPEG', quality=85)
            image_bytes = buf.getvalue()
        except Exception:
            return None  # 安全：PIL 处理失败则拒绝保存，不回退原始 bytes

        # 保存图片
        suffix_str = f'_{suffix}' if suffix else ''
        filename = f"{user_id}{suffix_str}_{int(datetime.now().timestamp())}.jpg"
        filepath = os.path.join(IDCARD_SAVE_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        return f'/static/idcard/{filename}'
    except Exception:
        return None

