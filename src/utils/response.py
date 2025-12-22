from flask import jsonify
from datetime import datetime
# 响应工具函数
def success_response(data=None, message="操作成功", status_code=200):
    """成功响应"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }), status_code

def error_response(message="操作失败", status_code=400, error_code=None):
    """错误响应"""
    return jsonify({
        'success': False,
        'message': message,
        'error_code': error_code,
        'timestamp': datetime.now().isoformat()
    }), status_code
