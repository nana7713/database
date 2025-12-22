from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from base import db_manager

Base = db_manager.Base


class PvGeneration(Base):
    __tablename__ = 'pv_generation'

    data_id = Column(String(20), primary_key=True)
    device_id = Column(String(20), ForeignKey('pv_device.device_id', ondelete='CASCADE'), nullable=False)
    grid_point_id = Column(String(20), nullable=False)
    collect_time = Column(DateTime, nullable=False)
    generation = Column(Numeric(10, 2), nullable=False)
    feed_in = Column(Numeric(10, 2), nullable=False)
    self_use = Column(Numeric(10, 2), nullable=False)
    inverter_efficiency = Column(Numeric(5, 2))
    string_voltage = Column(Numeric(8, 2))
    string_current = Column(Numeric(8, 2))