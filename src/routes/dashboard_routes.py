from flask import Blueprint, request
from dao.DashboardDAO import DashboardConfigDAO, RealtimeSummaryDAO, HistoricalTrendDAO
from utils.middleware import token_required, roles_required
from utils.response import success_response, error_response
from datetime import date, datetime

# 创建蓝图
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# 初始化DAO
dashboard_config_dao = DashboardConfigDAO()
realtime_summary_dao = RealtimeSummaryDAO()
historical_trend_dao = HistoricalTrendDAO()

# ============ 大屏配置管理 ============
@dashboard_bp.route('/configs', methods=['POST'])
@roles_required('ADMIN', 'MANAGER')
def create_dashboard_config():
    """新增大屏展示配置"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        # 验证必要字段
        required_fields = ['display_module', 'config_content', 'permission_level']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        config = dashboard_config_dao.insert_config(data)
        return success_response(data={"config_id": config.config_id}, message="配置创建成功", code=201)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/configs', methods=['GET'])
@token_required
def get_dashboard_configs():
    """获取大屏展示配置列表"""
    try:
        # 获取查询参数
        module = request.args.get('module')
        permission = request.args.get('permission')
        
        if module:
            configs = dashboard_config_dao.get_configs_by_module(module)
        elif permission:
            configs = dashboard_config_dao.get_configs_by_permission(permission)
        else:
            configs = dashboard_config_dao.get_all_configs()
        
        # 转换为字典列表
        config_list = [{
            "config_id": config.config_id,
            "display_module": config.display_module,
            "config_content": config.config_content,
            "permission_level": config.permission_level,
            "update_time": config.update_time.isoformat() if config.update_time else None
        } for config in configs]
        
        return success_response(data=config_list)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/configs/<int:config_id>', methods=['GET'])
@token_required
def get_dashboard_config(config_id):
    """获取单个大屏展示配置"""
    try:
        config = dashboard_config_dao.get_config_by_id(config_id)
        if not config:
            return error_response("配置不存在", 404)
        
        result = {
            "config_id": config.config_id,
            "display_module": config.display_module,
            "config_content": config.config_content,
            "permission_level": config.permission_level,
            "update_time": config.update_time.isoformat() if config.update_time else None
        }
        
        return success_response(data=result)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/configs/<int:config_id>', methods=['PUT'])
@roles_required('ADMIN', 'MANAGER')
def update_dashboard_config(config_id):
    """更新大屏展示配置"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        config = dashboard_config_dao.update_config(config_id, data)
        if not config:
            return error_response("配置不存在", 404)
        
        return success_response(message="配置更新成功")
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_dashboard_config(config_id):
    """删除大屏展示配置"""
    try:
        success = dashboard_config_dao.delete_config(config_id)
        if not success:
            return error_response("配置不存在", 404)
        
        return success_response(message="配置删除成功")
        
    except Exception as e:
        return error_response(str(e), 500)

# ============ 实时汇总数据 ============
@dashboard_bp.route('/summary', methods=['GET'])
@token_required
def get_dashboard_summary():
    """获取仪表板统计数据"""
    try:
        summary = realtime_summary_dao.get_latest_summary()
        if not summary:
            return success_response(data={
                "total_alarms": 0,
                "high_level_alarms": 0,
                "medium_level_alarms": 0,
                "low_level_alarms": 0,
                "total_energy": 0,
                "peak_load": 0
            }, message="暂无数据")
        
        result = {
            "total_alarms": summary.total_alarms,
            "high_level_alarms": summary.high_level_alarms,
            "medium_level_alarms": summary.medium_level_alarms,
            "low_level_alarms": summary.low_level_alarms,
            "total_energy": summary.total_energy,
            "peak_load": summary.peak_load
        }
        
        return success_response(data=result)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/realtime', methods=['GET'])
@token_required
def get_realtime_data():
    """获取实时数据"""
    try:
        summary = realtime_summary_dao.get_latest_summary()
        if not summary:
            return success_response(data={
                "total_alarms": 0,
                "high_level_alarms": 0,
                "total_energy": 0,
                "peak_load": 0
            }, message="暂无数据")
        
        result = {
            "total_alarms": summary.total_alarms,
            "high_level_alarms": summary.high_level_alarms,
            "total_energy": summary.total_energy,
            "peak_load": summary.peak_load
        }
        
        return success_response(data=result)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/summary/latest', methods=['GET'])
@token_required
def get_latest_summary():
    """获取最新的实时汇总数据"""
    try:
        summary = realtime_summary_dao.get_latest_summary()
        if not summary:
            return success_response(data={}, message="暂无数据")
        
        result = {
            "summary_id": summary.summary_id,
            "statistics_time": summary.statistics_time.isoformat(),
            "total_alarms": summary.total_alarms,
            "high_level_alarms": summary.high_level_alarms,
            "medium_level_alarms": summary.medium_level_alarms,
            "low_level_alarms": summary.low_level_alarms,
            "total_energy": summary.total_energy,
            "peak_load": summary.peak_load,
            "plant_area_id": summary.plant_area_id
        }
        
        return success_response(data=result)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/summary/alarm-statistics', methods=['GET'])
@token_required
def get_alarm_statistics():
    """获取告警统计信息"""
    try:
        days = int(request.args.get('days', 7))
        statistics = realtime_summary_dao.get_alarm_statistics(days)
        return success_response(data=statistics)
        
    except Exception as e:
        return error_response(str(e), 500)

# ============ 历史趋势数据 ============
@dashboard_bp.route('/trends/energy', methods=['GET'])
@token_required
def get_energy_trends():
    """获取能源历史趋势数据"""
    try:
        energy_type = request.args.get('type', required=True)
        cycle = request.args.get('cycle')
        
        trends = historical_trend_dao.get_trends_by_energy_type(energy_type, cycle)
        
        # 转换为字典列表
        trend_list = [{
            "trend_id": trend.trend_id,
            "energy_type": trend.energy_type,
            "statistical_date": trend.statistical_date.isoformat(),
            "statistical_cycle": trend.statistical_cycle,
            "energy_value": trend.energy_value,
            "yoy_growth_rate": trend.yoy_growth_rate,
            "mom_growth_rate": trend.mom_growth_rate,
            "industry_average": trend.industry_average
        } for trend in trends]
        
        return success_response(data=trend_list)
        
    except Exception as e:
        return error_response(str(e), 500)

@dashboard_bp.route('/trends/comparison', methods=['GET'])
@token_required
def get_energy_comparison():
    """获取多能源类型对比数据"""
    try:
        start_date = request.args.get('start_date', required=True)
        end_date = request.args.get('end_date', required=True)
        
        # 转换日期格式
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
        
        comparison = historical_trend_dao.get_energy_comparison(start_date, end_date)
        return success_response(data=comparison)
        
    except Exception as e:
        return error_response(str(e), 500)