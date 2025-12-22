# utils/security.py - 增强版，支持SHA-256和MD5
import hashlib
import hmac
import secrets
import re
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import Config

class SecurityUtils:
    """安全工具类 - 兼容你的表结构"""
    
    @staticmethod
    def hash_password(password: str, algorithm='sha256') -> str:
        """
        哈希密码
        algorithm: 'sha256' 或 'md5'（符合任务书要求）
        返回: 哈希值:盐值 的格式
        """
        # 生成随机盐
        salt = secrets.token_hex(16)
        
        if algorithm.lower() == 'sha256':
            # SHA-256 哈希
            hash_obj = hashlib.sha256()
            hash_obj.update(salt.encode('utf-8'))
            hash_obj.update(password.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
        elif algorithm.lower() == 'md5':
            # MD5 哈希
            hash_obj = hashlib.md5()
            hash_obj.update(salt.encode('utf-8'))
            hash_obj.update(password.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
        else:
            raise ValueError(f"不支持的加密算法: {algorithm}")
        
        # 存储格式: 哈希值:盐值:算法
        return f"{password_hash}:{salt}:{algorithm}"
    
    @staticmethod
    def verify_password(plain_password: str, stored_hash_str: str) -> bool:
        """
        验证密码
        stored_hash_str 格式: 哈希值:盐值:算法
        """
        if not stored_hash_str or ':' not in stored_hash_str:
            return False
        
        try:
            # 解析存储的哈希字符串
            parts = stored_hash_str.split(':')
            if len(parts) == 3:
                stored_hash, salt, algorithm = parts
            elif len(parts) == 2:
                # 兼容旧格式（哈希:盐）
                stored_hash, salt = parts
                algorithm = 'sha256'  # 默认算法
            else:
                return False
            
            if algorithm.lower() == 'sha256':
                hash_obj = hashlib.sha256()
                hash_obj.update(salt.encode('utf-8'))
                hash_obj.update(plain_password.encode('utf-8'))
                computed_hash = hash_obj.hexdigest()
            elif algorithm.lower() == 'md5':
                hash_obj = hashlib.md5()
                hash_obj.update(salt.encode('utf-8'))
                hash_obj.update(plain_password.encode('utf-8'))
                computed_hash = hash_obj.hexdigest()
            else:
                return False
            
            # 使用恒定时间比较防止时序攻击
            return hmac.compare_digest(computed_hash, stored_hash)
            
        except Exception:
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """验证密码强度"""
        if len(password) < 8:
            return False, "密码长度至少8位"
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含大写字母"
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含小写字母"
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码必须包含特殊字符"
        return True, "密码强度合格"
    
    @staticmethod
    def generate_jwt_token(user_id: str, username: str, roles: list) -> str:
        """生成JWT token - 30分钟过期（符合任务书要求）"""
        payload = {
            'user_id': user_id,
            'username': username,
            'roles': roles,
            'exp': datetime.utcnow() + timedelta(minutes=30),  # 30分钟
            'iat': datetime.utcnow(),
            'jti': secrets.token_hex(16)  # JWT ID，防止重放攻击
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            payload = jwt.decode(
                token, 
                Config.JWT_SECRET_KEY, 
                algorithms=['HS256'],
                options={'verify_exp': True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None  # token过期
        except jwt.InvalidTokenError:
            return None  # token无效