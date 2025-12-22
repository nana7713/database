# models/transformer_monitoring.py
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from base import db_manager
from datetime import datetime

Base = db_manager.Base

class TransformerMonitoringData(Base):
    __tablename__ = 'transformer_monitoring_data'
    
    __table_args__ = (
        CheckConstraint('load_rate >= 0', name='ck_load_rate'),
        CheckConstraint("running_status IN('正常', '异常')", name='ck_running_status'),
        UniqueConstraint('substation_id', 'transformer_id', 'collection_time', name='uk_transformer_time')
    )
    
    transformer_data_id = Column(Integer, primary_key=True, autoincrement=True)  # BIGINT
    substation_id = Column(String(20), ForeignKey('substation.substation_id'), nullable=False)
    transformer_id = Column(String(20), nullable=False)
    collection_time = Column(DateTime, nullable=False, default=datetime.now)
    load_rate = Column(Numeric(5, 2))
    winding_temp = Column(Numeric(5, 2), comment='单位：℃')
    core_temp = Column(Numeric(5, 2), comment='单位：℃')
    ambient_temp = Column(Numeric(5, 2), comment='单位：℃')
    ambient_humidity = Column(Numeric(5, 2), comment='单位：%')
    running_status = Column(String(10)) 

    