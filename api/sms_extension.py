"""
短信验证码扩展模块（号码认证服务版）
使用阿里云号码认证服务API：SendSmsVerifyCode + CheckSmsVerifyCode
无需申请签名和模板，使用系统预置签名和模板
配置文件: api/sms_config.json
"""
import re
import json
import os
import logging
from datetime import datetime, timedelta
from flask import jsonify, request

# 获取配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'sms_config.json')

logger = logging.getLogger(__name__)

# 本地频率控制存储（仅用于发送间隔限制）
sms_rate_limit = {}


def load_sms_config():
    """加载短信配置"""
    if not os.path.exists(CONFIG_FILE):
        return {'provider': 'demo'}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"加载短信配置失败: {e}")
        return {'provider': 'demo'}


def get_access_key():
    """获取AccessKey，优先从环境变量读取"""
    ak_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
    ak_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')
    if ak_id and ak_secret:
        return ak_id, ak_secret
    config = load_sms_config()
    aliyun = config.get('aliyun', {})
    return aliyun.get('access_key_id', ''), aliyun.get('access_key_secret', '')


def is_demo_mode():
    """判断是否为演示模式"""
    config = load_sms_config()
    provider = config.get('provider', '').lower()
    if not provider or provider == 'demo':
        return True
    if provider == 'aliyun':
        ak_id, ak_secret = get_access_key()
        if not ak_id or not ak_secret or 'YOUR_' in ak_id or 'YOUR_' in ak_secret:
            return True
        return False
    return True


def create_dypns_client():
    """创建号码认证服务客户端"""
    access_key_id, access_key_secret = get_access_key()

    from alibabacloud_dypnsapi20170525.client import Client
    from alibabacloud_tea_openapi import models as open_api_models

    sdk_config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    sdk_config.endpoint = 'dypnsapi.aliyuncs.com'
    return Client(sdk_config)


def send_aliyun_verify_code(phone):
    """调用阿里云 SendSmsVerifyCode 发送验证码"""
    config = load_sms_config()
    aliyun = config.get('aliyun', {})
    sign_name = aliyun.get('sign_name', '速通互联验证码')
    template_code = aliyun.get('template_code', '100001')

    try:
        from alibabacloud_dypnsapi20170525 import models as dypns_models

        client = create_dypns_client()

        request = dypns_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=sign_name,
            template_code=template_code,
            template_param='{"code":"##code##","min":"5"}',
            code_type=1,
            code_length=6,
            valid_time=300,
            duplicate_policy=1,
            interval=60,
            return_verify_code=True,
            auto_retry=1,
        )

        response = client.send_sms_verify_code(request)

        if response.body.success and response.body.code == 'OK':
            verify_code = None
            if response.body.model:
                verify_code = response.body.model.verify_code
            logger.info(f"阿里云验证码发送成功: {phone}")
            return True, '发送成功', verify_code
        else:
            err_msg = response.body.message or '发送失败'
            logger.error(f"阿里云验证码发送失败: {phone}, {err_msg}")
            return False, err_msg, None

    except ImportError as e:
        logger.error(f"号码认证SDK未安装: {e}")
        return False, 'SDK未安装', None
    except Exception as e:
        logger.error(f"阿里云验证码发送失败: {phone}, {e}")
        return False, str(e), None


def verify_aliyun_code(phone, code):
    """调用阿里云 CheckSmsVerifyCode 验证验证码"""
    try:
        from alibabacloud_dypnsapi20170525 import models as dypns_models

        client = create_dypns_client()

        request = dypns_models.CheckSmsVerifyCodeRequest(
            phone_number=phone,
            verify_code=code,
            case_auth_policy=1,
        )

        response = client.check_sms_verify_code(request)

        if response.body.success and response.body.code == 'OK':
            result = response.body.model.verify_result
            if result == 'PASS':
                return True, '验证成功'
            else:
                return False, '验证码错误'
        else:
            err_msg = response.body.message or '验证失败'
            logger.error(f"阿里云验证码验证接口失败: {phone}, {err_msg}")
            return False, err_msg

    except ImportError:
        return False, 'SDK未安装'
    except Exception as e:
        logger.error(f"阿里云验证码验证失败: {phone}, {e}")
        return False, str(e)


def generate_demo_code():
    """生成演示模式验证码"""
    import random
    return ''.join(random.choices('0123456789', k=6))


def register_sms_routes(app):
    """注册短信验证码相关路由"""

    @app.route('/api/sms/send', methods=['POST'])
    def send_sms_captcha():
        """发送短信验证码"""
        try:
            data = request.get_json()
            phone = data.get('phone', '').strip()

            if not phone:
                return jsonify({'success': False, 'message': '手机号不能为空'}), 400

            if not re.match(r'^1[3-9]\d{9}$', phone):
                return jsonify({'success': False, 'message': '手机号格式不正确'}), 400

            # 频率限制：60秒内不能重复发送
            if phone in sms_rate_limit:
                last_sent = sms_rate_limit[phone]
                elapsed = (datetime.now() - last_sent).total_seconds()
                if elapsed < 60:
                    wait = int(60 - elapsed)
                    return jsonify({
                        'success': False,
                        'message': f'请{wait}秒后再获取验证码'
                    }), 429

            # 根据配置选择发送方式
            demo = is_demo_mode()

            if not demo:
                sms_success, sms_msg, verify_code = send_aliyun_verify_code(phone)
                if sms_success:
                    sms_rate_limit[phone] = datetime.now()
                    return jsonify({
                        'success': True,
                        'message': '验证码已发送，请注意查收',
                    }), 200
                else:
                    logger.warning(f"阿里云发送失败，降级到演示模式: {sms_msg}")
                    demo = True

            if demo:
                code = generate_demo_code()
                sms_rate_limit[phone] = datetime.now()
                logger.info(f"【演示模式】手机号: {phone}, 验证码: {code}")
                return jsonify({
                    'success': True,
                    'message': '验证码已发送（演示模式）',
                    'code': code,
                    'demo': True
                }), 200

        except Exception as e:
            logger.error(f'发送短信验证码失败: {e}')
            return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500

    @app.route('/api/sms/verify', methods=['POST'])
    def verify_sms_captcha():
        """验证短信验证码"""
        try:
            data = request.get_json()
            phone = data.get('phone', '').strip()
            code = data.get('code', '').strip()

            if not phone or not code:
                return jsonify({'success': False, 'message': '手机号和验证码不能为空'}), 400

            if not re.match(r'^1[3-9]\d{9}$', phone):
                return jsonify({'success': False, 'message': '手机号格式不正确'}), 400

            demo = is_demo_mode()

            if not demo:
                ok, msg = verify_aliyun_code(phone, code)
                if ok:
                    return jsonify({'success': True, 'message': '验证成功'}), 200
                else:
                    return jsonify({'success': False, 'message': msg}), 400
            else:
                # 演示模式：直接返回成功（演示模式不验证）
                return jsonify({'success': True, 'message': '验证成功（演示模式）'}), 200

        except Exception as e:
            logger.error(f'验证短信验证码失败: {e}')
            return jsonify({'success': False, 'message': f'验证失败: {str(e)}'}), 500
