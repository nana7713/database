from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, DECIMAL
from base import db_manager
from models.plant_area import PlantArea

Base = db_manager.Base

class Device(Base):
    __tablename__ = 'device'
    device_id = Column(String(20), primary_key=True)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    plant_area_id = Column(String(20), ForeignKey('plant_area.plant_area_id'))
    manufacturer = Column(String(100))
    model = Column(String(100))
    installation_date = Column(DateTime)
    status = Column(String(20), default='正常')
    last_maintenance_date = Column(DateTime)

class Alarm(Base):
    __tablename__ = 'alarm'
    alarm_id = Column(String(20), primary_key=True)
    device_id = Column(String(20), ForeignKey('device.device_id'), nullable=False)
    alarm_type = Column(String(50), nullable=False)
    occur_time = Column(DateTime, nullable=False)
    alarm_level = Column(Integer, nullable=False)
    alarm_content = Column(String(255), nullable=False)
    status = Column(String(20), default='未处理')
    threshold_value = Column(DECIMAL(10, 2))

class MaintenanceOrder(Base):
    __tablename__ = 'maintenance_order'
    order_id = Column(String(20), primary_key=True)
    alarm_id = Column(String(20), ForeignKey('alarm.alarm_id'), nullable=False)
    maintainer_id = Column(String(20), nullable=False)
    dispatch_time = Column(DateTime, nullable=False)
    finish_time = Column(DateTime)
    result = Column(String(255))
    attachment_path = Column(String(255))
