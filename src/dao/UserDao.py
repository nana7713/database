from models.user import User
from models.role import UserRole, Role
from base import db_manager
from utils.security import SecurityUtils
from datetime import datetime, timedelta
from sqlalchemy import or_
from config import Config

class UserDao:
    """增强的用户数据访问对象"""
    
    # 登录尝试记录（简易内存存储，生产环境用Redis）
    _login_attempts = {}
    
    @staticmethod
    def select_all():
        """获取所有用户（不返回密码）"""
        with db_manager.get_session() as session:
            users = session.query(User).all()
            return [UserDao._user_to_dict(user) for user in users]
    
    @staticmethod
    def select_by_user_id(user_id: str):
        """根据用户ID查询"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                return UserDao._user_to_dict(user)
            return None
    
    @staticmethod
    def select_by_username(username: str):
        """根据用户名查询"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                return UserDao._user_to_dict(user)
            return None
    
    @staticmethod
    def select_by_email(email: str):
        """根据邮箱查询"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.email == email).first()
            if user:
                return UserDao._user_to_dict(user)
            return None
    
    @staticmethod
    def get_user_with_credentials(username: str):
        """获取用户及其凭证（包含密码）"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(
                or_(
                    User.username == username,
                    User.email == username,
                    User.phone == username
                )
            ).first()
            return user  # 返回完整的用户对象（包含密码）
    
    @staticmethod
    def get_user_roles(user_id: str):
        """获取用户角色列表"""
        with db_manager.get_session() as session:
            roles = session.query(Role).join(
                UserRole, Role.role_id == UserRole.role_id
            ).filter(UserRole.user_id == user_id).all()
            
            return [role.role_code for role in roles]
    
    @staticmethod
    def insert(user_data: dict):
        """创建新用户 - 使用SHA-256加密"""
        with db_manager.get_session() as session:
            # 使用SHA-256加密密码（符合任务书要求）
            if 'password' in user_data:
                password = user_data.pop('password')
                # 使用配置的算法加密
                hashed_password = SecurityUtils.hash_password(
                    password, 
                    algorithm=Config.PASSWORD_HASH_ALGORITHM
                )
                user_data['password_hash'] = hashed_password
            
            user = User(**user_data)
            session.add(user)
            session.flush()
            
            # 为新用户分配默认角色（USER）
            default_role = session.query(Role).filter(
                Role.role_code == 'USER'
            ).first()
            
            if default_role:
                user_role = UserRole(
                    user_id=user.user_id,
                    role_id=default_role.role_id
                )
                session.add(user_role)
            
            return UserDao._user_to_dict(user)
    
    @staticmethod
    def verify_login(username: str, password: str) -> tuple:
        """
        验证登录
        返回: (是否成功, 用户信息或错误消息)
        """
        with db_manager.get_session() as session:
            # 先查询用户
            user = session.query(User).filter(
                or_(
                    User.username == username,
                    User.email == username,
                    User.phone == username
                )
            ).first()
            
            if not user:
                return False, "用户名或密码错误"
            
            # 验证密码
            if not SecurityUtils.verify_password(password, user.password_hash):
                return False, "用户名或密码错误"
            
            # 登录成功，返回用户信息
            return True, UserDao._user_to_dict(user)
    
    @staticmethod
    def update(user_id: str, update_data: dict):
        """更新用户信息"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None
            
            # 如果更新密码，需要加密
            if 'password' in update_data:
                update_data['password_hash'] = SecurityUtils.hash_password(
                    update_data.pop('password')
                )
            
            # 清理输入
            for key in update_data:
                if hasattr(user, key) and key not in ['user_id', 'created_at']:
                    if isinstance(update_data[key], str):
                        update_data[key] = SecurityUtils.sanitize_input(update_data[key])
                    setattr(user, key, update_data[key])
            
            return UserDao._user_to_dict(user)
    
    @staticmethod
    def delete_by_user_id(user_id: str):
        """删除用户"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                session.delete(user)
                return True
            return False
    
    @staticmethod
    def check_login_attempts(username: str, max_attempts=5, lockout_minutes=15):
        """检查登录尝试次数"""
        key = f"login_attempts:{username}"
        
        if key in UserDao._login_attempts:
            attempts, lockout_time = UserDao._login_attempts[key]
            
            # 检查是否在锁定时间内
            if lockout_time and datetime.utcnow() < lockout_time:
                remaining = (lockout_time - datetime.utcnow()).seconds // 60
                return False, f"账号已锁定，请{remaining}分钟后再试"
            
            # 检查尝试次数
            if attempts >= max_attempts:
                # 锁定账号
                lockout_time = datetime.utcnow() + timedelta(minutes=lockout_minutes)
                UserDao._login_attempts[key] = (attempts, lockout_time)
                return False, f"登录失败次数过多，账号已锁定{lockout_minutes}分钟"
        
        return True, ""
    
    @staticmethod
    def record_login_attempt(username: str, success: bool):
        """记录登录尝试"""
        key = f"login_attempts:{username}"
        
        if success:
            # 登录成功，清除记录
            if key in UserDao._login_attempts:
                del UserDao._login_attempts[key]
        else:
            # 登录失败，增加计数
            if key in UserDao._login_attempts:
                attempts, lockout_time = UserDao._login_attempts[key]
                UserDao._login_attempts[key] = (attempts + 1, lockout_time)
            else:
                UserDao._login_attempts[key] = (1, None)
    
    @staticmethod
    def _user_to_dict(user: User):
        """将User对象转换为字典"""
        return {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
            'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
        }