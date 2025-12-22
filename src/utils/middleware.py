from flask import request, jsonify, g
from functools import wraps
from utils.security import SecurityUtils

def token_required(f):
    """JWT token验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # 从cookie获取token
        if not token:
            token = request.cookies.get('access_token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': '请先登录',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        # 验证token
        payload = SecurityUtils.verify_jwt_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': 'token无效或已过期',
                'error_code': 'TOKEN_INVALID'
            }), 401
        
        # 将用户信息存入g对象（类似Spring的ThreadLocal）
        g.current_user = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'roles': payload.get('roles', [])
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def roles_required(*required_roles):
    """角色权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            current_user = g.get('current_user', {})
            user_roles = current_user.get('roles', [])
            
            # 检查是否有任一所需角色
            if not any(role in user_roles for role in required_roles):
                return jsonify({
                    'success': False,
                    'message': '权限不足',
                    'error_code': 'PERMISSION_DENIED'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=5, window=60):
    """简单的限流装饰器（防止暴力破解）"""
    from collections import defaultdict
    import time
    
    requests = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 使用IP地址作为标识
            ip = request.remote_addr
            endpoint = request.endpoint
            
            key = f"{ip}:{endpoint}"
            current_time = time.time()
            
            # 清理过期的请求记录
            requests[key] = [
                req_time for req_time in requests[key]
                if current_time - req_time < window
            ]
            
            # 检查是否超过限制
            if len(requests[key]) >= max_requests:
                return jsonify({
                    'success': False,
                    'message': '请求过于频繁，请稍后再试',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': window
                }), 429
            
            # 记录本次请求
            requests[key].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator