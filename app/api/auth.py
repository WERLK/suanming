"""认证路由：验证码/短信/注册/登录/登出/密码重置"""

from app.api.deps import _get_today
from app.api.deps import _safe_parse_datetime
from datetime import datetime
from datetime import timedelta

from flask import Blueprint, jsonify, request

from app.extensions import limiter

from app.api.deps import _delete_captcha_entry
from app.api.deps import _get_captcha_entry
from app.api.deps import _set_captcha_entry
from app.api.deps import load_tokens
from app.api.deps import load_users
from app.api.deps import save_tokens
from app.api.deps import save_users
from app.extensions import limiter
from app.services.analytics_db import snapshot_user
from app.services.mailer import send_email
from app.services.nickname import generate_random_avatar
from app.services.nickname import generate_random_nickname
from app.services.security import generate_token
from app.services.security import hash_password
from app.services.security import verify_password

import base64
import io
import os
import random
import string


from PIL import Image, ImageDraw, ImageFont
from app.api.deps import (_delete_captcha_entry, _ensure_linked_accounts,
                         _ensure_tutorial_field, _ensure_vip_fields, _get_captcha_entry,
                         _set_captcha_entry)
from config import AVATAR_SAVE_DIR

bp = Blueprint('auth', __name__)

@bp.route('/api/captcha/generate', methods=['GET'])
def generate_captcha():
    """生成图片验证码"""
    try:
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        width, height = 120, 40
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        for _ in range(100):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            draw.point((x, y), fill=color)
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        except (OSError, IOError):
            font = ImageFont.load_default()
        for i, char in enumerate(captcha_text):
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            x = 10 + i * 25 + random.randint(-3, 3)
            y = random.randint(5, 15)
            draw.text((x, y), char, font=font, fill=color)
        for _ in range(3):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        _set_captcha_entry(captcha_id, {
            'type': 'image',
            'text': captcha_text,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        })
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return jsonify({
            'success': True,
            'captcha_id': captcha_id,
            'captcha_image': f"data:image/png;base64,{img_base64}"
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成验证码失败: {str(e)}'}), 500

@bp.route('/api/captcha/verify', methods=['POST'])
def verify_captcha():
    """验证图片验证码"""
    try:
        data = request.get_json()
        captcha_id = data.get('captcha_id', '')
        captcha_text = data.get('captcha_text', '').strip().upper()
        if not captcha_id or not captcha_text:
            return jsonify({'success': False, 'message': '参数不完整'}), 200
        entry = _get_captcha_entry(captcha_id)
        if not entry or entry.get('type') != 'image':
            return jsonify({'success': False, 'message': '验证码已失效，请刷新'}), 200
        if entry['text'] != captcha_text:
            return jsonify({'success': False, 'message': '验证码错误'}), 200
        _delete_captcha_entry(captcha_id)
        return jsonify({'success': True, 'message': '验证成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证验证码失败: {str(e)}'}), 500

@bp.route('/api/slider/generate', methods=['GET'])
def generate_slider():
    """生成滑块验证码"""
    try:
        target_x = random.randint(20, 80)
        target_y = random.randint(30, 70)
        slider_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        _set_captcha_entry(slider_id, {
            'type': 'slider',
            'target_x': target_x,
            'target_y': target_y,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        })
        return jsonify({
            'success': True,
            'slider_id': slider_id,
            'target_x': target_x,
            'image_width': 300,
            'image_height': 150
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成滑块验证码失败: {str(e)}'}), 500

@bp.route('/api/slider/verify', methods=['POST'])
def verify_slider():
    """验证滑块验证码"""
    try:
        data = request.get_json()
        slider_id = data.get('slider_id', '')
        slider_x = data.get('slider_x', 0)
        if not slider_id or slider_x is None:
            return jsonify({'success': False, 'message': '参数不完整'}), 200
        entry = _get_captcha_entry(slider_id)
        if not entry or entry.get('type') != 'slider':
            return jsonify({'success': False, 'message': '滑块验证码已失效，请刷新'}), 200
        target_x = entry['target_x']
        if abs(slider_x - target_x) <= 5:
            _delete_captcha_entry(slider_id)
            return jsonify({'success': True, 'message': '验证成功'}), 200
        else:
            return jsonify({'success': False, 'message': '请再试一次'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证滑块验证码失败: {str(e)}'}), 500

# ========== 短信验证码 ==========

@limiter.limit("3 per minute")
@bp.route('/api/sms/send', methods=['POST'])
def send_sms():
    """发送短信验证码（阿里云）"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        if not phone or not phone.isdigit() or len(phone) != 11:
            return jsonify({'success': False, 'message': '请输入正确的手机号'}), 200
        
        # 生成验证码
        sms_code = ''.join(random.choices(string.digits, k=6))
        sms_id = 'sms_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # 尝试通过阿里云发送短信
        aliyun_sent = False
        aliyun_error = ''
        try:
            from app.services.sms import send_aliyun_sms
            success, msg = send_aliyun_sms(phone, sms_code)
            if success:
                aliyun_sent = True
            else:
                aliyun_error = msg
        except ImportError as e:
            aliyun_error = f'SDK未安装: {e}'
        except Exception as e:
            aliyun_error = f'异常: {e}'
        
        # 如果阿里云发送失败，回退演示模式
        if not aliyun_sent:
            print(f"【短信】阿里云发送失败: {aliyun_error}, 回退演示模式: phone={phone}, code={sms_code}")
        else:
            print(f"【短信】阿里云发送成功: phone={phone}")
        
        # 存储验证码（文件存储，支持多worker）
        _set_captcha_entry(sms_id, {
            'type': 'sms',
            'phone': phone,
            'code': sms_code,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'used': False
        })
        
        # 安全修复：演示模式默认不再回传明文验证码（旧版直接返回 code，可被
        # 任意访客用于伪造短信验证）。本地联调需要时显式设置 SMS_DEMO_MODE=1。
        demo_mode = os.environ.get('SMS_DEMO_MODE', '') == '1'
        return jsonify({
            'success': True,
            'message': '验证码已发送' if aliyun_sent else '验证码已发送（演示模式）',
            'sms_id': sms_id,
            'code': sms_code if (not aliyun_sent and demo_mode) else None
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500

@limiter.limit("5 per minute")
@bp.route('/api/sms/verify', methods=['POST'])
def verify_sms():
    """验证短信验证码"""
    try:
        data = request.get_json()
        sms_id = data.get('sms_id', '')
        code = data.get('code', '').strip()
        if not sms_id or not code:
            return jsonify({'success': False, 'message': '参数不完整'}), 200
        entry = _get_captcha_entry(sms_id)
        if not entry or entry.get('type') != 'sms':
            return jsonify({'success': False, 'message': '验证码已失效，请重新获取'}), 200
        if entry.get('used'):
            return jsonify({'success': False, 'message': '验证码已使用，请重新获取'}), 200
        if entry['code'] != code:
            return jsonify({'success': False, 'message': '验证码错误'}), 200
        # 标记已使用（一次性）
        entry['used'] = True
        _set_captcha_entry(sms_id, entry)
        return jsonify({'success': True, 'message': '验证成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证失败: {str(e)}'}), 500

@limiter.limit("5 per minute")  # 注册限制：每分钟 5 次

@bp.route('/api/register', methods=['POST'])
def register():
    """用户注册（支持头像选择：预设emoji 或 自定义上传）"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        avatar_type = data.get('avatar_type', 'emoji')  # emoji | custom
        avatar_preset = data.get('avatar_preset', '')    # emoji字符
        avatar_data = data.get('avatar_data', '')        # base64 custom image

        if not username or len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度应为3-20个字符'}), 400
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6个字符'}), 400
        if not username.isalnum() and '_' not in username:
            return jsonify({'success': False, 'message': '用户名只能包含字母、数字和下划线'}), 400
        users = load_users()
        if any(u['username'] == username for u in users):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        if email and any(u.get('email') == email for u in users):
            return jsonify({'success': False, 'message': '邮箱已注册'}), 400
        if phone and any(u.get('phone') == phone for u in users):
            return jsonify({'success': False, 'message': '手机号已注册'}), 400

        # 处理头像
        if avatar_type == 'custom' and avatar_data:
            # 自定义头像：先创建用户获取ID，再保存头像文件
            pass  # 延迟处理，需要先有 user_id
            avatar_preset = ''  # 自定义头像时清空预设
        elif avatar_type == 'emoji' and avatar_preset:
            # 用户选择了特定emoji
            pass
        else:
            # 未选择，随机分配
            avatar_type = 'emoji'
            avatar_preset = generate_random_avatar()

        new_user = {
            'id': 'user_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            'username': username,
            'nickname': generate_random_nickname(),
            'password': hash_password(password),
            'email': email,
            'phone': phone,
            'avatar': '',
            'avatar_type': avatar_type,
            'avatar_preset': avatar_preset,
            'birthday': '',
            'gender': '',
            'create_time': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'status': 'active',
            'vip_level': 'basic',
            'vip_expire': None,
            'ad_watch_count': 0,
            'ad_watch_date': '',
            'tutorial_shown': False,
            'linked_accounts': {}
        }

        # 处理自定义头像上传
        if avatar_type == 'custom' and avatar_data:
            try:
                from app.services.avatar_audit import AvatarAuditor
                audit_result = AvatarAuditor.audit_avatar(avatar_data)

                if audit_result['result'] == 'block':
                    return jsonify({
                        'success': False, 'message': f'头像审核未通过：{audit_result["reason"]}'
                    }), 400

                # 解码并保存头像
                clean_data = avatar_data
                if 'base64,' in clean_data:
                    clean_data = clean_data.split('base64,')[1]

                image_bytes = base64.b64decode(clean_data)
                avatar_bytes = AvatarAuditor.resize_avatar(image_bytes, size=(200, 200))

                avatar_filename = f"{new_user['id']}_{int(datetime.now().timestamp())}.jpg"
                avatar_path = os.path.join(AVATAR_SAVE_DIR, avatar_filename)

                with open(avatar_path, 'wb') as f:
                    f.write(avatar_bytes)

                new_user['avatar'] = f'/static/avatars/{avatar_filename}'
            except Exception as ave:
                import traceback
                print(f'[Register Avatar Error] {traceback.format_exc()}', flush=True)
                # 头像保存失败不影响注册，使用随机emoji兜底
                new_user['avatar_type'] = 'emoji'
                new_user['avatar_preset'] = generate_random_avatar()
                new_user['avatar'] = ''

        users.append(new_user)
        save_users(users)

        # 记录注册事件到分析数据库
        try:
            snapshot_user(user_id=new_user['id'], username=username,
                         gender='', birth_str='', vip_level='basic', is_new=True)
            from app.services.analytics_db import track_session as _ts2
            _ts2(user_id=new_user['id'], event_type='signup', page='/api/register',
                 client_ip=request.remote_addr or '')
        except: pass

        token = generate_token(new_user['id'])
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'nickname': new_user['nickname'],
                'avatar_type': new_user['avatar_type'],
                'avatar_preset': new_user['avatar_preset'],
                'avatar': new_user.get('avatar', ''),
                'tutorial_shown': False
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@limiter.limit("5 per minute")  # 登录限制：每分钟 5 次
@bp.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        users = load_users()
        user = None
        for u in users:
            if u['username'] == username or u.get('email') == username or u.get('phone') == username:
                user = u
                break
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 200
        if not verify_password(password, user['password']):
            return jsonify({'success': False, 'message': '密码错误'}), 200
        if user.get('status') != 'active':
            return jsonify({'success': False, 'message': '账户已被禁用'}), 200

        # 每日登录自动发放随机 VIP 时长
        _ensure_vip_fields(user)
        _ensure_tutorial_field(user)
        _ensure_linked_accounts(user)
        today = _get_today()
        login_reward_given = False
        login_reward_hours = 0
        if user.get('last_login_reward_date', '') != today:
            now = datetime.now()
            vip_expire = user.get('vip_expire')
            if vip_expire:
                expire_dt = _safe_parse_datetime(vip_expire)
                if expire_dt is None:
                    expire_dt = now
                elif expire_dt < now:
                    expire_dt = now
            else:
                expire_dt = now
            login_reward_hours = random.randint(1, 6)
            new_expire = expire_dt + timedelta(hours=login_reward_hours)
            user['vip_expire'] = new_expire.isoformat()
            user['vip_level'] = 'basic'
            user['last_login_reward_date'] = today
            login_reward_given = True
            # 找到用户索引并保存
            for i, u in enumerate(users):
                if u['id'] == user['id']:
                    users[i] = user
                    break

        user['last_login'] = datetime.now().isoformat()
        save_users(users)

        # 记录登录事件到分析数据库
        try:
            snapshot_user(user_id=user['id'], username=user['username'],
                         gender=user.get('gender', ''), birth_str=user.get('birthday', ''),
                         vip_level=user.get('vip_level', 'basic'))
            from app.services.analytics_db import track_session as _ts
            _ts(user_id=user['id'], event_type='login', page='/api/login',
                client_ip=request.remote_addr or '')
        except: pass

        token = generate_token(user['id'])
        response = jsonify({
            'success': True,
            'token': token,
            'login_reward': login_reward_given,
            'reward_hours': login_reward_hours,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'nickname': user.get('nickname', user['username']),
                'avatar_type': user.get('avatar_type', ''),
                'avatar_preset': user.get('avatar_preset', ''),
                'tutorial_shown': user.get('tutorial_shown', False)
            }
        })
        if remember:
            response.set_cookie('token', token, max_age=7*24*3600, httponly=True)
        else:
            response.set_cookie('token', token, httponly=True)
        return response, 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500

@bp.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    response = jsonify({'success': True, 'message': '登出成功'})
    response.delete_cookie('token')
    return response, 200


@bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码 - 发送重置邮件"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        if not email:
            return jsonify({'success': False, 'message': '邮箱不能为空'}), 400
        users = load_users()
        user = None
        for u in users:
            if u.get('email') == email:
                user = u
                break
        if not user:
            return jsonify({'success': False, 'message': '邮箱未注册'}), 404
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        tokens = load_tokens()
        tokens[reset_token] = {
            'user_id': user['id'],
            'expire_time': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        save_tokens(tokens)
        reset_link = f"{request.host_url.rstrip('/')}/reset-password.html?token={reset_token}"
        email_body = f"""
        <h2>重置密码</h2>
        <p>请点击以下链接重置您的密码（1小时内有效）：</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
        """

        # 尝试发送真实邮件
        email_sent = send_email(email, '密码重置 - 玄机算命网', email_body)

        if email_sent:
            return jsonify({
                'success': True, 'message': '重置链接已发送到您的邮箱，请注意查收',
            }), 200
        else:
            return jsonify({
                'success': True, 'message': '重置链接已生成（邮件服务未配置，请使用以下链接）',
                'reset_link': reset_link
            }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送重置邮件失败: {str(e)}'}), 500

@bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('password', '')
        if not token or not new_password:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6个字符'}), 400
        tokens = load_tokens()
        if token not in tokens:
            return jsonify({'success': False, 'message': '重置链接无效'}), 400
        token_data = tokens[token]
        expire_time = datetime.fromisoformat(token_data['expire_time'])
        if datetime.now() > expire_time:
            del tokens[token]
            save_tokens(tokens)
            return jsonify({'success': False, 'message': '重置链接已过期'}), 400
        users = load_users()
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == token_data['user_id']:
                user_index = i
                break
        if user_index is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        users[user_index]['password'] = hash_password(new_password)
        save_users(users)
        del tokens[token]
        save_tokens(tokens)
        return jsonify({'success': True, 'message': '密码重置成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'重置密码失败: {str(e)}'}), 500
