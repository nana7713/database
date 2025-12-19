from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models import EnergyMeteringEquipment, EnergyMonitoringData, PeakValleyEnergyData
from datetime import datetime

class EnergyManagementDAO:
    def __init__(self, db_session: Session):
        """
        :param db_session: 数据库会话对象 (SQLAlchemy Session)
        """
        self.session = db_session

    # ---------------------------------------------------------
    # 任务书 3.3 要求功能：新增 (Insert)
    # ---------------------------------------------------------
    def add_monitoring_data(self, data_dict):
        """
        录入能耗监测数据
        :param data_dict: 包含数据字段的字典
        """
        new_data = EnergyMonitoringData(
            equipment_id=data_dict['equipment_id'],
            collection_time=data_dict['collection_time'],
            energy_consumption=data_dict['energy_consumption'],
            unit=data_dict['unit'],
            data_quality=data_dict['data_quality'],
            plant_area_id=data_dict['plant_area_id'],
            verification_status=data_dict.get('verification_status', '已核实')
        )
        self.session.add(new_data)
        self.session.commit()
        return new_data.data_id

    def add_device(self, device_dict):
        """新增能耗设备信息"""
        device = EnergyMeteringEquipment(**device_dict)
        self.session.add(device)
        self.session.commit()
        return device.equipment_id

    # ---------------------------------------------------------
    # 任务书 3.3 要求功能：查询 (Query)
    # 对应示例: queryCircuitDataByTime
    # ---------------------------------------------------------
    def get_data_by_time_range(self, equipment_id, start_time, end_time):
        """
        按时间范围查询某设备的能耗数据（用于前端绘制曲线图）
        """
        results = self.session.query(EnergyMonitoringData).filter(
            EnergyMonitoringData.equipment_id == equipment_id,
            EnergyMonitoringData.collection_time >= start_time,
            EnergyMonitoringData.collection_time <= end_time
        ).order_by(EnergyMonitoringData.collection_time.asc()).all()
        return results

    def get_abnormal_data(self):
        """
        查询数据质量差或待核实的数据（用于数据清洗页面）
        """
        results = self.session.query(EnergyMonitoringData).filter(
            (EnergyMonitoringData.data_quality == '差') | 
            (EnergyMonitoringData.verification_status == '待核实')
        ).all()
        return results

    # ---------------------------------------------------------
    # 任务书 3.3 要求功能：修改 (Update)
    # ---------------------------------------------------------
    def verify_data(self, data_id):
        """
        人工核实数据，更新状态为'已核实'
        """
        record = self.session.query(EnergyMonitoringData).filter_by(data_id=data_id).first()
        if record:
            record.verification_status = '已核实'
            self.session.commit()
            return True
        return False

    # ---------------------------------------------------------
    # 任务书 3.3 要求功能：统计查询 (Complex Query)
    # ---------------------------------------------------------
    def get_daily_cost_report(self, date_str):
        """
        获取某日的各厂区成本日报
        """
        results = self.session.query(PeakValleyEnergyData).filter(
            PeakValleyEnergyData.statistics_date == date_str
        ).order_by(desc(PeakValleyEnergyData.energy_cost)).all()
        return results