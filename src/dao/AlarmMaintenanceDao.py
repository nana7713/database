from base import db_manager
from datetime import datetime
from sqlalchemy import and_, or_, desc, asc, func
from models.alarm_models import Alarm, MaintenanceOrder, Device
from models.plant_area import PlantArea


class AlarmMaintenanceDao:
    """
    告警运维管理业务线 - 持久层核心实现
    涵盖表：alarm, maintenance_order, device, plant_area
    对应任务书章节：3.3 系统的数据库持久层设计工作
    """

    # =========================================================================
    # 1. 新增 (Create)
    # =========================================================================

    def insert_alarm(self, alarm_data):
        """
        [新增] 录入告警信息 (模拟设备自动上报)
        对应任务书: "新增: 录入能耗监测数据/添加设备" 类似的写入操作
        """
        with db_manager.get_session() as session:
            try:
                new_alarm = Alarm(
                    alarm_id=alarm_data['alarm_id'],
                    device_id=alarm_data['device_id'],
                    alarm_type=alarm_data['alarm_type'],
                    occur_time=alarm_data['occur_time'],
                    alarm_level=alarm_data['alarm_level'],
                    alarm_content=alarm_data['alarm_content'],
                    status='未处理',  # 初始状态固定为未处理
                    threshold_value=alarm_data['threshold_value']
                )
                session.add(new_alarm)
                session.commit()
                print(f"[成功] 新增告警: {alarm_data['alarm_id']}")
                return True
            except Exception as e:
                session.rollback()
                print(f"[失败] 新增告警数据库错误: {e}")
                return False

    def create_maintenance_order(self, order_data):
        """
        [新增 + 修改] 生成运维工单 (事务操作)
        说明: 插入工单的同时，必须将关联告警的状态改为 '处理中'
        """
        with db_manager.get_session() as session:
            try:
                # 1. 创建工单记录
                new_order = MaintenanceOrder(
                    order_id=order_data['order_id'],
                    alarm_id=order_data['alarm_id'],
                    maintainer_id=order_data['maintainer_id'],
                    dispatch_time=datetime.now()
                )
                session.add(new_order)

                # 2. 更新告警状态
                alarm = session.query(Alarm).filter_by(alarm_id=order_data['alarm_id']).first()
                if alarm:
                    alarm.status = '处理中'

                session.commit()
                print(f"[成功] 工单 {order_data['order_id']} 已派发，告警状态已更新")
                return True
            except Exception as e:
                session.rollback()
                print(f"[失败] 派单事务回滚: {e}")
                return False

    # =========================================================================
    # 2. 查询 (Read)
    # =========================================================================

    def query_all_alarms_detailed(self):
        """
        [查询] 获取所有告警信息 (多表连接查询)
        关联表: alarm -> device -> plant_area
        """
        with db_manager.get_session() as session:
            try:
                results = session.query(
                    Alarm.alarm_id,
                    Alarm.occur_time,
                    Alarm.alarm_level,
                    Alarm.alarm_content,
                    Alarm.status,
                    Device.device_name,
                    Device.device_type,
                    func.IFNULL(PlantArea.plant_area_name, '未知区域').label('area_name')
                ).join(
                    Device, Alarm.device_id == Device.device_id
                ).outerjoin(
                    PlantArea, Device.plant_area_id == PlantArea.plant_area_id
                ).order_by(
                    desc(Alarm.occur_time)
                ).all()
                
                # 转换为字典列表
                return [{
                    'alarm_id': result.alarm_id,
                    'occur_time': result.occur_time,
                    'alarm_level': result.alarm_level,
                    'alarm_content': result.alarm_content,
                    'status': result.status,
                    'device_name': result.device_name,
                    'device_type': result.device_type,
                    'area_name': result.area_name
                } for result in results]
            except Exception as e:
                print(f"[失败] 查询所有告警错误: {e}")
                return []

    def query_pending_alarms_detailed(self):
        """
        [查询] 获取详细的未处理告警列表 (多表连接查询)
        关联表: alarm -> device -> plant_area
        对应任务书: "覆盖不同业务场景...连接3个及以上关系" [cite: 231]
        """
        with db_manager.get_session() as session:
            try:
                results = session.query(
                    Alarm.alarm_id,
                    Alarm.occur_time,
                    Alarm.alarm_level,
                    Alarm.alarm_content,
                    Device.device_name,
                    Device.device_type,
                    func.IFNULL(PlantArea.plant_area_name, '未知区域').label('area_name')
                ).join(
                    Device, Alarm.device_id == Device.device_id
                ).outerjoin(
                    PlantArea, Device.plant_area_id == PlantArea.plant_area_id
                ).filter(
                    Alarm.status == '未处理'
                ).order_by(
                    desc(Alarm.alarm_level),
                    asc(Alarm.occur_time)
                ).all()
                
                # 转换为字典列表
                return [{
                    'alarm_id': result.alarm_id,
                    'occur_time': result.occur_time,
                    'alarm_level': result.alarm_level,
                    'alarm_content': result.alarm_content,
                    'device_name': result.device_name,
                    'device_type': result.device_type,
                    'area_name': result.area_name
                } for result in results]
            except Exception as e:
                print(f"[失败] 查询未处理告警错误: {e}")
                return []

    def query_orders_by_maintainer(self, maintainer_id):
        """
        [查询] 查询某运维人员负责的所有工单
        对应任务书: "按设备编号查询运维工单" 类似的查询需求 [cite: 237]
        """
        with db_manager.get_session() as session:
            try:
                results = session.query(
                    MaintenanceOrder.order_id,
                    MaintenanceOrder.dispatch_time,
                    MaintenanceOrder.finish_time,
                    MaintenanceOrder.result,
                    Alarm.alarm_content
                ).join(
                    Alarm, MaintenanceOrder.alarm_id == Alarm.alarm_id
                ).filter(
                    MaintenanceOrder.maintainer_id == maintainer_id
                ).order_by(
                    desc(MaintenanceOrder.dispatch_time)
                ).all()
                
                # 转换为字典列表
                return [{
                    'order_id': result.order_id,
                    'dispatch_time': result.dispatch_time,
                    'finish_time': result.finish_time,
                    'result': result.result,
                    'alarm_content': result.alarm_content
                } for result in results]
            except Exception as e:
                print(f"[失败] 查询运维人员工单错误: {e}")
                return []

    # =========================================================================
    # 3. 修改 (Update)
    # =========================================================================

    def handle_alarm(self, alarm_id):
        """
        [修改] 处理告警，直接将告警状态改为已处理
        """
        with db_manager.get_session() as session:
            try:
                # 更新告警状态
                alarm = session.query(Alarm).filter_by(alarm_id=alarm_id).first()
                if alarm:
                    alarm.status = '已处理'
                    session.commit()
                    print(f"[成功] 告警 {alarm_id} 处理完成")
                    return True
                return False
            except Exception as e:
                session.rollback()
                print(f"[失败] 处理告警出错: {e}")
                return False

    def complete_order(self, order_id, result_text, attachment_path):
        """
        [修改] 运维人员完结工单
        对应任务书: "修改: 更新告警处理状态" [cite: 236]
        说明: 更新工单结果 + 更新告警状态为 '已结案'
        """
        with db_manager.get_session() as session:
            try:
                # 1. 更新工单详情
                order = session.query(MaintenanceOrder).filter_by(order_id=order_id).first()
                if not order:
                    return False
                    
                order.finish_time = datetime.now()
                order.result = result_text
                order.attachment_path = attachment_path

                # 2. 更新关联的告警状态
                alarm = session.query(Alarm).filter_by(alarm_id=order.alarm_id).first()
                if alarm:
                    alarm.status = '已结案'

                session.commit()
                print(f"[成功] 工单 {order_id} 处理完成，闭环结束")
                return True
            except Exception as e:
                session.rollback()
                print(f"[失败] 完结工单出错: {e}")
                return False

    # =========================================================================
    # 4. 删除 (Delete)
    # =========================================================================

    def delete_invalid_alarms(self):
        """
        [删除] 清理无效的测试数据或过期数据
        对应任务书: "删除: 删除过期告警记录/清理无效测试数据"
        """
        # 假设规则：删除 1 年前且已结案的告警
        one_year_ago = datetime.now().replace(year=datetime.now().year - 1)
        
        with db_manager.get_session() as session:
            try:
                rows_deleted = session.query(Alarm).filter(
                    and_(
                        Alarm.status == '已结案',
                        Alarm.occur_time < one_year_ago
                    )
                ).delete()
                
                session.commit()
                print(f"[成功] 已清理过期告警数据 {rows_deleted} 条")
                return True
            except Exception as e:
                session.rollback()
                print(f"[失败] 删除数据出错: {e}")
                return False