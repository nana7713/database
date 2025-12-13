-- 回路异常数据视图
CREATE VIEW circuit_abnormal_view AS
SELECT 
    -- 基本信息
    c.substation_id AS '配电房编号',
    s.substation_name AS '配电房名称',
    p.plant_area_name AS '所属厂区',
    c.circuit_id AS '回路编号',
    DATE_FORMAT(c.collection_time, '%Y-%m-%d %H:%i') AS '采集时间',
    
    -- 回路监测数据
    c.voltage AS '电压(kV)',
    c.current AS '电流(A)',
    c.active_power AS '有功功率(kW)',
    c.reactive_power AS '无功功率(kVar)',
    c.power_factor AS '功率因数',
    c.switch_status AS '开关状态',
    
    -- 数据完整性检查
    CASE 
        WHEN c.voltage IS NULL OR c.current IS NULL THEN '数据不完整'
        ELSE '数据完整'
    END AS '数据完整性',
    
    -- 电压异常判断
    CASE 
        WHEN s.voltage_level = '35KV' AND c.voltage > 37.0 THEN '电压超限'
        WHEN s.voltage_level = '0.4KV' AND c.voltage > 0.44 THEN '电压超限' -- 0.4KV参考10%上限
        ELSE '电压正常'
    END AS '电压状态',
    
    -- 电流异常判断
    -- 假设阈值：35KV回路2000A，0.4KV回路3000A
    CASE 
        WHEN (s.voltage_level = '35KV' AND c.current > 2000) OR
             (s.voltage_level = '0.4KV' AND c.current > 3000) THEN '电流超限'
        ELSE '电流正常'
    END AS '电流状态',
    
    -- 综合异常状态
    CASE 
        WHEN c.voltage IS NULL OR c.current IS NULL THEN '数据不完整异常'
        WHEN (s.voltage_level = '35KV' AND c.voltage > 37.0) OR
             (s.voltage_level = '0.4KV' AND c.current > 3000) THEN '运行参数异常'
        ELSE '正常'
    END AS '异常状态',
    
    -- 异常等级
    CASE 
        WHEN c.voltage IS NULL OR c.current IS NULL THEN '低'
        WHEN (s.voltage_level = '35KV' AND c.voltage > 37.0) THEN '中'
        WHEN (s.voltage_level = '0.4KV' AND c.current > 3000) THEN '中'
        ELSE '正常'
    END AS '异常等级'
    
FROM circuit_monitoring_data c
JOIN substation s ON c.substation_id = s.substation_id
JOIN plant_area p ON s.plant_area_id = p.plant_area_id
-- 只显示异常数据
WHERE (
    -- 数据不完整
    c.voltage IS NULL OR c.current IS NULL
    -- 35KV电压超37KV
    OR (s.voltage_level = '35KV' AND c.voltage > 37.0)
    -- 电流超限
    OR (s.voltage_level = '35KV' AND c.current > 2000)
    OR (s.voltage_level = '0.4KV' AND c.current > 3000)
)
-- 最近24小时数据（运维常用时间范围）
AND c.collection_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY c.collection_time DESC;