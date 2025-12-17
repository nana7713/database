from models.user import User
from base import db_manager


class UserDao:
    def selectAll(self):
        with db_manager.get_session() as session:
            users = session.query(User).all()
            return [{
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone
            } for user in users]

    def selectByUserId(self, user_id):
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user is not None:
                return {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone': user.phone
                }
            else:
                return None

    def insert(self, user_data):
        with db_manager.get_session() as session:
            user = User(**user_data)
            session.add(user)

    def update(self, user_id, new_data):
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            for key, value in new_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return True

    def deleteByUserId(self, user_id):
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                session.delete(user)
                return True
            return False