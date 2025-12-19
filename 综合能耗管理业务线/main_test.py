from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from dao import EnergyManagementDAO
from datetime import datetime

# 1. 配置数据库连接 (请修改为你的实际账号密码)
# 格式: mysql+pymysql://用户名:密码@主机/数据库名
DATABASE_URL = "mysql+pymysql://root:password@localhost/energy_db"

# 创建引擎和会话
engine = create_engine(DATABASE_URL, echo=True) # echo=True 会打印生成的 SQL 语句，适合答辩演示
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 2. 实例化 DAO
dao = EnergyManagementDAO(session)

# 3. 测试：新增数据
try:
    print("--- 开始测试新增数据 ---")
    data_input = {
        'equipment_id': 'DEV_W001',  # 确保数据库里有这个设备
        'collection_time': datetime.now(),
        'energy_consumption': 150.55,
        'unit': 'm³',
        'data_quality': '优',
        'plant_area_id': 'AREA_01'
    }
    new_id = dao.add_monitoring_data(data_input)
    print(f"成功插入数据，ID: {new_id}")

    # 4. 测试：查询数据
    print("\n--- 开始测试按时间查询 ---")
    history_data = dao.get_data_by_time_range('DEV_W001', '2025-01-01', '2025-12-31')
    for d in history_data:
        print(f"时间: {d.collection_time}, 值: {d.energy_consumption}")

    # 5. 测试：核实异常数据
    print("\n--- 开始测试数据核实 ---")
    # 假设 ID 为 1 的数据需要核实
    if dao.verify_data(1):
        print("数据 ID 1 核实成功")

except Exception as e:
    session.rollback()
    print(f"发生错误: {e}")
finally:
    session.close()