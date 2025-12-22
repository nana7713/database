# config.py - 添加安全配置
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or '智慧能源管理系统密钥-2024'
    
    # JWT配置 - 会话超时30分钟（符合任务书要求）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  # 30分钟会话超时
    
    # 安全配置 - 符合任务书要求
    PASSWORD_HASH_ALGORITHM = 'sha256'  # 使用SHA-256
    MAX_LOGIN_ATTEMPTS = 5              # 最大登录尝试次数
    LOCKOUT_TIME_MINUTES = 30           # 锁定时间30分钟
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123123@localhost/smart_energy_db'