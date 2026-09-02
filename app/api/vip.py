"""VIP 会员路由：状态/广告奖励/签到/兑换/转盘"""

from config import IDCARD_SAVE_DIR
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.api.deps import _vip_service

import base64
import os


from app.api.deps import _ensure_vip_fields, _get_auth_user, load_users, save_users

bp = Blueprint('vip', __name__)

@bp.route('/api/vip/status', methods=['GET'])
def vip_status():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = _vip_service()
        return jsonify(svc.get_status(user, users)), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/vip/watch-ad', methods=['POST'])
def vip_watch_ad():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = _vip_service()
        data, status = svc.watch_ad(user, users, 'personal')
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/vip/bottom-ad', methods=['POST'])
def vip_bottom_ad():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = _vip_service()
        data, status = svc.watch_ad(user, users, 'bottom')
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/vip/checkin', methods=['POST'])
def vip_checkin():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = _vip_service()
        data, status = svc.do_checkin(user, users)
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/vip/redeem', methods=['POST'])
def vip_redeem():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        data_req = request.get_json() or {}
        redeem_type = data_req.get('type', '')
        svc = _vip_service()
        data, status = svc.do_redeem(user, users, redeem_type)
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/vip/wheel', methods=['POST'])
def vip_wheel():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = _vip_service()
        data, status = svc.do_wheel(user, users)
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 头像上传（带自动审核）==========
from app.services.avatar_audit import AvatarAuditor


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
