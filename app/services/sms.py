"""
阿里云短信服务。

变更：不再 vendor SDK 源码（原 api/sdk/ 目录已删除），
改为标准 pip 依赖 aliyun-python-sdk-core / aliyun-python-sdk-dysmsapi。
延迟导入：未安装或未配置时模块仍可正常加载（进入演示模式）。
"""
import json
import os
import random
import string


def _cfg():
    return {
        'access_key_id': os.environ.get('ALIYUN_ACCESS_KEY_ID', ''),
        'access_key_secret': os.environ.get('ALIYUN_ACCESS_KEY_SECRET', ''),
        'sign_name': os.environ.get('ALIYUN_SIGN_NAME', ''),
        'template_code': os.environ.get('ALIYUN_TEMPLATE_CODE', ''),
    }


def is_configured():
    c = _cfg()
    return bool(c['access_key_id'] and c['access_key_secret']
                and c['sign_name'] and c['template_code'])


def generate_sms_code():
    """生成 6 位随机数字验证码。"""
    return ''.join(random.choices(string.digits, k=6))


def send_aliyun_sms(phone, code):
    """真实发送短信，返回 (ok, message)。"""
    c = _cfg()
    if not (c['access_key_id'] and c['access_key_secret']):
        return False, 'AccessKey 未配置'
    if not c['sign_name']:
        return False, '短信签名未配置'
    if not c['template_code']:
        return False, '短信模板未配置'

    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

        client = AcsClient(c['access_key_id'], c['access_key_secret'], 'cn-hangzhou')
        req = SendSmsRequest()
        req.set_PhoneNumbers(phone)
        req.set_SignName(c['sign_name'])
        req.set_TemplateCode(c['template_code'])
        req.set_TemplateParam(json.dumps({'code': code, 'min': '5'}))

        resp = client.do_action_with_exception(req)
        result = json.loads(resp.decode('utf-8') if isinstance(resp, bytes) else resp)
        if result.get('Code') == 'OK':
            return True, '发送成功'
        return False, f"阿里云返回错误 [{result.get('Code')}]: {result.get('Message', '未知错误')}"
    except ImportError:
        return False, '阿里云 SDK 未安装（pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi）'
    except Exception as e:
        return False, f'{e}'
