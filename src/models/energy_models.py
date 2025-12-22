from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from base import db_manager


# 1. 能耗计量设备模型
# 对应表: energy_metering_equipment
class EnergyMeteringEquipment(db_manager.Base):
    __tablename__ = 'energy_metering_equipment'

    equipment_id = Column(String(20), primary_key=True, comment='设备编号')
    energy_type = Column(String(10), nullable=False, comment='能源类型')
    plant_area_id = Column(String(20), nullable=False, comment='所属厂区')
    installation_location = Column(String(255), nullable=False, comment='安装位置')
    pipe_diameter = Column(String(20), comment='管径规格')
    communication_protocol = Column(String(10), nullable=False, comment='通讯协议')
    running_status = Column(String(10), default='正常', comment='运行状态')
    calibration_cycle = Column(Integer, nullable=False, comment='校准周期(月)')
    manufacturer = Column(String(100), comment='生产厂家')

    # 定义关系 (可选，方便连表查询)
    # monitoring_data = relationship("EnergyMonitoringData", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment(id='{self.equipment_id}', type='{self.energy_type}')>"

# 2. 能耗监测数据模型
# 对应表: energy_monitoring_data
class EnergyMonitoringData(db_manager.Base):
    __tablename__ = 'energy_monitoring_data'

    data_id = Column(Integer, primary_key=True, autoincrement=True, comment='数据编号')
    equipment_id = Column(String(20), ForeignKey('energy_metering_equipment.equipment_id'), nullable=False)
    collection_time = Column(DateTime, nullable=False, comment='采集时间')
    energy_consumption = Column(DECIMAL(15, 2), nullable=False, comment='能耗值')
    unit = Column(String(10), nullable=False, comment='单位')
    data_quality = Column(String(4), nullable=False, comment='数据质量')
    plant_area_id = Column(String(20), nullable=False, comment='冗余厂区ID')
    verification_status = Column(String(10), default='已核实', comment='核实状态')

    # equipment = relationship("EnergyMeteringEquipment", back_populates="monitoring_data")

    def __repr__(self):
        return f"<Data(id={self.data_id}, time='{self.collection_time}', val={self.energy_consumption})>"

# 3. 峰谷能耗数据模型
# 对应表: peak_valley_energy_data
class PeakValleyEnergyData(db_manager.Base):
    __tablename__ = 'peak_valley_energy_data'

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    energy_type = Column(String(10), nullable=False)
    plant_area_id = Column(String(20), nullable=False)
    statistics_date = Column(Date, nullable=False)
    
    peak_energy = Column(DECIMAL(15, 2), default=0.00)
    high_peak_energy = Column(DECIMAL(15, 2), default=0.00)
    flat_energy = Column(DECIMAL(15, 2), default=0.00)
    valley_energy = Column(DECIMAL(15, 2), default=0.00)
    total_energy = Column(DECIMAL(15, 2), nullable=False)
    
    peak_valley_price = Column(DECIMAL(10, 4))
    energy_cost = Column(DECIMAL(15, 2), nullable=False)

    def __repr__(self):
        return f"<PeakValley(date='{self.statistics_date}', area='{self.plant_area_id}', cost={self.energy_cost})>"
