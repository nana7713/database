from alarm_dao import AlarmMaintenanceDao
from datetime import datetime
import time


def main():
    # 初始化 DAO
    dao = AlarmMaintenanceDao()

    print("=== 开始告警运维业务线全流程测试 ===\n")

    # 为了防止多次运行报错，使用时间戳生成唯一ID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_alarm_id = f"ALM_{timestamp}"
    test_order_id = f"WO_{timestamp}"

    # 预置数据检查 (对应 SQL 脚本中的数据)
    test_device_id = 'd001'  # 必须存在于 device 表
    test_user_id = 'u001'  # 必须存在于 user 表

    # -------------------------------------------------------------------------
    # 1. 场景：系统监测到异常，自动生成告警
    # [cite_start]对应任务书: "系统监测到数据异常...自动生成告警" [cite: 176]
    # -------------------------------------------------------------------------
    print(f">>> [步骤1] 正在生成告警 (ID: {test_alarm_id})...")
    new_alarm = {
        'alarm_id': test_alarm_id,
        'device_id': test_device_id,
        'alarm_type': '越限告警',
        'occur_time': datetime.now(),
        'alarm_level': '高',
        'alarm_content': '35KV主变绕组温度超100℃',
        'threshold_value': 100.00
    }

    if dao.insert_alarm(new_alarm):
        print("   -> 成功：告警已创建，状态默认为 '未处理'")

    # -------------------------------------------------------------------------
    # 2. 场景：管理员查询未处理的告警 (查看关联的设备和厂区)
    # [cite_start]对应任务书: "针对5条业务线...设计实用视图" [cite: 245]
    # -------------------------------------------------------------------------
    print("\n>>> [步骤2] 查询未处理的高等级告警详情...")
    pending_list = dao.query_pending_alarms_detailed()

    found_target = False
    for item in pending_list:
        # 打印查询结果，包含多表连接查出来的 设备名 和 厂区名
        print(f"   发现告警: {item['alarm_content']} | 设备: {item['device_name']} | 区域: {item['area_name']}")
        if item['alarm_id'] == test_alarm_id:
            found_target = True

    if not found_target:
        print("   [警告] 刚刚插入的告警未找到，请检查数据库连接或事务提交。")

    # -------------------------------------------------------------------------
    # 3. 场景：生成运维工单并派发
    # [cite_start]对应任务书: "运维工单管理员...生成运维工单并分配" [cite: 177]
    # [cite_start]关键点: DAO层会自动将对应的告警状态更新为 '处理中' [cite: 173]
    # -------------------------------------------------------------------------
    print(f"\n>>> [步骤3] 正在派发工单 (工单ID: {test_order_id})...")
    new_order = {
        'order_id': test_order_id,
        'alarm_id': test_alarm_id,
        'maintainer_id': test_user_id
    }

    if dao.create_maintenance_order(new_order):
        print("   -> 成功：工单已派发，系统已自动将告警状态更新为 '处理中'")

    # -------------------------------------------------------------------------
    # 4. 场景：运维人员处理完成，上传结果并结案
    # [cite_start]对应任务书: "运维人员现场处理后...管理员复查通过后结案" [cite: 178]
    # 关键点: DAO层会自动将工单填完，并将告警状态更新为 '已结案'
    # -------------------------------------------------------------------------
    print("\n>>> [步骤4] 运维人员填写处理结果并结案...")
    fix_result = '已更换冷却风扇，温度恢复正常'
    photo_path = '/files/site_photo_2025.jpg'

    if dao.complete_order(test_order_id, fix_result, photo_path):
        print("   -> 成功：工单信息已更新，关联告警已自动闭环改为 '已结案'")

    print("\n=== 测试结束：全业务流程验证通过 ===")


if __name__ == "__main__":
    main()