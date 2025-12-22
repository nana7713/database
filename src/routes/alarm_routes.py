from flask import Blueprint, request
from dao.AlarmMaintenanceDao import AlarmMaintenanceDao
from utils.middleware import token_required, roles_required
from utils.response import success_response, error_response
from datetime import datetime

# 创建蓝图
alarm_bp = Blueprint('alarm', __name__, url_prefix='/api/alarm')

# 初始化DAO
alarm_dao = AlarmMaintenanceDao()

# ============ 告警管理 ============
@alarm_bp.route('/', methods=['GET'])
@token_required
def get_all_alarms():
    """获取所有告警信息"""
    try:
        alarms = alarm_dao.query_all_alarms_detailed()
        return success_response(data=alarms)
    except Exception as e:
        return error_response(str(e), 500)

@alarm_bp.route('/', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def create_alarm():
    """录入告警信息"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        # 验证必要字段
        required_fields = ['alarm_id', 'device_id', 'alarm_type', 'occur_time', 'alarm_level', 'alarm_content', 'threshold_value']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        # 转换日期格式
        if isinstance(data['occur_time'], str):
            data['occur_time'] = datetime.fromisoformat(data['occur_time'].replace('Z', '+00:00'))
        
        success = alarm_dao.insert_alarm(data)
        if success:
            return success_response(message="告警信息录入成功", code=201)
        else:
            return error_response("告警信息录入失败", 500)
            
    except Exception as e:
        return error_response(str(e), 500)

@alarm_bp.route('/pending', methods=['GET'])
@token_required
def get_pending_alarms():
    """获取未处理告警列表"""
    try:
        alarms = alarm_dao.query_pending_alarms_detailed()
        return success_response(data=alarms)
    except Exception as e:
        return error_response(str(e), 500)

# ============ 运维工单管理 ============
@alarm_bp.route('/orders', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def create_maintenance_order():
    """生成运维工单"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        # 验证必要字段
        required_fields = ['order_id', 'alarm_id', 'maintainer_id']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        success = alarm_dao.create_maintenance_order(data)
        if success:
            return success_response(message="运维工单生成成功", code=201)
        else:
            return error_response("运维工单生成失败", 500)
            
    except Exception as e:
        return error_response(str(e), 500)

@alarm_bp.route('/orders/maintainer/<maintainer_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def get_orders_by_maintainer(maintainer_id):
    """查询运维人员的工单列表"""
    try:
        orders = alarm_dao.query_orders_by_maintainer(maintainer_id)
        return success_response(data=orders)
    except Exception as e:
        return error_response(str(e), 500)

@alarm_bp.route('/orders/<order_id>', methods=['PUT'])
@roles_required('ADMIN', 'MAINTENANCE')
def complete_maintenance_order(order_id):
    """完成运维工单"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        # 验证必要字段
        if 'result' not in data:
            return error_response("缺少必要字段: result", 400)
        
        result_text = data['result']
        attachment_path = data.get('attachment_path', '')
        
        success = alarm_dao.complete_order(order_id, result_text, attachment_path)
        if success:
            return success_response(message="运维工单完成", code=200)
        else:
            return error_response("运维工单完成失败", 500)
            
    except Exception as e:
        return error_response(str(e), 500)

@alarm_bp.route('/<alarm_id>/handle', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def handle_alarm(alarm_id):
    """处理告警"""
    try:
        success = alarm_dao.handle_alarm(alarm_id)
        if success:
            return success_response(message="告警处理成功")
        else:
            return error_response("告警处理失败", 500)
    except Exception as e:
        return error_response(str(e), 500)

@alarm_bp.route('/cleanup', methods=['DELETE'])
@roles_required('ADMIN')
def cleanup_alarms():
    """清理过期告警数据"""
    try:
        success = alarm_dao.delete_invalid_alarms()
        if success:
            return success_response(message="过期告警数据清理成功", code=200)
        else:
            return error_response("过期告警数据清理失败", 500)
            
    except Exception as e:
        return error_response(str(e), 500)