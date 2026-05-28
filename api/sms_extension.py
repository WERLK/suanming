"""
短信验证码扩展模块 - 阿里云短信服务
SDK 已内置于 api/sdk/ 目录，无需 pip 安装
"""
import os
import sys

# Add local SDK to path
_sdk_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sdk')
if _sdk_dir not in sys.path:
    sys.path.insert(0, _sdk_dir)

import re
import json
import string
import random
from datetime import datetime, timedelta

# 阿里云短信配置
ALIYUN_ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID', '')
ALIYUN_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET', '')
ALIYUN_SIGN_NAME = os.environ.get('ALIYUN_SIGN_NAME', '速通互联验证码')
ALIYUN_TEMPLATE_CODE = os.environ.get('ALIYUN_TEMPLATE_CODE', '100001')


def send_aliyun_sms(phone, code):
    """发送阿里云短信 - 真实发送"""
    if not ALIYUN_ACCESS_KEY_ID or not ALIYUN_ACCESS_KEY_SECRET:
        return False, 'AccessKey 未配置'
    if not ALIYUN_SIGN_NAME:
        return False, '短信签名未配置'
    if not ALIYUN_TEMPLATE_CODE:
        return False, '短信模板未配置'

    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

        # 初始化客户端
        acs_client = AcsClient(
            ALIYUN_ACCESS_KEY_ID,
            ALIYUN_ACCESS_KEY_SECRET,
            'cn-hangzhou'
        )

        # 构建请求（模板有两个变量: ${code} 和 ${min}）
        req = SendSmsRequest()
        req.set_PhoneNumbers(phone)
        req.set_SignName(ALIYUN_SIGN_NAME)
        req.set_TemplateCode(ALIYUN_TEMPLATE_CODE)
        req.set_TemplateParam(json.dumps({'code': code, 'min': '5'}))

        # 发送
        resp = acs_client.do_action_with_exception(req)
        result = json.loads(resp.decode('utf-8') if isinstance(resp, bytes) else resp)

        if result.get('Code') == 'OK':
            return True, '发送成功'
        else:
            return False, f"阿里云返回错误 [{result.get('Code')}]: {result.get('Message', '未知错误')}"

    except Exception as e:
        return False, f'{e}'


def generate_sms_code():
    """生成6位随机数字验证码"""
    return ''.join(random.choices(string.digits, k=6))
