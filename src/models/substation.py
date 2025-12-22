# models/substation.py
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from base import db_manager
from datetime import date

Base = db_manager.Base

class Substation(Base):
    __tablename__ = 'substation'
    
    substation_id = Column(String(20), primary_key=True)
    plant_area_id = Column(String(20), ForeignKey('plant_area.plant_area_id'), nullable=False)
    substation_name = Column(String(100), nullable=False)
    substation_location_desc = Column(String(255))
    voltage_level = Column(String(10))
    transformer_count = Column(Integer, default=0)
    commissioning_date = Column(Date)
    responsible_user_id = Column(String(20), ForeignKey('users.user_id'))
    contact_phone = Column(String(20))
    

