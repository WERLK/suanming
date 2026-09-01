"""
配置模块 — 集中管理所有环境相关配置。

原则：
- 所有敏感信息一律来自环境变量，不再提供硬编码回退值；
- 生产环境（PRODUCTION=1 或 FLASK_ENV=production）启动时强校验必填项，
  缺失即拒绝启动（fail-fast），避免带默认密钥上线。
"""
import os


class BaseConfig:
    """通用配置"""

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    # 支持环境变量覆盖：便于把数据目录指向持久化磁盘（如 Docker volume、独立数据盘）
    DATA_DIR = os.environ.get('DATA_DIR', os.path.join(PROJECT_ROOT, 'data'))

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET', '')
    JSON_AS_ASCII = False

    # JWT
    JWT_EXPIRE_DAYS = int(os.environ.get('JWT_EXPIRATION_DELTA', '7') or '7')

    # 数据文件（JSON 存储层，后续可平滑切换 SQLite/MySQL）
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    TOKENS_FILE = os.path.join(DATA_DIR, 'tokens.json')
    CAPTCHA_FILE = os.path.join(DATA_DIR, 'captcha_store.json')
    OAUTH_STATE_FILE = os.path.join(DATA_DIR, 'oauth_states.json')
    ANALYTICS_DB = os.path.join(DATA_DIR, 'analytics.db')

    # 验证码
    CAPTCHA_TTL_MINUTES = 5
    SMS_CODE_TTL_MINUTES = 5

    # 各业务数据文件（历史遗留 JSON 存储，路径保持不变以兼容存量数据）
    FAVORITES_FILE = os.path.join(DATA_DIR, 'favorites.json')
    DIVINATION_FILE = os.path.join(DATA_DIR, 'divination_history.json')
    NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')
    DATASETS_FILE = os.path.join(DATA_DIR, 'datasets.json')

    # 上传目录
    AVATAR_SAVE_DIR = os.path.join(PROJECT_ROOT, 'static', 'avatars')
    IDCARD_SAVE_DIR = os.path.join(PROJECT_ROOT, 'static', 'idcard')

    # 下载代理缓存
    DOWNLOADS_DIR = os.environ.get('DOWNLOADS_DIR', os.path.join(PROJECT_ROOT, 'downloads'))
    DOWNLOAD_CACHE_TTL = 24 * 3600

    # 限流
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per minute')
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    # 管理端（analytics API 鉴权）
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')

    # 外部 API
    HOROSCOPE_API_BASE = os.environ.get('HOROSCOPE_API_BASE', 'https://web.juhe.cn')
    HOROSCOPE_API_KEY = os.environ.get('HOROSCOPE_API_KEY', '')
    TAROT_API_BASE = os.environ.get('TAROT_API_BASE', 'https://api.vvhan.com')

    # 阿里云短信
    ALIYUN_ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID', '')
    ALIYUN_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET', '')
    ALIYUN_SIGN_NAME = os.environ.get('ALIYUN_SIGN_NAME', '')
    ALIYUN_TEMPLATE_CODE = os.environ.get('ALIYUN_TEMPLATE_CODE', '')

    # SMTP
    SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587') or '587')
    SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

    # OAuth（github / wechat / qq）
    OAUTH_GITHUB_CLIENT_ID = os.environ.get('OAUTH_GITHUB_CLIENT_ID', '')
    OAUTH_GITHUB_CLIENT_SECRET = os.environ.get('OAUTH_GITHUB_CLIENT_SECRET', '')
    OAUTH_WECHAT_APPID = os.environ.get('OAUTH_WECHAT_APPID', '')
    OAUTH_WECHAT_SECRET = os.environ.get('OAUTH_WECHAT_SECRET', '')
    OAUTH_QQ_APPID = os.environ.get('OAUTH_QQ_APPID', '')
    OAUTH_QQ_SECRET = os.environ.get('OAUTH_QQ_SECRET', '')

    @classmethod
    def ensure_dirs(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)


class DevConfig(BaseConfig):
    DEBUG = True
    # 开发环境允许回落到本地默认密钥（仅本机调试用）
    SECRET_KEY = BaseConfig.SECRET_KEY or 'dev-only-secret-key'


class ProductionConfig(BaseConfig):
    DEBUG = False

    @classmethod
    def validate(cls):
        """生产环境 fail-fast 校验。"""
        problems = []
        if not BaseConfig.SECRET_KEY:
            problems.append(
                'SECRET_KEY 未设置。生产环境必须通过环境变量提供，'
                '（历史版本存在硬编码回退密钥，已移除）'
            )
        if problems:
            raise RuntimeError('配置校验失败:\n  - ' + '\n  - '.join(problems))


class TestConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = BaseConfig.SECRET_KEY or 'test-secret-key'
    # 测试时使用临时目录，避免污染真实数据
    DATA_DIR = os.path.join(BaseConfig.PROJECT_ROOT, 'data_test')


def get_config():
    """根据环境变量选择配置类。"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production' or os.environ.get('PRODUCTION'):
        return ProductionConfig
    if env == 'testing':
        return TestConfig
    return DevConfig


# ---------- 模块级便捷导出（路径类常量，供蓝图直接 import） ----------
# 这些路径与环境无关（均相对项目根），故安全地在模块级展开。
AVATAR_SAVE_DIR = BaseConfig.AVATAR_SAVE_DIR
IDCARD_SAVE_DIR = BaseConfig.IDCARD_SAVE_DIR
DATA_DIR = BaseConfig.DATA_DIR
FAVORITES_FILE = BaseConfig.FAVORITES_FILE
DIVINATION_FILE = BaseConfig.DIVINATION_FILE
NOTIFICATIONS_FILE = BaseConfig.NOTIFICATIONS_FILE
DATASETS_FILE = BaseConfig.DATASETS_FILE
PROJECT_ROOT = BaseConfig.PROJECT_ROOT
USERS_FILE = BaseConfig.USERS_FILE
TOKENS_FILE = BaseConfig.TOKENS_FILE

# 确保数据目录存在（首次 clone / 新环境部署时 data/ 不在版本库内，
# 蓝图模块导入阶段会直接创建数据文件，父目录缺失会导致启动崩溃）
os.makedirs(DATA_DIR, exist_ok=True)
