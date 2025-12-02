# models/circuit_monitoring.py
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from base import db_manager
from datetime import datetime

Base = db_manager.Base

class CircuitMonitoringData(Base):
    __tablename__ = 'circuit_monitoring_data'
    
    __table_args__ = (
        CheckConstraint('power_factor < 1 AND power_factor > -1', name='ck_power_factor_range'),
        CheckConstraint("switch_status IN ('分闸', '合闸')", name='ck_switch_status'),
        UniqueConstraint('substation_id', 'circuit_id', 'collection_time', name='uk_circuit_time')
    )
    
    circuit_data_id = Column(Integer, primary_key=True, autoincrement=True)  # BIGINT 在SQLAlchemy中通常用Integer
    substation_id = Column(String(20), ForeignKey('substation.substation_id'), nullable=False)
    circuit_id = Column(String(20), nullable=False)
    collection_time = Column(DateTime, nullable=False, default=datetime.now)
    voltage = Column(Numeric(10, 2), comment='单位: kV')  # DECIMAL在SQLAlchemy中用Numeric
    current = Column(Numeric(10, 2), comment='单位: A')
    active_power = Column(Numeric(10, 2), comment='单位: kW')
    reactive_power = Column(Numeric(10, 2), comment='单位：kVar')
    power_factor = Column(Numeric(3, 2))
    forward_active_energy = Column(Numeric(15, 2), comment='单位：kWh')
    reverse_active_energy = Column(Numeric(15, 2), comment='单位：kWh')
    switch_status = Column(String(10))
    cable_temp = Column(Numeric(5, 2), comment='单位：℃')
    capacitor_temp = Column(Numeric(5, 2), comment='单位：℃')
  
    