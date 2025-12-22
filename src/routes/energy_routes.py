from flask import Blueprint, request
from dao.EnergyManagementDAO import EnergyManagementDAO
from utils.middleware import token_required, roles_required
from utils.response import success_response, error_response
from datetime import datetime

# 创建蓝图
energy_bp = Blueprint('energy', __name__, url_prefix='/api/energy')

# 初始化DAO
energy_dao = EnergyManagementDAO()

# ============ 能耗设备管理 ============
@energy_bp.route('/devices', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def add_energy_device():
    """新增能耗设备信息"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        # 验证必要字段
        required_fields = ['equipment_id', 'equipment_name', 'equipment_type', 'plant_area_id']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        equipment_id = energy_dao.add_device(data)
        return success_response(data={"equipment_id": equipment_id}, message="设备添加成功", code=201)
        
    except Exception as e:
        return error_response(str(e), 500)

@energy_bp.route('/devices', methods=['GET'])
@token_required
def get_all_energy_devices():
    """获取所有能耗设备列表"""
    try:
        devices = energy_dao.get_all_devices()
        
        # 转换为字典列表
        device_list = [{"equipment_id": d.equipment_id,
                       "equipment_name": d.equipment_name,
                       "equipment_type": d.equipment_type,
                       "plant_area_id": d.plant_area_id,
                       "installed_location": d.installed_location,
                       "installation_date": d.installation_date.isoformat() if d.installation_date else None,
                       "manufacturer": d.manufacturer,
                       "model": d.model,
                       "specification": d.specification,
                       "unit": d.unit,
                       "measurement_range": d.measurement_range,
                       "accuracy": d.accuracy,
                       "communication_protocol": d.communication_protocol,
                       "status": d.status,
                       "last_calibration_date": d.last_calibration_date.isoformat() if d.last_calibration_date else None,
                       "next_calibration_date": d.next_calibration_date.isoformat() if d.next_calibration_date else None,
                       "remark": d.remark} for d in devices]
        
        return success_response(data=device_list)
        
    except Exception as e:
        return error_response(str(e), 500)

# ============ 能耗监测数据 ============
@energy_bp.route('/monitoring', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def add_monitoring_data():
    """录入能耗监测数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        # 验证必要字段
        required_fields = ['equipment_id', 'collection_time', 'energy_consumption', 'unit', 'data_quality', 'plant_area_id']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        # 转换日期格式
        if isinstance(data['collection_time'], str):
            data['collection_time'] = datetime.fromisoformat(data['collection_time'].replace('Z', '+00:00'))
        
        data_id = energy_dao.add_monitoring_data(data)
        return success_response(data={"data_id": data_id}, message="监测数据录入成功", code=201)
        
    except Exception as e:
        return error_response(str(e), 500)

@energy_bp.route('/monitoring/device/<equipment_id>', methods=['GET'])
@token_required
def get_monitoring_data_by_device(equipment_id):
    """获取设备的能耗监测数据"""
    try:
        # 获取查询参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if not start_time or not end_time:
            return error_response("缺少必要参数: start_time和end_time", 400)
        
        # 转换日期格式
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        data = energy_dao.get_data_by_time_range(equipment_id, start_time, end_time)
        
        # 转换为字典列表
        data_list = [{
            "data_id": d.data_id,
            "equipment_id": d.equipment_id,
            "collection_time": d.collection_time.isoformat(),
            "energy_consumption": d.energy_consumption,
            "unit": d.unit,
            "data_quality": d.data_quality,
            "plant_area_id": d.plant_area_id,
            "verification_status": d.verification_status
        } for d in data]
        
        return success_response(data=data_list)
        
    except Exception as e:
        return error_response(str(e), 500)

@energy_bp.route('/monitoring/abnormal', methods=['GET'])
@token_required
def get_abnormal_monitoring_data():
    """获取异常监测数据"""
    try:
        data = energy_dao.get_abnormal_data()
        
        # 转换为字典列表
        data_list = [{
            "data_id": d.data_id,
            "equipment_id": d.equipment_id,
            "collection_time": d.collection_time.isoformat(),
            "energy_consumption": d.energy_consumption,
            "unit": d.unit,
            "data_quality": d.data_quality,
            "plant_area_id": d.plant_area_id,
            "verification_status": d.verification_status
        } for d in data]
        
        return success_response(data=data_list)
        
    except Exception as e:
        return error_response(str(e), 500)

@energy_bp.route('/data', methods=['GET'])
@token_required
def get_energy_data():
    """获取能源监控数据"""
    try:
        # 默认获取最新的10条数据
        data = energy_dao.get_latest_monitoring_data(limit=10)
        
        # 转换为字典列表
        data_list = [{"data_id": d.data_id,
                     "equipment_id": d.equipment_id,
                     "collection_time": d.collection_time.isoformat() if d.collection_time else None,
                     "energy_consumption": d.energy_consumption,
                     "unit": d.unit,
                     "data_quality": d.data_quality,
                     "plant_area_id": d.plant_area_id,
                     "verification_status": d.verification_status} for d in data]
        
        return success_response(data=data_list)
        
    except Exception as e:
        return error_response(str(e), 500)

@energy_bp.route('/trend', methods=['GET'])
@token_required
def get_energy_trend():
    """获取能源趋势数据"""
    try:
        # 获取查询参数
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # 如果没有提供日期范围，默认使用过去7天
        if not start_date or not end_date:
            from datetime import datetime, timedelta
            end_date = datetime.now().isoformat()
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        # 这里简化处理，实际应该根据日期范围查询
        data = energy_dao.get_latest_monitoring_data(limit=100)
        
        # 转换为字典列表
        data_list = [{"equipment_id": d.equipment_id,
                     "collection_time": d.collection_time.isoformat() if d.collection_time else None,
                     "energy_consumption": d.energy_consumption,
                     "unit": d.unit} for d in data]
        
        return success_response(data=data_list)
        
    except Exception as e:
        return error_response(str(e), 500)

@energy_bp.route('/monitoring/verify/<int:data_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def verify_monitoring_data(data_id):
    """核实监测数据"""
    try:
        success = energy_dao.verify_data(data_id)
        if success:
            return success_response(message="数据已核实")
        else:
            return error_response("数据不存在", 404)
            
    except Exception as e:
        return error_response(str(e), 500)

# ============ 能耗成本报告 ============
@energy_bp.route('/reports/daily-cost', methods=['GET'])
@token_required
def get_daily_cost_report():
    """获取日成本报告"""
    try:
        date_str = request.args.get('date', required=True)
        report = energy_dao.get_daily_cost_report(date_str)
        
        # 转换为字典列表
        report_list = [{
            "report_id": r.report_id,
            "plant_area_id": r.plant_area_id,
            "statistics_date": r.statistics_date,
            "energy_type": r.energy_type,
            "peak_energy": r.peak_energy,
            "valley_energy": r.valley_energy,
            "flat_energy": r.flat_energy,
            "peak_price": r.peak_price,
            "valley_price": r.valley_price,
            "flat_price": r.flat_price,
            "energy_cost": r.energy_cost
        } for r in report]
        
        return success_response(data=report_list)
        
    except Exception as e:
        return error_response(str(e), 500)