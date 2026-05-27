"""
短信验证码扩展模块
支持阿里云短信、腾讯云短信，以及演示模式
配置文件: api/sms_config.json
"""
import re
import json
import string
import random
import os
import logging
from datetime import datetime, timedelta
from flask import jsonify, request

# 获取配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'sms_config.json')

# 短信验证码存储
sms_captcha_store = {}

logger = logging.getLogger(__name__)


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


def is_demo_mode():
    """判断是否为演示模式"""
    config = load_sms_config()
    provider = config.get('provider', '').lower()
    if not provider or provider == 'demo':
        return True
    # 检查密钥是否已填写
    if provider == 'aliyun':
        aliyun = config.get('aliyun', {})
        return 'YOUR_' in aliyun.get('access_key_id', 'YOUR_')
    if provider == 'tencent':
        tencent = config.get('tencent', {})
        return 'YOUR_' in tencent.get('secret_id', 'YOUR_')
    return True


def send_aliyun_sms(phone, code):
    """发送阿里云短信"""
    config = load_sms_config()
    aliyun = config.get('aliyun', {})

    access_key_id = aliyun.get('access_key_id', '')
    access_key_secret = aliyun.get('access_key_secret', '')
    sign_name = aliyun.get('sign_name', '玄机算命网')
    template_code = aliyun.get('template_code', '')

    try:
        from aliyunsdk.core import client
        from aliyunsdk.request.v20170525 import SendSmsRequest

        clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')

        req = SendSmsRequest.SendSmsRequest()
        req.set_PhoneNumbers(phone)
        req.set_SignName(sign_name)
        req.set_TemplateCode(template_code)
        req.set_TemplateParam(json.dumps({'code': code}))

        response = clt.do_action_with_exception(req)
        result = json.loads(response)

        if result.get('Code') == 'OK':
            logger.info(f"阿里云短信发送成功: {phone}")
            return True, '发送成功'
        else:
            err_msg = result.get('Message', '发送失败')
            logger.error(f"阿里云短信发送失败: {phone}, {err_msg}")
            return False, err_msg
    except ImportError:
        logger.error("阿里云短信SDK未安装: pip3 install aliyun-python-sdk-dysmsapi")
        return False, 'SDK未安装'
    except Exception as e:
        logger.error(f"阿里云短信发送失败: {phone}, {e}")
        return False, str(e)


def send_tencent_sms(phone, code):
    """发送腾讯云短信"""
    config = load_sms_config()
    tencent = config.get('tencent', {})

    secret_id = tencent.get('secret_id', '')
    secret_key = tencent.get('secret_key', '')
    sms_sdk_app_id = tencent.get('sms_sdk_app_id', '')
    sign_name = tencent.get('sign_name', '玄机算命网')
    template_id = tencent.get('template_id', '')

    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.sms.v20210111 import sms_client, models

        cred = credential.Credential(secret_id, secret_key)
        hp = HttpProfile()
        hp.scheme = 'https'
        cpf = ClientProfile()
        cpf.http_profile = hp
        client_obj = sms_client.SmsClient(cred, 'ap-guangzhou', cpf)

        req = models.SendSmsRequest()
        req.SmsSdkAppId = sms_sdk_app_id
        req.SignName = sign_name
        req.TemplateId = str(template_id)
        req.TemplateParam = json.dumps([code])
        req.PhoneNumberSet = [f"+86{phone}"]

        resp = client_obj.SendSms(req)
        result = json.loads(resp.to_json_string())

        if result.get('SendStatusSet')[0].get('Code') == 'Ok':
            logger.info(f"腾讯云短信发送成功: {phone}")
            return True, '发送成功'
        else:
            err_msg = result.get('SendStatusSet')[0].get('Message', '发送失败')
            logger.error(f"腾讯云短信发送失败: {phone}, {err_msg}")
            return False, err_msg
    except ImportError:
        logger.error("腾讯云短信SDK未安装: pip3 install tencentcloud-sdk-python-sms")
        return False, 'SDK未安装'
    except Exception as e:
        logger.error(f"腾讯云短信发送失败: {phone}, {e}")
        return False, str(e)


def generate_sms_code():
    """生成6位随机数字验证码"""
    return ''.join(random.choices(string.digits, k=6))


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
            if phone in sms_captcha_store:
                last_sent = sms_captcha_store[phone].get('send_time')
                if last_sent:
                    elapsed = (datetime.now() - last_sent).total_seconds()
                    if elapsed < 60:
                        wait = int(60 - elapsed)
                        return jsonify({
                            'success': False,
                            'message': f'请{wait}秒后再获取验证码'
                        }), 429

            code = generate_sms_code()

            # 存储验证码（5分钟有效期）
            sms_captcha_store[phone] = {
                'code': code,
                'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat(),
                'try_count': 0,
                'send_time': datetime.now()
            }

            # 根据配置选择发送方式
            demo = is_demo_mode()
            sms_success = False

            if not demo:
                config = load_sms_config()
                provider = config.get('provider', '').lower()

                if provider == 'aliyun':
                    sms_success, sms_msg = send_aliyun_sms(phone, code)
                elif provider == 'tencent':
                    sms_success, sms_msg = send_tencent_sms(phone, code)
                else:
                    demo = True

                if not sms_success:
                    # 发送失败，降级到演示模式
                    logger.warning(f"短信发送失败，降级到演示模式: {sms_msg}")
                    demo = True

            if demo:
                logger.info(f"【演示模式】手机号: {phone}, 验证码: {code}")
                return jsonify({
                    'success': True,
                    'message': '验证码已发送（演示模式）',
                    'code': code,
                    'demo': True
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': '验证码已发送，请注意查收',
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

            if phone not in sms_captcha_store:
                return jsonify({'success': False, 'message': '验证码已失效，请重新获取'}), 400

            captcha_data = sms_captcha_store[phone]
            expire_time = datetime.fromisoformat(captcha_data['expire_time'])

            if datetime.now() > expire_time:
                del sms_captcha_store[phone]
                return jsonify({'success': False, 'message': '验证码已过期，请重新获取'}), 400

            if captcha_data.get('try_count', 0) >= 5:
                del sms_captcha_store[phone]
                return jsonify({'success': False, 'message': '验证次数过多，请重新获取验证码'}), 400

            if captcha_data['code'] != code:
                sms_captcha_store[phone]['try_count'] = captcha_data.get('try_count', 0) + 1
                remaining = 5 - sms_captcha_store[phone]['try_count']
                return jsonify({
                    'success': False,
                    'message': f'验证码错误，还剩{remaining}次机会'
                }), 400

            # 验证成功
            del sms_captcha_store[phone]
            return jsonify({'success': True, 'message': '验证成功'}), 200

        except Exception as e:
            logger.error(f'验证短信验证码失败: {e}')
            return jsonify({'success': False, 'message': f'验证失败: {str(e)}'}), 500
