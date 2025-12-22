# models/plant_area.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from base import db_manager

Base = db_manager.Base

class PlantArea(Base):
    __tablename__ = 'plant_area'
    plant_area_id = Column(String(20), primary_key=True)
    plant_area_name = Column(String(100), nullable=False, unique=True)
    location_desc = Column(String(255))
    manager_id = Column(String(20), ForeignKey('users.user_id'))
    contact_phone = Column(String(20))
    