# routes/pv_routes.py
from flask import Blueprint, request, jsonify
from dao.PvDeviceDao import PvDeviceDao
from dao.PvGenerationDao import PvGenerationDao
from dao.PvForecastDao import PvForecastDao
from utils.middleware import token_required, roles_required
from utils.response import success_response, error_response
from datetime import datetime, timedelta
import decimal

pv_bp = Blueprint('pv', __name__, url_prefix='/api/pv')

# 初始化DAO
device_dao = PvDeviceDao()
generation_dao = PvGenerationDao()
forecast_dao = PvForecastDao()

# ==================== 光伏设备管理 ====================
@pv_bp.route('/devices', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE', 'DATA_ANALYST', 'MANAGER')
def get_all_devices():
    """获取所有光伏设备"""
    try:
        device_type = request.args.get('type')
        status = request.args.get('status')
        
        if device_type:
            devices = device_dao.select_by_type(device_type)
        elif status:
            devices = device_dao.select_by_status(status)
        else:
            devices = device_dao.select_all()
        
        return success_response(data=devices)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/devices', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def create_device():
    """创建光伏设备"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空', 400)
        
        # 验证必要字段
        required_fields = ['device_id', 'device_type', 'location', 'capacity', 
                          'operation_date', 'calibration_cycle', 'protocol']
        for field in required_fields:
            if field not in data:
                return error_response(f'缺少必要字段: {field}', 400)
        
        # 设置默认状态
        if 'status' not in data:
            data['status'] = '正常'
        
        # 转换日期格式
        if 'operation_date' in data and isinstance(data['operation_date'], str):
            data['operation_date'] = datetime.fromisoformat(data['operation_date'].replace('Z', '+00:00')).date()
        
        device_id = device_dao.insert(data)
        return success_response(
            data={'device_id': device_id},
            message='设备创建成功',
            code=201
        )
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/devices/<device_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE', 'DATA_ANALYST')
def get_device_detail(device_id):
    """获取设备详情"""
    try:
        device = device_dao.select_by_id(device_id)
        if not device:
            return error_response('设备不存在', 404)
        
        # 可选：获取设备关联的发电数据
        include_generation = request.args.get('include_generation', 'false').lower() == 'true'
        include_forecast = request.args.get('include_forecast', 'false').lower() == 'true'
        
        result = device
        
        if include_generation:
            generation_data = generation_dao.select_by_device(device_id)
            result['generation_data'] = generation_data[:50]  # 限制数量
        
        if include_forecast:
            forecast_data = forecast_dao.select_by_device(device_id)
            result['forecast_data'] = forecast_data
        
        return success_response(data=result)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/devices/<device_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def update_device(device_id):
    """更新设备信息"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空', 400)
        
        # 检查设备是否存在
        existing = device_dao.select_by_id(device_id)
        if not existing:
            return error_response('设备不存在', 404)
        
        # 处理日期字段
        if 'operation_date' in data and isinstance(data['operation_date'], str):
            data['operation_date'] = datetime.fromisoformat(data['operation_date'].replace('Z', '+00:00')).date()
        
        updated = device_dao.update(device_id, data)
        if updated:
            return success_response(data=updated, message='设备更新成功')
        else:
            return error_response('更新失败', 500)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/devices/<device_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_device(device_id):
    """删除设备"""
    try:
        success = device_dao.delete(device_id)
        if success:
            return success_response(message='设备删除成功')
        else:
            return error_response('设备不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/devices/stats/status', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MANAGER', 'DATA_ANALYST')
def get_device_status_stats():
    """获取设备状态统计"""
    try:
        stats = {
            'total': len(device_dao.select_all()),
            'normal': device_dao.count_by_status('正常'),
            'fault': device_dao.count_by_status('故障'),
            'offline': device_dao.count_by_status('离线')
        }
        
        # 计算比例
        if stats['total'] > 0:
            stats['normal_rate'] = round(stats['normal'] / stats['total'] * 100, 2)
            stats['fault_rate'] = round(stats['fault'] / stats['total'] * 100, 2)
            stats['offline_rate'] = round(stats['offline'] / stats['total'] * 100, 2)
        
        return success_response(data=stats)
    except Exception as e:
        return error_response(str(e), 500)

# ==================== 光伏发电数据管理 ====================
@pv_bp.route('/generation', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST', 'MANAGER')
def get_generation_data():
    """获取发电数据"""
    try:
        device_id = request.args.get('device_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        abnormal_only = request.args.get('abnormal', 'false').lower() == 'true'
        
        if abnormal_only:
            # 获取逆变器效率低于85%的异常数据
            data = generation_dao.select_abnormal_efficiency(85.0)
        elif device_id and start_time and end_time:
            # 按设备和时间范围查询
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                data = generation_dao.select_by_time_range(start_dt, end_dt)
                # 按设备ID过滤
                data = [record for record in data if record.get('device_id') == device_id]
            except ValueError:
                return error_response('时间格式错误，请使用ISO格式', 400)
        elif device_id:
            # 按设备查询
            data = generation_dao.select_by_device(device_id)
        else:
            data = generation_dao.select_all()
        
        # 分页处理
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_data = data[start_idx:end_idx]
        
        return success_response(data={
            'data': paginated_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(data),
                'total_pages': (len(data) + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/generation', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def create_generation_data():
    """创建发电数据（支持批量）"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空', 400)
        
        if isinstance(data, list):
            # 批量插入
            ids = generation_dao.batch_insert(data)
            return success_response(
                data={'inserted_count': len(ids)},
                message='批量插入成功',
                code=201
            )
        else:
            # 单条插入
            required_fields = ['data_id', 'device_id', 'grid_point_id', 
                             'collect_time', 'generation', 'feed_in', 'self_use']
            for field in required_fields:
                if field not in data:
                    return error_response(f'缺少必要字段: {field}', 400)
            
            # 转换时间格式
            if 'collect_time' in data and isinstance(data['collect_time'], str):
                data['collect_time'] = datetime.fromisoformat(data['collect_time'].replace('Z', '+00:00'))
            
            data_id = generation_dao.insert(data)
            return success_response(
                data={'data_id': data_id},
                message='数据创建成功',
                code=201
            )
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/generation/<data_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def get_generation_detail(data_id):
    """获取单条发电数据"""
    try:
        data = generation_dao.select_by_id(data_id)
        if data:
            return success_response(data=data)
        else:
            return error_response('发电数据不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/generation/<data_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER')
def update_generation_data(data_id):
    """更新发电数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空', 400)
        
        updated = generation_dao.update(data_id, data)
        if updated:
            return success_response(data=updated, message='数据更新成功')
        else:
            return error_response('发电数据不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/generation/<data_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_generation_data(data_id):
    """删除发电数据"""
    try:
        success = generation_dao.delete(data_id)
        if success:
            return success_response(message='数据删除成功')
        else:
            return error_response('发电数据不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)

# ==================== 光伏预测数据管理 ====================
@pv_bp.route('/forecasts', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST', 'MANAGER')
def get_forecast_data():
    """获取预测数据"""
    try:
        device_id = request.args.get('device_id')
        forecast_date = request.args.get('date')
        high_deviation = request.args.get('high_deviation', 'false').lower() == 'true'
        
        if high_deviation:
            # 获取偏差率超过15%的数据
            data = forecast_dao.select_high_deviation(15.0)
        elif device_id and forecast_date:
            # 按设备和日期查询
            try:
                date_obj = datetime.fromisoformat(forecast_date.replace('Z', '+00:00')).date()
                all_data = forecast_dao.select_by_date(date_obj)
                data = [record for record in all_data if record.get('device_id') == device_id]
            except ValueError:
                return error_response('日期格式错误，请使用ISO格式', 400)
        elif device_id:
            # 按设备查询
            data = forecast_dao.select_by_device(device_id)
        elif forecast_date:
            # 按日期查询
            try:
                date_obj = datetime.fromisoformat(forecast_date.replace('Z', '+00:00')).date()
                data = forecast_dao.select_by_date(date_obj)
            except ValueError:
                return error_response('日期格式错误，请使用ISO格式', 400)
        else:
            data = forecast_dao.select_all()
        
        return success_response(data=data)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/forecasts', methods=['POST'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def create_forecast():
    """创建预测数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空', 400)
        
        required_fields = ['forecast_id', 'device_id', 'grid_point_id', 
                          'forecast_date', 'time_slot', 'forecast_generation', 'model_version']
        for field in required_fields:
            if field not in data:
                return error_response(f'缺少必要字段: {field}', 400)
        
        # 转换日期格式
        if 'forecast_date' in data and isinstance(data['forecast_date'], str):
            data['forecast_date'] = datetime.fromisoformat(data['forecast_date'].replace('Z', '+00:00')).date()
        
        forecast_id = forecast_dao.insert(data)
        return success_response(
            data={'forecast_id': forecast_id},
            message='预测数据创建成功',
            code=201
        )
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/forecasts/<forecast_id>', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def get_forecast_detail(forecast_id):
    """获取单条预测数据"""
    try:
        forecast = forecast_dao.select_by_id(forecast_id)
        if forecast:
            return success_response(data=forecast)
        else:
            return error_response('预测数据不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/forecasts/<forecast_id>', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def update_forecast(forecast_id):
    """更新预测数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空', 400)
        
        # 转换日期格式
        if 'forecast_date' in data and isinstance(data['forecast_date'], str):
            data['forecast_date'] = datetime.fromisoformat(data['forecast_date'].replace('Z', '+00:00')).date()
        
        updated = forecast_dao.update(forecast_id, data)
        if updated:
            return success_response(data=updated, message='预测数据更新成功')
        else:
            return error_response('预测数据不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/forecasts/<forecast_id>/deviation', methods=['PUT'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def update_deviation_rate(forecast_id):
    """更新偏差率（根据实际发电量）"""
    try:
        data = request.get_json()
        actual_generation = data.get('actual_generation')
        
        if actual_generation is None:
            return error_response('缺少实际发电量数据', 400)
        
        result = forecast_dao.update_deviation_rate(forecast_id, actual_generation)
        if result:
            return success_response(data=result, message='偏差率更新成功')
        else:
            return error_response('预测数据不存在或无法计算偏差率', 404)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/forecasts/<forecast_id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_forecast(forecast_id):
    """删除预测数据"""
    try:
        success = forecast_dao.delete(forecast_id)
        if success:
            return success_response(message='预测数据删除成功')
        else:
            return error_response('预测数据不存在', 404)
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 业务视图接口（课程设计要求） ====================
@pv_bp.route('/views/daily_generation', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST', 'MANAGER')
def get_daily_generation_view():
    """光伏日发电量视图（课程设计要求）"""
    try:
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 模拟视图数据，实际应该从数据库视图查询
        view_data = {
            'date': date_str,
            'devices': [
                {
                    'device_id': 'PV001',
                    'device_type': '逆变器',
                    'total_generation': 1250.5,
                    'feed_in': 850.2,
                    'self_use': 400.3,
                    'avg_efficiency': 92.5
                },
                {
                    'device_id': 'PV002',
                    'device_type': '汇流箱',
                    'total_generation': 980.3,
                    'feed_in': 650.1,
                    'self_use': 330.2,
                    'avg_efficiency': 88.7
                }
            ],
            'summary': {
                'total_generation': 2230.8,
                'total_feed_in': 1500.3,
                'total_self_use': 730.5,
                'avg_efficiency': 90.6,
                'self_use_rate': 32.7
            }
        }
        
        return success_response(data=view_data)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/views/forecast_deviation', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'DATA_ANALYST')
def get_forecast_deviation_view():
    """光伏预测偏差视图（课程设计要求）"""
    try:
        # 获取高偏差率的数据
        high_deviation_data = forecast_dao.select_high_deviation(15.0)
        
        view_data = {
            'high_deviation_count': len(high_deviation_data),
            'threshold': 15.0,
            'data': high_deviation_data[:20],  # 限制返回数量
            'summary': {
                'max_deviation': max([d.get('deviation_rate', 0) for d in high_deviation_data]) if high_deviation_data else 0,
                'avg_deviation': sum([d.get('deviation_rate', 0) for d in high_deviation_data]) / len(high_deviation_data) if high_deviation_data else 0,
                'needs_optimization': len([d for d in high_deviation_data if d.get('deviation_rate', 0) > 20.0])
            }
        }
        
        return success_response(data=view_data)
    except Exception as e:
        return error_response(str(e), 500)

@pv_bp.route('/views/abnormal_efficiency', methods=['GET'])
@roles_required('ADMIN', 'ENERGY_MANAGER', 'MAINTENANCE')
def get_abnormal_efficiency_view():
    """逆变器异常效率视图（课程设计要求）"""
    try:
        # 获取逆变器效率低于85%的数据
        abnormal_data = generation_dao.select_abnormal_efficiency(85.0)
        
        # 按设备分组
        device_abnormal = {}
        for data in abnormal_data:
            device_id = data.get('device_id')
            if device_id not in device_abnormal:
                device_abnormal[device_id] = []
            device_abnormal[device_id].append(data)
        
        view_data = {
            'threshold': 85.0,
            'total_abnormal_records': len(abnormal_data),
            'affected_devices': len(device_abnormal),
            'device_details': [
                {
                    'device_id': device_id,
                    'abnormal_count': len(records),
                    'min_efficiency': min([r.get('inverter_efficiency', 0) for r in records]),
                    'avg_efficiency': sum([r.get('inverter_efficiency', 0) for r in records]) / len(records),
                    'latest_abnormal_time': records[0].get('collect_time') if records else None
                }
                for device_id, records in list(device_abnormal.items())[:10]  # 限制设备数量
            ]
        }
        
        return success_response(data=view_data)
    except Exception as e:
        return error_response(str(e), 500)