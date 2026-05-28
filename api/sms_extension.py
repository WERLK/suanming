"""
短信验证码扩展模块
可以被导入到 api/app.py 中
"""
import os
import re
import json
import string
import random
from datetime import datetime, timedelta
from flask import jsonify, request

# 短信验证码存储（实际项目中应使用Redis或数据库）
sms_captcha_store = {}

# 检测阿里云SDK是否可用
_ALIYUN_SDK_AVAILABLE = False
try:
    from aliyunsdk.core import client
    from aliyunsdk.request.v20170525 import SendSmsRequest
    _ALIYUN_SDK_AVAILABLE = True
except ImportError:
    pass

# 阿里云短信配置（从环境变量读取，不在代码中硬编码以保证安全）
ALIYUN_ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID', '')
ALIYUN_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET', '')
ALIYUN_SIGN_NAME = os.environ.get('ALIYUN_SIGN_NAME', '速通互联验证码')
ALIYUN_TEMPLATE_CODE = os.environ.get('ALIYUN_TEMPLATE_CODE', '100001')

# 腾讯云短信配置（实际使用需填写）
TENCENT_SECRET_ID = 'YOUR_SECRET_ID'                # 腾讯云SecretId
TENCENT_SECRET_KEY = 'YOUR_SECRET_KEY'              # 腾讯云SecretKey
TENCENT_SMS_SDK_APP_ID = '1400000000'              # 短信应用ID
TENCENT_SIGN_NAME = '玄机算命网'                  # 短信签名
TENCENT_TEMPLATE_ID = '123456'                        # 短信模板ID


def send_aliyun_sms(phone, code):
    """发送阿里云短信"""
    if not _ALIYUN_SDK_AVAILABLE:
        return False, 'Aliyun SDK not installed'
    try:
        from aliyunsdk.core import client
        from aliyunsdk.request.v20170525 import SendSmsRequest
        
        # 初始化客户端
        clt = client.AcsClient(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, 'default')
        
        # 创建请求
        request = SendSmsRequest.SendSmsRequest()
        request.set_PhoneNumbers(phone)
        request.set_SignName(ALIYUN_SIGN_NAME)
        request.set_TemplateCode(ALIYUN_TEMPLATE_CODE)
        request.set_TemplateParam(json.dumps({'code': code}))
        
        # 发送短信
        response = clt.do_action_with_exception(request)
        result = json.loads(response)
        
        if result.get('Code') == 'OK':
            return True, '发送成功'
        else:
            return False, result.get('Message', '发送失败')
    except Exception as e:
        print(f"阿里云短信发送失败: {e}")
        return False, str(e)


def send_tencent_sms(phone, code):
    """发送腾讯云短信"""
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.sms.v20210111 import sms_client, models
        
        # 初始化认证
        cred = credential.Credential(TENCENT_SECRET_ID, TENCENT_SECRET_KEY)
        
        # 配置HTTP参数
        hp = HttpProfile()
        hp.scheme = 'https'
        
        # 配置客户端
        cpf = ClientProfile()
        cpf.http_profile = hp
        
        # 创建客户端
        client = sms_client.SmsClient(cred, 'ap-guangzhou', cpf)
        
        # 创建请求
        req = models.SendSmsRequest()
        req.SmsSdkAppId = TENCENT_SMS_SDK_APP_ID
        req.SignName = TENCENT_SIGN_NAME
        req.TemplateId = str(TENCENT_TEMPLATE_ID)
        req.TemplateParam = json.dumps([code])
        req.PhoneNumberSet = [f"+86{phone}"]
        
        # 发送短信
        resp = client.SendSms(req)
        result = json.loads(resp.to_json_string())
        
        if result.get('SendStatusSet')[0].get('Code') == 'Ok':
            return True, '发送成功'
        else:
            return False, result.get('SendStatusSet')[0].get('Message', '发送失败')
    except Exception as e:
        print(f"腾讯云短信发送失败: {e}")
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
            
            # 验证手机号
            if not phone:
                return jsonify({'success': False, 'message': '手机号不能为空'}), 400
            
            if not re.match(r'^1[3-9]\d{9}$', phone):
                return jsonify({'success': False, 'message': '手机号格式不正确'}), 400
            
            # 生成验证码
            code = generate_sms_code()
            
            # 存储验证码（5分钟有效期）
            sms_captcha_store[phone] = {
                'code': code,
                'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat(),
                'try_count': 0  # 验证尝试次数
            }
            
            # 发送短信（实际项目中取消注释）
            # 阿里云短信
            # success, message = send_aliyun_sms(phone, code)
            
            # 腾讯云短信
            # success, message = send_tencent_sms(phone, code)
            
            # 演示模式：直接返回验证码
            print(f"【演示模式】手机号: {phone}, 验证码: {code}")
            
            return jsonify({
                'success': True,
                'message': '验证码已发送（演示模式：请查看控制台输出）',
                'code': code  # 演示模式返回验证码，实际项目中删除此行
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'发送短信验证码失败: {str(e)}'}), 500

    
    @app.route('/api/sms/verify', methods=['POST'])
    def verify_sms_captcha():
        """验证短信验证码"""
        try:
            data = request.get_json()
            phone = data.get('phone', '').strip()
            code = data.get('code', '').strip()
            
            # 验证输入
            if not phone or not code:
                return jsonify({'success': False, 'message': '手机号和验证码不能为空'}), 400
            
            # 检查验证码是否存在
            if phone not in sms_captcha_store:
                return jsonify({'success': False, 'message': '验证码已失效，请重新获取'}), 400
            
            # 检查是否过期
            captcha_data = sms_captcha_store[phone]
            expire_time = datetime.fromisoformat(captcha_data['expire_time'])
            
            if datetime.now() > expire_time:
                del sms_captcha_store[phone]
                return jsonify({'success': False, 'message': '验证码已过期，请重新获取'}), 400
            
            # 检查尝试次数
            if captcha_data['try_count'] >= 3:
                del sms_captcha_store[phone]
                return jsonify({'success': False, 'message': '验证次数过多，请重新获取验证码'}), 400
            
            # 验证验证码
            if captcha_data['code'] != code:
                # 增加尝试次数
                sms_captcha_store[phone]['try_count'] += 1
                return jsonify({'success': False, 'message': '验证码错误'}), 400
            
            # 验证成功，删除验证码
            del sms_captcha_store[phone]
            
            return jsonify({'success': True, 'message': '验证成功'}), 200
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'验证短信验证码失败: {str(e)}'}), 500
