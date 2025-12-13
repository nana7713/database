-- 变压器异常视图
CREATE VIEW transformer_abnormal_view AS
SELECT 
    t.substation_id AS '配电房编号',
    s.substation_name AS '配电房名称',
    p.plant_area_name AS '所属厂区',
    t.transformer_id AS '变压器编号',
    DATE_FORMAT(t.collection_time, '%Y-%m-%d %H:%i') AS '采集时间',
    
    -- 变压器数据
    t.load_rate AS '负载率(%)',
    t.winding_temp AS '绕组温度(℃)',
    t.core_temp AS '铁芯温度(℃)',
    t.ambient_temp AS '环境温度(℃)',
    t.ambient_humidity AS '环境湿度(%)',
    t.running_status AS '运行状态',
    
    -- 可能的异常原因分析
    CASE 
        WHEN t.winding_temp > 100 THEN '绕组温度过高'
        WHEN t.core_temp > 95 THEN '铁芯温度过高'
        WHEN t.load_rate > 100 THEN '过载运行'
        WHEN t.running_status = '异常' THEN '其他异常'
        ELSE '正常'
    END AS '异常原因'

FROM transformer_monitoring_data t
JOIN substation s ON t.substation_id = s.substation_id
JOIN plant_area p ON s.plant_area_id = p.plant_area_id
WHERE t.running_status = '异常'  
AND t.collection_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY t.collection_time DESC;