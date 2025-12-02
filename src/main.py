from dao import UserDao
from models.user import User

userdao=UserDao.Userdao()
user_data = {
    'user_id': '1',
    'username': 'testuser',
    'password_hash': 'hashed_password_123',
    'full_name': '张三',
    'email': 'zhangsan@example.com',
    'phone': '13800138000'
}
userdao.insert(user_data)
users=userdao.selectAll()
for user in users:
    print(f"  ID: {user['user_id']}")     
    print(f"  用户名: {user['username']}")
    print(f"  邮箱: {user['email']}")
    print(f"  姓名: {user['full_name']}")
    print(f"  电话: {user['phone']}")