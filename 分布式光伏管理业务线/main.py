from dao.PvDeviceDao import PvDeviceDao
from dao.PvGenerationDao import PvGenerationDao
from dao.PvForecastDao import PvForecastDao
from dao.UserDao import UserDao
from datetime import datetime, date
import hashlib

# 创建DAO实例
device_dao = PvDeviceDao()
generation_dao = PvGenerationDao()
forecast_dao = PvForecastDao()
user_dao = UserDao()


def hash_password(password):
    """密码加密函数"""
    return hashlib.sha256(password.encode()).hexdigest()


# 测试用户操作
# 测试用户操作
def test_user_operations():
    print("\n=== 测试用户相关功能 ===")

    # 创建UserDao实例
    user_dao = UserDao()

    # 1. 添加用户
    user_data = {
        'user_id': 'USER001',
        'username': 'zhangsan',
        'password_hash': hash_password('password123'),
        'email': 'zhangsan@example.com',
        'full_name': '张三',
        'phone': '13800138000'
    }

    print("1. 添加用户...")
    try:
        user_dao.insert(user_data)
        print(f"   用户添加成功: {user_data['username']}")
    except Exception as e:
        print(f"   添加用户失败: {e}")

    # 再添加几个测试用户
    test_users = [
        {
            'user_id': 'USER002',
            'username': 'lisi',
            'password_hash': hash_password('password456'),
            'email': 'lisi@example.com',
            'full_name': '李四',
            'phone': '13800138001'
        },
        {
            'user_id': 'USER003',
            'username': 'wangwu',
            'password_hash': hash_password('password789'),
            'email': 'wangwu@example.com',
            'full_name': '王五',
            'phone': '13800138002'
        },
        {
            'user_id': 'USER004',
            'username': 'zhaoliu',
            'password_hash': hash_password('password012'),
            'email': 'zhaoliu@example.com',
            'full_name': '赵六',
            'phone': '13800138003'
        }
    ]

    for user in test_users:
        try:
            user_dao.insert(user)
            print(f"   用户添加成功: {user['username']}")
        except Exception as e:
            print(f"   添加用户失败 {user['username']}: {e}")

    # 2. 查询所有用户
    print("\n2. 查询所有用户...")
    try:
        users = user_dao.selectAll()
        print(f"   用户总数: {len(users)}")
        for i, user in enumerate(users, 1):
            print(f"   {i}. ID: {user['user_id']}, 用户名: {user['username']}, 姓名: {user['full_name']}")
    except Exception as e:
        print(f"   查询用户失败: {e}")

    # 3. 查询单个用户 - 调试版本
    print("\n3. 查询单个用户(调试)...")
    try:
        user = user_dao.selectByUserId('USER001')
        print(f"   查询结果类型: {type(user)}")
        print(f"   查询结果: {user}")
        if user:
            print(f"   查询到用户: ID={user.get('user_id')}, 用户名={user.get('username')}")
        else:
            print("   用户不存在")
    except Exception as e:
        print(f"   查询单个用户失败: {e}")
        import traceback
        traceback.print_exc()

    # 4. 更新用户信息
    print("\n4. 更新用户信息...")
    try:
        update_data = {
            'full_name': '张三丰',
            'email': 'zhangsanfeng@example.com',
            'phone': '13900139000'
        }
        result = user_dao.update('USER001', update_data)
        if result:
            print(f"   用户更新成功")
        else:
            print("   用户更新失败")
    except Exception as e:
        print(f"   更新用户失败: {e}")

    # 5. 验证更新结果
    print("\n5. 验证更新结果...")
    try:
        updated_user = user_dao.selectByUserId('USER001')
        if updated_user:
            print(f"   更新后用户信息:")
            print(f"     姓名: {updated_user.get('full_name')}")
            print(f"     邮箱: {updated_user.get('email')}")
            print(f"     电话: {updated_user.get('phone')}")
        else:
            print("   用户不存在")
    except Exception as e:
        print(f"   验证更新失败: {e}")

    # 6. 删除用户 - 详细调试
    print("\n6. 删除用户...")
    try:
        # 先查询确保用户存在
        user_to_delete = user_dao.selectByUserId('USER004')
        print(f"   要删除的用户查询结果: {user_to_delete}")
        print(f"   要删除的用户查询结果类型: {type(user_to_delete)}")

        if user_to_delete:
            print(f"   准备删除用户: {user_to_delete.get('username')}")
            result = user_dao.deleteByUserId('USER004')
            print(f"   删除操作返回值: {result}")
            if result:
                print("   用户删除成功")
            else:
                print("   用户删除失败")
        else:
            print("   要删除的用户不存在")
    except Exception as e:
        print(f"   删除用户失败: {e}")
        import traceback
        traceback.print_exc()

    # 7. 验证删除结果 - 改进的调试版本
    print("\n7. 验证删除结果(调试)...")
    try:
        # 先等待一下，确保删除操作完成
        import time
        time.sleep(0.1)

        deleted_user = user_dao.selectByUserId('USER004')
        print(f"   删除后查询结果: {deleted_user}")
        print(f"   删除后查询结果类型: {type(deleted_user)}")

        if deleted_user is None:
            print("   用户已成功删除")
        else:
            print("   用户删除失败，用户仍然存在")
            print(f"   仍然存在的用户信息: {deleted_user}")
    except Exception as e:
        print(f"   验证删除失败: {e}")
        import traceback
        traceback.print_exc()

    # 8. 查询删除后的用户列表
    print("\n8. 查询删除后的所有用户...")
    try:
        remaining_users = user_dao.selectAll()
        print(f"   剩余用户总数: {len(remaining_users)}")
        user004_found = False
        for i, user in enumerate(remaining_users, 1):
            print(f"   {i}. ID: {user.get('user_id')}, 用户名: {user.get('username')}")
            if user.get('user_id') == 'USER004':
                user004_found = True

        if user004_found:
            print("   ⚠️  USER004 仍然存在于用户列表中!")
        else:
            print("   ✅ USER004 已从用户列表中移除")
    except Exception as e:
        print(f"   查询用户列表失败: {e}")

    print("\n=== 用户功能测试完成 ===")


# 测试光伏设备操作
def test_pv_device():
    print("\n=== 测试光伏设备功能 ===")

    # 添加光伏设备
    device_data = {
        'device_id': 'PV001',
        'device_type': '逆变器',
        'location': '屋顶区域1',
        'capacity': 50.00,
        'operation_date': date(2023, 1, 1),
        'calibration_cycle': 6,
        'status': '正常',
        'protocol': 'RS485'
    }
    try:
        device_id = device_dao.insert(device_data)
        print(f"添加设备ID: {device_id}")
    except Exception as e:
        print(f"添加设备失败: {e}")

    # 查询设备
    try:
        device = device_dao.select_by_id('PV001')
        print(f"查询设备: {device}")
    except Exception as e:
        print(f"查询设备失败: {e}")

    # 更新设备状态
    try:
        update_data = {'status': '离线'}
        device_dao.update('PV001', update_data)
        print("设备状态已更新")
    except Exception as e:
        print(f"更新设备状态失败: {e}")

    # 查询所有设备
    try:
        devices = device_dao.select_all()
        print(f"设备总数: {len(devices)}")
    except Exception as e:
        print(f"查询所有设备失败: {e}")

    print("=== 光伏设备功能测试完成 ===")


def test_pv_generation():
    print("\n=== 测试光伏发电数据功能 ===")

    # 添加发电数据
    generation_data = {
        'data_id': 'GD001',
        'device_id': 'PV001',
        'grid_point_id': 'GP001',
        'collect_time': datetime.now(),
        'generation': 25.50,
        'feed_in': 20.00,
        'self_use': 5.50,
        'inverter_efficiency': 88.50,
        'string_voltage': 220.00,
        'string_current': 5.00
    }
    try:
        data_id = generation_dao.insert(generation_data)
        print(f"添加发电数据ID: {data_id}")
    except Exception as e:
        print(f"添加发电数据失败: {e}")

    # 查询低效率设备
    try:
        abnormal = generation_dao.select_abnormal_efficiency(85.0)
        print(f"低效率设备数量: {len(abnormal)}")
    except Exception as e:
        print(f"查询低效率设备失败: {e}")

    print("=== 光伏发电数据功能测试完成 ===")


def test_pv_forecast():
    print("\n=== 测试光伏预测数据功能 ===")

    # 添加预测数据
    forecast_data = {
        'forecast_id': 'FC001',
        'device_id': 'PV001',
        'grid_point_id': 'GP001',
        'forecast_date': date(2024, 1, 15),
        'time_slot': '08:00-09:00',
        'forecast_generation': 30.00,
        'model_version': 'V1.0'
    }
    try:
        forecast_id = forecast_dao.insert(forecast_data)
        print(f"添加预测数据ID: {forecast_id}")
    except Exception as e:
        print(f"添加预测数据失败: {e}")

    # 更新偏差率
    try:
        forecast_dao.update_deviation_rate('FC001', 25.50)
        print("偏差率已更新")
    except Exception as e:
        print(f"更新偏差率失败: {e}")

    # 查询高偏差预测
    try:
        high_deviation = forecast_dao.select_high_deviation(15.0)
        print(f"高偏差预测数量: {len(high_deviation)}")
    except Exception as e:
        print(f"查询高偏差预测失败: {e}")

    print("=== 光伏预测数据功能测试完成 ===")

    # 综合测试所有功能


def run_all_tests():
    print("=" * 60)
    print("开始智慧能源管理系统DAO层测试")
    print("=" * 60)

    # 测试顺序：用户 → 设备 → 发电数据 → 预测数据
    try:
        test_user_operations()
        test_pv_device()
        test_pv_generation()
        test_pv_forecast()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()


# 运行测试
if __name__ == '__main__':
    run_all_tests()