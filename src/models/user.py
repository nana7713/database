from base import db_manager
from sqlalchemy import Column, String
class User(db_manager.Base):
    __tablename__ = 'users'
    user_id = Column(String(20), primary_key=True)
    username = Column(String(50), nullable=False)
    password_hash= Column(String(255))
    full_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
 