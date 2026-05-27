# PythonAnywhere WSGI 配置
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 Flask 应用  
from api.app import app as application

# PythonAnywhere 使用 application 变量名
application = application
