from models.user import User
from base import db_manager

class Userdao:
    def selectAll(self):
        with db_manager.get_session() as session:
            users=session.query(User).all()
            return [{
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone
            } for user in users]
    def selectByUserId(self,user_id):
        with db_manager.get_session() as session:
            user=session.query(User).filter(User.user_id==user_id).all()
            return {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone
            }
    def insert(self,user_data):
        with db_manager.get_session() as session:
            user=User(**user_data)
            session.add(user)
            
    def update(user_id, new_data):
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                print(f"用户ID {user_id} 不存在")
                return None
            for key, value in new_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                    print(f"  设置 {key} = {value}")
            return user
    def deleteByUserId(self,user_id):
        with db_manager.get_session() as session:
            user=session.query(User).filter(User.user_id == user_id).all()
            if user:
                session.delete(user)