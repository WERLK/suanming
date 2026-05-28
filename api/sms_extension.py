"""
短信验证码扩展模块 - 阿里云短信服务
"""
import os
import re
import json
import string
import random
from datetime import datetime, timedelta

# 阿里云短信配置（从环境变量读取）
ALIYUN_ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID', '')
ALIYUN_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET', '')
ALIYUN_SIGN_NAME = os.environ.get('ALIYUN_SIGN_NAME', '')
ALIYUN_TEMPLATE_CODE = os.environ.get('ALIYUN_TEMPLATE_CODE', '')


def send_aliyun_sms(phone, code):
    """发送阿里云短信 - 真实发送，失败时返回详细错误信息"""
    # 验证配置
    if not ALIYUN_ACCESS_KEY_ID or not ALIYUN_ACCESS_KEY_SECRET:
        return False, 'AccessKey 未配置，请在环境变量中设置 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET'
    if not ALIYUN_SIGN_NAME:
        return False, '短信签名未配置，请在环境变量中设置 ALIYUN_SIGN_NAME'
    if not ALIYUN_TEMPLATE_CODE:
        return False, '短信模板未配置，请在环境变量中设置 ALIYUN_TEMPLATE_CODE'
    
    # 尝试导入阿里云 SDK
    try:
        from aliyunsdk.core.client import AcsClient
        from aliyunsdk.dysmsapi.request.v20170525 import SendSmsRequest
    except ImportError as e:
        return False, f'阿里云SDK未安装: {e}。请运行: pip3 install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi'
    
    try:
        # 初始化客户端（使用 cn-hangzhou region）
        acs_client = AcsClient(
            ALIYUN_ACCESS_KEY_ID,
            ALIYUN_ACCESS_KEY_SECRET,
            'cn-hangzhou'
        )
        
        # 构建请求
        request = SendSmsRequest()
        request.set_accept_format('json')
        request.set_PhoneNumbers(phone)
        request.set_SignName(ALIYUN_SIGN_NAME)
        request.set_TemplateCode(ALIYUN_TEMPLATE_CODE)
        request.set_TemplateParam(json.dumps({'code': code}))
        
        # 发送
        response = acs_client.do_action_with_exception(request)
        result = json.loads(response.decode('utf-8') if isinstance(response, bytes) else response)
        
        if result.get('Code') == 'OK':
            return True, '发送成功'
        else:
            error_msg = result.get('Message', '发送失败')
            error_code = result.get('Code', 'Unknown')
            return False, f'阿里云返回错误 [{error_code}]: {error_msg}'
            
    except Exception as e:
        return False, f'发送异常: {str(e)}'


def generate_sms_code():
    """生成6位随机数字验证码"""
    return ''.join(random.choices(string.digits, k=6))
