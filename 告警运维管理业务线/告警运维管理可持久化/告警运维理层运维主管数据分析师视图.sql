-- =========================================================
-- 视图 1：待处理高危告警视图 (View_Critical_Pending_Alarms)
-- 适用角色：企业管理层、运维主管
-- 业务价值：跨越厂区和设备表，直接筛选出最紧急、需要立即关注的告警。
-- =========================================================
CREATE OR REPLACE VIEW view_critical_pending_alarms AS
SELECT 
    a.alarm_id,
    a.occur_time,
    p.area_name AS '所属厂区',
    d.device_name AS '设备名称',
    a.alarm_type AS '告警类型',
    a.alarm_content AS '告警内容',
    a.threshold_value AS '触发阈值'
FROM alarm a
JOIN device d ON a.device_id = d.device_id
LEFT JOIN plant_area p ON d.plant_area_id = p.plant_area_id
WHERE a.status = '未处理' AND a.alarm_level = '高';

-- =========================================================
-- 视图 2：运维人员工作量统计视图 (View_Maintainer_Workload)
-- 适用角色：运维主管
-- 业务价值：统计每位运维人员的接单数量和完成数量，用于绩效考核。
-- =========================================================
CREATE OR REPLACE VIEW view_maintainer_workload AS
SELECT 
    u.user_id,
    u.username AS '运维人员姓名',
    COUNT(mo.order_id) AS '总工单数',
    SUM(CASE WHEN mo.finish_time IS NOT NULL THEN 1 ELSE 0 END) AS '已完成工单数',
    MAX(mo.dispatch_time) AS '最近一次派单时间'
FROM user u
LEFT JOIN maintenance_order mo ON u.user_id = mo.maintainer_id
WHERE u.role = '运维人员'
GROUP BY u.user_id, u.username;

-- =========================================================
-- 3. 厂区设备故障率排行视图 (View_Plant_Failure_Stats)
-- 适用角色：数据分析师、能源管理员
-- 业务价值：统计各厂区的告警总数，帮助识别哪个厂区设备老化严重或环境恶劣。
-- =========================================================
CREATE OR REPLACE VIEW view_plant_failure_stats AS
SELECT 
    p.area_name AS '厂区名称',
    COUNT(d.device_id) AS '设备总数',
    COUNT(a.alarm_id) AS '产生告警总数',
    ROUND(COUNT(a.alarm_id) / COUNT(d.device_id), 2) AS '平均单机故障数'
FROM plant_area p
JOIN device d ON p.plant_area_id = d.plant_area_id
LEFT JOIN alarm a ON d.device_id = a.device_id
GROUP BY p.plant_area_id, p.area_name
ORDER BY COUNT(a.alarm_id) DESC;