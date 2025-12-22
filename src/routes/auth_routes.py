from flask import Blueprint, request, g, make_response
from datetime import datetime, timedelta
from dao.UserDao import UserDao
from utils.security import SecurityUtils
from utils.middleware import token_required, roles_required, rate_limit
import uuid
import re
from base import db_manager
from sqlalchemy import or_
from models.user import User
from config import Config
from utils.response import error_response,success_response
_login_attempts = {} 
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@rate_limit(max_requests=3, window=60)  # 60秒内最多3次注册
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        # 验证必要字段
        required_fields = ['username', 'password', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return error_response(f"{field}字段不能为空")
        
        username = data['username'].strip()
        password = data['password']
        email = data['email'].strip()
        
        # 验证用户名格式（字母开头，4-20位）
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{3,19}$', username):
            return error_response("用户名必须以字母开头，4-20位字母数字下划线")
        
        # 验证邮箱格式
        if not SecurityUtils.validate_email(email):
            return error_response("邮箱格式不正确")
        
        # 验证密码强度
        password_valid, password_msg = SecurityUtils.validate_password(password)
        if not password_valid:
            return error_response(password_msg)
        
        # 检查用户名是否已存在
        if UserDao.select_by_username(username):
            return error_response("用户名已存在", error_code='USERNAME_EXISTS')
        
        # 检查邮箱是否已存在
        if UserDao.select_by_email(email):
            return error_response("邮箱已注册", error_code='EMAIL_EXISTS')
        
        # 生成用户ID（可根据需要调整规则）
        user_id = f"U{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # 创建用户数据
        user_data = {
            'user_id': user_id,
            'username': username,
            'password': password,  # 会在DAO层加密
            'email': email,
            'full_name': data.get('full_name', ''),
            'phone': data.get('phone', '')
        }
        
        # 创建用户
        new_user = UserDao.insert(user_data)
        
        return success_response(
            data=new_user,
            message="注册成功",
            status_code=201
        )
        
    except Exception as e:
        return error_response(f"注册失败: {str(e)}", status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录 - 实现5次失败锁定和30分钟会话"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return error_response("用户名和密码不能为空")
        
        # 获取客户端IP
        ip_address = request.remote_addr
        attempt_key = f"{username}_{ip_address}"
        current_time = datetime.now()
        
        # ========== 1. 检查登录尝试次数（5次限制）==========
        if attempt_key in _login_attempts:
            attempts, lock_until = _login_attempts[attempt_key]
            
            # 检查是否在锁定时间内
            if lock_until and current_time < lock_until:
                remaining_minutes = max(1, int((lock_until - current_time).total_seconds() / 60))
                return error_response(
                    f"账号已锁定，请{remaining_minutes}分钟后再试", 
                    status_code=429,
                    error_code='ACCOUNT_LOCKED'
                )
            
            # 检查尝试次数是否超过5次
            if attempts >= Config.MAX_LOGIN_ATTEMPTS:
                # 锁定30分钟
                lock_until = current_time + timedelta(minutes=Config.LOCKOUT_TIME_MINUTES)
                _login_attempts[attempt_key] = (attempts, lock_until)
                return error_response(
                    f"登录失败次数过多，账号已锁定{Config.LOCKOUT_TIME_MINUTES}分钟",
                    status_code=429,
                    error_code='MAX_ATTEMPTS_EXCEEDED'
                )
        
        # ========== 2. 验证用户名和密码 ==========
        # 使用新的验证方法
        from dao.UserDao import UserDao
        success, result = UserDao.verify_login(username, password)
        
        if not success:
            # 记录失败尝试
            if attempt_key in _login_attempts:
                attempts, lock_until = _login_attempts[attempt_key]
                _login_attempts[attempt_key] = (attempts + 1, lock_until)
            else:
                _login_attempts[attempt_key] = (1, None)
            
            return error_response(
                result, 
                error_code='INVALID_CREDENTIALS'
            )
        
        # ========== 3. 登录成功 ==========
        # 清除尝试记录
        if attempt_key in _login_attempts:
            del _login_attempts[attempt_key]
        
        # 获取用户信息和角色
        user_info = result
        roles = UserDao.get_user_roles(user_info['user_id'])
        
        # ========== 4. 生成JWT token（30分钟过期）==========
        token = SecurityUtils.generate_jwt_token(
            user_id=user_info['user_id'],
            username=user_info['username'],
            roles=roles
        )
        
        # ========== 5. 构建响应数据 ==========
        user_info['roles'] = roles
        response_data = {
            'user': user_info,
            'token': token,
            'expires_in': 1800,  # 30分钟 = 1800秒（符合任务书要求）
            'token_type': 'Bearer'
        }
        
        response = make_response(success_response(
            data=response_data,
            message="登录成功"
        ))
        
        
        return response
        
    except Exception as e:
        # 记录错误日志
        import traceback
        print(f"登录异常: {str(e)}")
        print(traceback.format_exc())
        
        return error_response(
            f"登录失败: {str(e)}", 
            status_code=500,
            error_code='SERVER_ERROR'
        )

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """用户登出"""
    try:
        response = make_response(success_response(message="登出成功"))
        
        # 清除token cookie
        response.set_cookie('access_token', '', expires=0)
        
        return response
    except Exception as e:
        return error_response(f"登出失败: {str(e)}", status_code=500)

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """获取当前用户信息"""
    try:
        current_user = g.current_user
        user_id = current_user['user_id']
        
        user = UserDao.select_by_user_id(user_id)
        if not user:
            return error_response("用户不存在", status_code=404)
        
        # 获取角色信息
        roles = UserDao.get_user_roles(user_id)
        user['roles'] = roles
        
        return success_response(data=user, message="获取个人信息成功")
        
    except Exception as e:
        return error_response(f"获取信息失败: {str(e)}", status_code=500)

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """更新用户信息"""
    try:
        current_user = g.current_user
        user_id = current_user['user_id']
        
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        # 不允许修改的字段
        protected_fields = ['user_id', 'username', 'password']
        for field in protected_fields:
            if field in data:
                return error_response(f"不允许修改{field}")
        
        # 如果修改邮箱，需要验证格式
        if 'email' in data and data['email']:
            if not SecurityUtils.validate_email(data['email']):
                return error_response("邮箱格式不正确")
        
        # 如果修改手机号，需要验证格式
        if 'phone' in data and data['phone']:
            if not SecurityUtils.validate_phone(data['phone']):
                return error_response("手机号格式不正确")
        
        # 更新用户信息
        updated_user = UserDao.update(user_id, data)
        if not updated_user:
            return error_response("用户不存在", status_code=404)
        
        return success_response(data=updated_user, message="更新成功")
        
    except Exception as e:
        return error_response(f"更新失败: {str(e)}", status_code=500)

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """修改密码"""
    try:
        current_user = g.current_user
        user_id = current_user['user_id']
        
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        required_fields = ['old_password', 'new_password']
        for field in required_fields:
            if field not in data or not data[field]:
                return error_response(f"{field}字段不能为空")
        
        old_password = data['old_password']
        new_password = data['new_password']
        
        # 获取用户验证旧密码
        user = UserDao.get_user_with_credentials(current_user['username'])
        if not user:
            return error_response("用户不存在", status_code=404)
        
        if not SecurityUtils.verify_password(old_password, user.password_hash):
            return error_response("原密码错误", error_code='OLD_PASSWORD_INCORRECT')
        
        # 验证新密码强度
        password_valid, password_msg = SecurityUtils.validate_password(new_password)
        if not password_valid:
            return error_response(password_msg)
        
        # 更新密码
        update_data = {'password': new_password}
        updated_user = UserDao.update(user_id, update_data)
        
        return success_response(message="密码修改成功")
        
    except Exception as e:
        return error_response(f"修改密码失败: {str(e)}", status_code=500)

@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """刷新token"""
    try:
        # 从cookie获取旧token
        old_token = request.cookies.get('access_token')
        if not old_token:
            return error_response("token不存在", status_code=401)
        
        # 验证旧token
        payload = SecurityUtils.verify_jwt_token(old_token)
        if not payload:
            return error_response("token无效或已过期", status_code=401)
        
        # 生成新token
        new_token = SecurityUtils.generate_jwt_token(
            user_id=payload['user_id'],
            username=payload['username'],
            roles=payload.get('roles', [])
        )
        
        response_data = {
            'token': new_token,
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        
        response = make_response(success_response(
            data=response_data,
            message="token刷新成功"
        ))
        
        # 设置新的cookie
        response.set_cookie(
            'access_token',
            new_token,
            httponly=True,
            secure=False,
            samesite='Strict',
            max_age=3600
        )
        
        return response
        
    except Exception as e:
        return error_response(f"刷新token失败: {str(e)}", status_code=500)

@auth_bp.route('/check-username/<username>', methods=['GET'])
def check_username(username):
    """检查用户名是否可用"""
    try:
        exists = UserDao.select_by_username(username) is not None
        return success_response(data={'available': not exists})
    except Exception as e:
        return error_response(f"检查失败: {str(e)}")

@auth_bp.route('/check-email/<email>', methods=['GET'])
def check_email(email):
    """检查邮箱是否可用"""
    try:
        exists = UserDao.select_by_email(email) is not None
        return success_response(data={'available': not exists})
    except Exception as e:
        return error_response(f"检查失败: {str(e)}")

# 管理员接口（需要管理员权限）
@auth_bp.route('/users', methods=['GET'])
@token_required
@roles_required('ADMIN', 'SYSTEM_ADMIN')
def get_all_users():
    """获取所有用户列表（管理员权限）"""
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        
        # 这里可以实现分页查询
        users = UserDao.select_all()
        
        return success_response(data={
            'users': users,
            'total': len(users),
            'page': page,
            'size': size
        })
    except Exception as e:
        return error_response(f"获取用户列表失败: {str(e)}", status_code=500)

# 测试接口
@auth_bp.route('/test-protected', methods=['GET'])
@token_required
def test_protected():
    """测试受保护接口"""
    return success_response(
        data={
            'message': '这是一个受保护的接口',
            'current_user': g.current_user
        }
    )

@auth_bp.route('/test-admin', methods=['GET'])
@token_required
@roles_required('ADMIN')
def test_admin():
    """测试管理员接口"""
    return success_response(data={'message': '这是一个管理员接口'})
