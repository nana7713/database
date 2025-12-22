from sqlalchemy import and_, desc
from models.energy_models import EnergyMeteringEquipment, EnergyMonitoringData, PeakValleyEnergyData
from datetime import datetime
from base import db_manager


class EnergyManagementDAO:
    def __init__(self):
        """能耗管理数据访问对象初始化"""
        pass

    # ---------------------------------------------------------    
    # 任务书 3.3 要求功能：新增 (Insert)
    # ---------------------------------------------------------    
    def add_monitoring_data(self, data_dict):
        """
        录入能耗监测数据
        :param data_dict: 包含数据字段的字典
        """
        with db_manager.get_session() as session:
            new_data = EnergyMonitoringData(
                equipment_id=data_dict['equipment_id'],
                collection_time=data_dict['collection_time'],
                energy_consumption=data_dict['energy_consumption'],
                unit=data_dict['unit'],
                data_quality=data_dict['data_quality'],
                plant_area_id=data_dict['plant_area_id'],
                verification_status=data_dict.get('verification_status', '已核实')
            )
            session.add(new_data)
            session.commit()
            return new_data.data_id

    def add_device(self, device_dict):
        """新增能耗设备信息"""
        with db_manager.get_session() as session:
            device = EnergyMeteringEquipment(**device_dict)
            session.add(device)
            session.commit()
            return device.equipment_id

    # ---------------------------------------------------------    
    # 任务书 3.3 要求功能：查询 (Query)
    # 对应示例: queryCircuitDataByTime
    # ---------------------------------------------------------    
    def get_data_by_time_range(self, equipment_id, start_time, end_time):
        """
        按时间范围查询某设备的能耗数据（用于前端绘制曲线图）
        """
        with db_manager.get_session() as session:
            results = session.query(EnergyMonitoringData).filter(
                EnergyMonitoringData.equipment_id == equipment_id,
                EnergyMonitoringData.collection_time >= start_time,
                EnergyMonitoringData.collection_time <= end_time
            ).order_by(EnergyMonitoringData.collection_time.asc()).all()
            return results

    def get_abnormal_data(self):
        """
        查询数据质量差或待核实的数据（用于数据清洗页面）
        """
        with db_manager.get_session() as session:
            results = session.query(EnergyMonitoringData).filter(
                (EnergyMonitoringData.data_quality == '差') | 
                (EnergyMonitoringData.verification_status == '待核实')
            ).all()
            return results

    def get_all_devices(self):
        """
        查询所有能耗设备列表
        """
        with db_manager.get_session() as session:
            results = session.query(EnergyMeteringEquipment).all()
            return results

    def get_latest_monitoring_data(self, limit=10):
        """
        获取最新的能耗监测数据
        :param limit: 返回数据的数量限制
        """
        with db_manager.get_session() as session:
            results = session.query(EnergyMonitoringData).order_by(desc(EnergyMonitoringData.collection_time)).limit(limit).all()
            return results

    # ---------------------------------------------------------    
    # 任务书 3.3 要求功能：修改 (Update)
    # ---------------------------------------------------------    
    def verify_data(self, data_id):
        """
        人工核实数据，更新状态为'已核实'
        """
        with db_manager.get_session() as session:
            record = session.query(EnergyMonitoringData).filter_by(data_id=data_id).first()
            if record:
                record.verification_status = '已核实'
                session.commit()
                return True
            return False

    # ---------------------------------------------------------    
    # 任务书 3.3 要求功能：统计查询 (Complex Query)
    # ---------------------------------------------------------    
    def get_daily_cost_report(self, date_str):
        """
        获取某日的各厂区成本日报
        """
        with db_manager.get_session() as session:
            results = session.query(PeakValleyEnergyData).filter(
                PeakValleyEnergyData.statistics_date == date_str
            ).order_by(desc(PeakValleyEnergyData.energy_cost)).all()
            return results