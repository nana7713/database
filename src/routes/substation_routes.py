# routes/substation_routes.py
from flask import Blueprint, request, jsonify
from dao.SubstationDao import SubstationDao
from dao.CircuitMonitoringDao import CircuitMonitoringDao
from dao.TransformerMonitoringDao import TransformerMonitoringDao
from dao.PlantAreaDao import PlantAreaDao
from utils.middleware import token_required, roles_required
from utils.response import success_response, error_response
from datetime import datetime, timedelta

substation_bp = Blueprint('substation', __name__, url_prefix='/api/substation')

# 初始化DAO
substation_dao = SubstationDao()
circuit_dao = CircuitMonitoringDao()
transformer_dao = TransformerMonitoringDao()
plant_area_dao = PlantAreaDao()

# ============ 配电房管理 ============
@substation_bp.route('/rooms', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE', 'MANAGER', 'DATA_ANALYST')
def get_all_substations():
    """获取所有配电房"""
    try:
        substations = substation_dao.selectAll()
        return success_response(data=substations)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/rooms', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def create_substation():
    """创建配电房"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['substation_id', 'substation_name', 'plant_area_id', 'voltage_level']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        # 检查厂区是否存在
        plant_area = plant_area_dao.selectByPlantAreaId(data['plant_area_id'])
        if not plant_area:
            return error_response("指定的厂区不存在", 400)
        
        # 转换日期格式
        if 'commissioning_date' in data and data['commissioning_date']:
            try:
                data['commissioning_date'] = datetime.fromisoformat(data['commissioning_date'].replace('Z', '+00:00'))
            except ValueError:
                return error_response("日期格式错误，请使用ISO格式", 400)
        
        new_id = substation_dao.insert(data)
        return success_response(data={'substation_id': new_id}, message="创建成功", code=201)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/rooms/<substation_id>', methods=['GET'])
@token_required
def get_substation_detail(substation_id):
    """获取配电房详情"""
    try:
        substation = substation_dao.selectBySubstationId(substation_id)
        if not substation:
            return error_response("配电房不存在", 404)
        
        # 获取关联数据（可选）
        include_circuits = request.args.get('include_circuits', 'false').lower() == 'true'
        include_transformers = request.args.get('include_transformers', 'false').lower() == 'true'
        
        result = substation
        if include_circuits:
            circuits = circuit_dao.selectBySubstation(substation_id)
            result['circuits'] = circuits[:10]  # 只显示最近10条
        
        if include_transformers:
            transformers = transformer_dao.selectBySubstation(substation_id)
            result['transformers'] = transformers[:10]
        
        return success_response(data=result)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/rooms/<substation_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def update_substation(substation_id):
    """更新配电房信息"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求体为空", 400)
        
        # 检查配电房是否存在
        existing = substation_dao.selectBySubstationId(substation_id)
        if not existing:
            return error_response("配电房不存在", 404)
        
        # 如果有日期字段，转换格式
        if 'commissioning_date' in data and data['commissioning_date']:
            try:
                data['commissioning_date'] = datetime.fromisoformat(data['commissioning_date'].replace('Z', '+00:00'))
            except ValueError:
                return error_response("日期格式错误，请使用ISO格式", 400)
        
        updated = substation_dao.update(substation_id, data)
        if updated:
            return success_response(data=updated, message="更新成功")
        else:
            return error_response("更新失败", 500)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/rooms/<substation_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_substation(substation_id):
    """删除配电房"""
    try:
        success = substation_dao.deleteBySubstationId(substation_id)
        if success:
            # 同时删除关联的监测数据
            circuit_dao.deleteBySubstation(substation_id)
            return success_response(message="删除成功")
        else:
            return error_response("配电房不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/rooms/plant_area/<plant_area_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE', 'MANAGER')
def get_substations_by_plant_area(plant_area_id):
    """根据厂区获取配电房"""
    try:
        substations = substation_dao.selectByPlantAreaId(plant_area_id)
        return success_response(data=substations)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/rooms/responsible/<user_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def get_substations_by_responsible(user_id):
    """根据负责人获取配电房"""
    try:
        substations = substation_dao.selectByResponsibleUserId(user_id)
        return success_response(data=substations)
    except Exception as e:
        return error_response(str(e), 500)

# ============ 回路监测数据 ============
@substation_bp.route('/circuits', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE', 'DATA_ANALYST')
def get_circuit_data():
    """获取回路监测数据"""
    try:
        substation_id = request.args.get('substation_id')
        circuit_id = request.args.get('circuit_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 100, type=int)
        
        if substation_id and circuit_id:
            data = circuit_dao.selectBySubstationAndCircuit(substation_id, circuit_id)
        elif substation_id:
            data = circuit_dao.selectLatestBySubstation(substation_id, limit)
        else:
            data = circuit_dao.selectAll()
        
        # 时间过滤（如果提供时间范围）
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                data = [record for record in data 
                       if start <= datetime.fromisoformat(record['collection_time']) <= end]
            except ValueError:
                pass  # 如果时间格式错误，返回所有数据
        
        return success_response(data=data)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/circuits', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def create_circuit_data():
    """创建回路监测数据（支持批量）"""
    try:
        data = request.get_json()
        
        if isinstance(data, list):  # 批量插入
            ids = circuit_dao.batchInsert(data)
            return success_response(data={'inserted_count': len(ids)}, message="批量插入成功", code=201)
        else:  # 单条插入
            required_fields = ['substation_id', 'circuit_id', 'collection_time']
            for field in required_fields:
                if field not in data:
                    return error_response(f"缺少必要字段: {field}", 400)
            
            circuit_dao.insert(data)
            return success_response(message="创建成功", code=201)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/circuits/<int:circuit_data_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def get_circuit_data_by_id(circuit_data_id):
    """获取单条回路监测数据"""
    try:
        data = circuit_dao.selectById(circuit_data_id)
        if data:
            return success_response(data=data)
        else:
            return error_response("回路监测数据不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/circuits/<int:circuit_data_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def update_circuit_data(circuit_data_id):
    """更新回路监测数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求体为空", 400)
        
        updated = circuit_dao.update(circuit_data_id, data)
        if updated:
            return success_response(message="更新成功")
        else:
            return error_response("回路监测数据不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/circuits/<int:circuit_data_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_circuit_data(circuit_data_id):
    """删除回路监测数据"""
    try:
        success = circuit_dao.deleteById(circuit_data_id)
        if success:
            return success_response(message="删除成功")
        else:
            return error_response("回路监测数据不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)

# ============ 变压器监测数据 ============
@substation_bp.route('/transformers', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE', 'DATA_ANALYST')
def get_transformer_data():
    """获取变压器监测数据"""
    try:
        substation_id = request.args.get('substation_id')
        transformer_id = request.args.get('transformer_id')
        status = request.args.get('status')
        
        if status == 'abnormal':
            data = transformer_dao.selectAbnormalRecords()
        elif substation_id:
            data = transformer_dao.selectBySubstation(substation_id)
        else:
            data = transformer_dao.selectAll()
        
        # 如果指定了变压器ID，进行过滤
        if transformer_id:
            data = [record for record in data if record.get('transformer_id') == transformer_id]
        
        return success_response(data=data)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/transformers', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def create_transformer_data():
    """创建变压器监测数据"""
    try:
        data = request.get_json()
        
        required_fields = ['substation_id', 'transformer_id', 'collection_time']
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必要字段: {field}", 400)
        
        transformer_dao.insert(data)
        return success_response(message="创建成功", code=201)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/transformers/<int:transformer_data_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def get_transformer_data_by_id(transformer_data_id):
    """获取单条变压器监测数据"""
    try:
        data = transformer_dao.selectById(transformer_data_id)
        if data:
            return success_response(data=data)
        else:
            return error_response("变压器监测数据不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/transformers/<int:transformer_data_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def update_transformer_data(transformer_data_id):
    """更新变压器监测数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求体为空", 400)
        
        updated = transformer_dao.update(transformer_data_id, data)
        if updated:
            return success_response(message="更新成功")
        else:
            return error_response("变压器监测数据不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/transformers/<int:transformer_data_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_transformer_data(transformer_data_id):
    """删除变压器监测数据"""
    try:
        success = transformer_dao.deleteById(transformer_data_id)
        if success:
            return success_response(message="删除成功")
        else:
            return error_response("变压器监测数据不存在", 404)
    except Exception as e:
        return error_response(str(e), 500)


# ============ 视图相关接口============
@substation_bp.route('/views/abnormal_data', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def get_abnormal_data_view():
    """回路异常数据视图（课程设计要求）"""
    try:
        # 实际项目中这里应该调用数据库视图，这里模拟实现
        all_circuits = circuit_dao.selectAll()
        
        # 过滤异常数据：电压超过37kV或电流超过500A
        abnormal_data = []
        for circuit in all_circuits:
            voltage = circuit.get('voltage')
            current = circuit.get('current')
            
            if (voltage and voltage > 37.0) or (current and current > 500.0):
                # 标记异常原因
                if voltage and voltage > 37.0:
                    circuit['abnormal_reason'] = f'电压超限: {voltage}kV > 37kV'
                elif current and current > 500.0:
                    circuit['abnormal_reason'] = f'电流超限: {current}A > 500A'
                else:
                    circuit['abnormal_reason'] = '数据异常'
                
                abnormal_data.append(circuit)
        
        return success_response(data=abnormal_data)
    except Exception as e:
        return error_response(str(e), 500)

@substation_bp.route('/views/daily_summary', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MANAGER', 'DATA_ANALYST')
def get_daily_summary_view():
    """配电房日报表视图"""
    try:
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 这里应该是从数据库视图查询，这里模拟数据
        summary = {
            'date': date_str,
            'total_substations': len(substation_dao.selectAll()),
            'operating_substations': 25,  # 示例数据
            'maintenance_substations': 2,  # 示例数据
            'total_energy_consumption': 12500.5,  # kWh
            'peak_load': 850.2,  # kW
            'abnormal_events': 3,
            'avg_power_factor': 0.92
        }
        
        return success_response(data=summary)
    except Exception as e:
        return error_response(str(e), 500)