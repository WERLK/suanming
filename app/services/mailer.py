"""
邮件服务（密码重置等）。

配置优先级：环境变量 > api/mail_config.json（兼容历史部署） > 演示模式。
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_mail_config():
    config = {
        'smtp_server': os.environ.get('SMTP_SERVER', ''),
        'smtp_port': int(os.environ.get('SMTP_PORT', '0') or '0'),
        'sender_email': os.environ.get('SMTP_EMAIL', ''),
        'sender_password': os.environ.get('SMTP_PASSWORD', ''),
    }
    if config['smtp_server'] and config['sender_email'] and config['sender_password']:
        if not config['smtp_port']:
            config['smtp_port'] = 587
        return config

    # 兼容历史配置文件（生产服务器在用）
    mail_config_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'api', 'mail_config.json')
    if os.path.exists(mail_config_file):
        try:
            import json
            with open(mail_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            server = data.get('smtp_server', '')
            email = data.get('sender_email', '')
            pwd = data.get('sender_password', '')
            port = int(data.get('smtp_port', '587'))
            if server and email and pwd and 'YOUR_' not in pwd:
                return {'smtp_server': server, 'smtp_port': port,
                        'sender_email': email, 'sender_password': pwd}
        except Exception:
            pass
    return None


def send_email(to_email, subject, body):
    """发送邮件（自动根据配置选择真实发送或演示模式）。"""
    cfg = get_mail_config()
    if cfg is None:
        print(f"【演示模式】未配置 SMTP，邮件内容:\n  收件人: {to_email}\n  主题: {subject}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = cfg['sender_email']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        server = smtplib.SMTP(cfg['smtp_server'], cfg['smtp_port'])
        server.starttls()
        server.login(cfg['sender_email'], cfg['sender_password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False
