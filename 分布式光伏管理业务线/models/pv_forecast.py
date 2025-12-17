from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from base import db_manager

Base = db_manager.Base


class PvForecast(Base):
    __tablename__ = 'pv_forecast'

    forecast_id = Column(String(20), primary_key=True)
    device_id = Column(String(20), ForeignKey('pv_device.device_id', ondelete='CASCADE'), nullable=False)
    grid_point_id = Column(String(20), nullable=False)
    forecast_date = Column(Date, nullable=False)
    time_slot = Column(String(20), nullable=False)
    forecast_generation = Column(Numeric(10, 2), nullable=False)
    actual_data_id = Column(String(20))
    actual_generation = Column(Numeric(10, 2))
    deviation_rate = Column(Numeric(5, 2))
    model_version = Column(String(10), nullable=False)