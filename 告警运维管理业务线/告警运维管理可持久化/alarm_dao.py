from db_utils import get_connection
from datetime import datetime
import pymysql


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
        sql = """
        INSERT INTO alarm (
            alarm_id, device_id, alarm_type, occur_time, 
            alarm_level, alarm_content, status, threshold_value
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        conn = get_connection()
        if not conn: return False
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, (
                    alarm_data['alarm_id'],
                    alarm_data['device_id'],
                    alarm_data['alarm_type'],
                    alarm_data['occur_time'],
                    alarm_data['alarm_level'],
                    alarm_data['alarm_content'],
                    '未处理',  # 初始状态固定为未处理
                    alarm_data['threshold_value']
                ))
            conn.commit()
            print(f"[成功] 新增告警: {alarm_data['alarm_id']}")
            return True
        except pymysql.Error as e:
            conn.rollback()
            print(f"[失败] 新增告警数据库错误: {e}")
            return False
        finally:
            conn.close()

    def create_maintenance_order(self, order_data):
        """
        [新增 + 修改] 生成运维工单 (事务操作)
        说明: 插入工单的同时，必须将关联告警的状态改为 '处理中'
        """
        conn = get_connection()
        if not conn: return False
        try:
            # 开启事务
            conn.begin()
            with conn.cursor() as cursor:
                # 1. 插入工单记录
                sql_insert = """
                INSERT INTO maintenance_order (
                    order_id, alarm_id, maintainer_id, dispatch_time
                ) VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (
                    order_data['order_id'],
                    order_data['alarm_id'],
                    order_data['maintainer_id'],
                    datetime.now()
                ))

                # 2. 更新告警状态 (如果没有触发器，这里是必须的；即使有触发器，写在代码里也是双重保险)
                sql_update = "UPDATE alarm SET status = '处理中' WHERE alarm_id = %s"
                cursor.execute(sql_update, (order_data['alarm_id'],))

            conn.commit()
            print(f"[成功] 工单 {order_data['order_id']} 已派发，告警状态已更新")
            return True
        except pymysql.Error as e:
            conn.rollback()
            print(f"[失败] 派单事务回滚: {e}")
            return False
        finally:
            conn.close()

    # =========================================================================
    # 2. 查询 (Read)
    # =========================================================================

    def query_pending_alarms_detailed(self):
        """
        [查询] 获取详细的未处理告警列表 (多表连接查询)
        关联表: alarm -> device -> plant_area
        对应任务书: "覆盖不同业务场景...连接3个及以上关系" [cite: 231]
        """
        sql = """
        SELECT 
            a.alarm_id, 
            a.occur_time, 
            a.alarm_level, 
            a.alarm_content,
            d.device_name, 
            d.device_type,
            IFNULL(p.area_name, '未知区域') as area_name
        FROM alarm a
        JOIN device d ON a.device_id = d.device_id
        LEFT JOIN plant_area p ON d.plant_area_id = p.plant_area_id
        WHERE a.status = '未处理'
        ORDER BY a.alarm_level DESC, a.occur_time ASC
        """
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                return results
        finally:
            conn.close()

    def query_orders_by_maintainer(self, maintainer_id):
        """
        [查询] 查询某运维人员负责的所有工单
        对应任务书: "按设备编号查询运维工单" 类似的查询需求 [cite: 237]
        """
        sql = """
        SELECT mo.order_id, mo.dispatch_time, mo.finish_time, mo.result, 
               a.alarm_content 
        FROM maintenance_order mo
        JOIN alarm a ON mo.alarm_id = a.alarm_id
        WHERE mo.maintainer_id = %s
        ORDER BY mo.dispatch_time DESC
        """
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, (maintainer_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    # =========================================================================
    # 3. 修改 (Update)
    # =========================================================================

    def complete_order(self, order_id, result_text, attachment_path):
        """
        [修改] 运维人员完结工单
        对应任务书: "修改: 更新告警处理状态" [cite: 236]
        说明: 更新工单结果 + 更新告警状态为 '已结案'
        """
        conn = get_connection()
        if not conn: return False
        try:
            conn.begin()
            with conn.cursor() as cursor:
                # 1. 更新工单详情
                sql_order = """
                UPDATE maintenance_order 
                SET finish_time = %s, result = %s, attachment_path = %s 
                WHERE order_id = %s
                """
                cursor.execute(sql_order, (
                    datetime.now(),
                    result_text,
                    attachment_path,
                    order_id
                ))

                # 2. 查找关联的告警ID
                cursor.execute("SELECT alarm_id FROM maintenance_order WHERE order_id = %s", (order_id,))
                row = cursor.fetchone()

                # 3. 更新告警状态
                if row:
                    sql_alarm = "UPDATE alarm SET status = '已结案' WHERE alarm_id = %s"
                    cursor.execute(sql_alarm, (row['alarm_id'],))

            conn.commit()
            print(f"[成功] 工单 {order_id} 处理完成，闭环结束")
            return True
        except pymysql.Error as e:
            conn.rollback()
            print(f"[失败] 完结工单出错: {e}")
            return False
        finally:
            conn.close()

    # =========================================================================
    # 4. 删除 (Delete)
    # =========================================================================

    def delete_invalid_alarms(self):
        """
        [删除] 清理无效的测试数据或过期数据
        对应任务书: "删除: 删除过期告警记录/清理无效测试数据"
        """
        # 假设规则：删除 1 年前且已结案的告警
        sql = """
        DELETE FROM alarm 
        WHERE status = '已结案' 
        AND occur_time < DATE_SUB(NOW(), INTERVAL 1 YEAR)
        """
        conn = get_connection()
        if not conn: return False
        try:
            with conn.cursor() as cursor:
                rows = cursor.execute(sql)
            conn.commit()
            print(f"[成功] 已清理过期告警数据 {rows} 条")
            return True
        except pymysql.Error as e:
            conn.rollback()
            print(f"[失败] 删除数据出错: {e}")
            return False
        finally:
            conn.close()