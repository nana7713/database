from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base import db_manager

Base = db_manager.Base

class Role(Base):
    __tablename__ = 'roles'
    
    role_id = Column(Integer, primary_key=True)
    role_code = Column(String(20), nullable=False, unique=True)
    role_name = Column(String(50), nullable=False)
    description = Column(String(255))

class UserRole(Base):
    __tablename__ = 'user_roles'
    
    user_id = Column(String(20), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.role_id', ondelete='CASCADE'), primary_key=True)
