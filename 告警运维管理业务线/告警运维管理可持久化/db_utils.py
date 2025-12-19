import pymysql
from datetime import datetime

# 数据库配置信息 - 请根据你本地 MySQL 修改
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'db': 'smart_energy_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # 返回字典格式，方便前端使用
}

def get_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接失败: {e}")
        return None