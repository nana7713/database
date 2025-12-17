from sqlalchemy import Column, String, Numeric, Date, Integer, CheckConstraint
from base import db_manager

Base = db_manager.Base


class PvDevice(Base):
    __tablename__ = 'pv_device'

    __table_args__ = (
        CheckConstraint("device_type IN ('逆变器', '汇流箱')", name='ck_device_type'),
        CheckConstraint("status IN ('正常', '故障', '离线')", name='ck_status'),
        CheckConstraint("protocol IN ('RS485', 'Lora')", name='ck_protocol'),
    )

    device_id = Column(String(20), primary_key=True)
    device_type = Column(String(10), nullable=False)
    location = Column(String(50), nullable=False)
    capacity = Column(Numeric(8, 2), nullable=False)
    operation_date = Column(Date, nullable=False)
    calibration_cycle = Column(Integer, nullable=False)
    status = Column(String(10), nullable=False)
    protocol = Column(String(10), nullable=False)