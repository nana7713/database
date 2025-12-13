-- 配电房实时运行状态视图
CREATE VIEW substation_realtime_status_view AS
SELECT 
    s.substation_id AS '配电房编号',
    s.substation_name AS '配电房名称',
    p.plant_area_name AS '所属厂区',
    s.voltage_level AS '电压等级',
    s.transformer_count AS '变压器数量',
    s.commissioning_date AS '投运时间',
    u.full_name AS '负责人',
    
    -- 实时数据（最新5分钟）
    (SELECT COUNT(DISTINCT circuit_id) 
     FROM circuit_monitoring_data c
     WHERE c.substation_id = s.substation_id
     AND c.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) AS '在线回路数',
    
    (SELECT AVG(voltage)
     FROM circuit_monitoring_data c
     WHERE c.substation_id = s.substation_id
     AND c.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) AS '平均电压(kV)',
    
    (SELECT SUM(active_power)
     FROM circuit_monitoring_data c
     WHERE c.substation_id = s.substation_id
     AND c.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) AS '总有功功率(kW)',
    
    -- 变压器状态
    (SELECT COUNT(*)
     FROM transformer_monitoring_data t
     WHERE t.substation_id = s.substation_id
     AND t.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
     AND t.running_status = '异常') AS '异常变压器数',
    
    (SELECT AVG(load_rate)
     FROM transformer_monitoring_data t
     WHERE t.substation_id = s.substation_id
     AND t.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) AS '平均负载率(%)',
    
    -- 运行状态评估
    CASE 
        WHEN (SELECT COUNT(*) FROM transformer_monitoring_data t 
              WHERE t.substation_id = s.substation_id 
              AND t.running_status = '异常' 
              AND t.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) > 0 
        THEN '异常'
        WHEN (SELECT AVG(load_rate) FROM transformer_monitoring_data t 
              WHERE t.substation_id = s.substation_id 
              AND t.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) > 90 
        THEN '重载'
        WHEN (SELECT AVG(load_rate) FROM transformer_monitoring_data t 
              WHERE t.substation_id = s.substation_id 
              AND t.collection_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)) < 30 
        THEN '轻载'
        ELSE '正常'
    END AS '运行状态',
    
    -- 数据更新时间
    (SELECT MAX(collection_time) 
     FROM circuit_monitoring_data c
     WHERE c.substation_id = s.substation_id) AS '最后数据时间'

FROM substation s
JOIN plant_area p ON s.plant_area_id = p.plant_area_id
LEFT JOIN users u ON s.responsible_user_id = u.user_id
ORDER BY p.plant_area_name, s.substation_name;