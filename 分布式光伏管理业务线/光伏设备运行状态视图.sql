CREATE OR REPLACE VIEW pv_device_operation_status_view AS
SELECT 
    pd.device_id,
    pd.device_type,
    pd.location,
    ROUND(pd.capacity, 2) AS capacity_kwp,
    pd.operation_date,
    pd.calibration_cycle,
    pd.status AS device_status,
    pd.protocol,
    -- 最近一次发电数据
    MAX(pg.collect_time) AS last_collect_time,
    ROUND(COALESCE(MAX(pg.generation), 0), 2) AS last_generation_kwh,
    ROUND(COALESCE(MAX(pg.inverter_efficiency), 0), 2) AS last_efficiency_percent,
    -- 当日发电统计
    ROUND(COALESCE(SUM(CASE WHEN DATE(pg.collect_time) = CURDATE() THEN pg.generation ELSE 0 END), 0), 2) AS today_generation_kwh,
    -- 当月发电统计
    ROUND(COALESCE(SUM(CASE WHEN MONTH(pg.collect_time) = MONTH(CURDATE()) 
         AND YEAR(pg.collect_time) = YEAR(CURDATE()) 
         THEN pg.generation ELSE 0 END)), 2) AS month_generation_kwh,
    -- 效率分析
    CASE 
        WHEN COALESCE(AVG(pg.inverter_efficiency), 0) >= 90 THEN '效率优秀'
        WHEN COALESCE(AVG(pg.inverter_efficiency), 0) >= 85 THEN '效率良好'
        WHEN COALESCE(AVG(pg.inverter_efficiency), 0) >= 80 THEN '效率一般'
        WHEN COALESCE(AVG(pg.inverter_efficiency), 0) > 0 THEN '效率较低'
        ELSE '无效率数据'
    END AS efficiency_evaluation,
    -- 维护需求分析
    CASE 
        WHEN pd.status = '故障' THEN '需立即维修'
        WHEN pd.status = '离线' THEN '需检查通讯'
        WHEN TIMESTAMPDIFF(MONTH, pd.operation_date, CURDATE()) >= pd.calibration_cycle THEN '需校准'
        WHEN COALESCE(AVG(pg.inverter_efficiency), 0) < 85 THEN '需效率检查'
        WHEN TIMESTAMPDIFF(HOUR, MAX(pg.collect_time), NOW()) > 24 THEN '数据采集异常'
        ELSE '运行正常'
    END AS maintenance_need,
    -- 运行时长
    TIMESTAMPDIFF(MONTH, pd.operation_date, CURDATE()) AS operation_months,
    -- 最近一次校准时间
    DATE_ADD(pd.operation_date, INTERVAL pd.calibration_cycle MONTH) AS next_calibration_date,
    -- 设备利用率（当日发电量/装机容量）
    ROUND(
        COALESCE(SUM(CASE WHEN DATE(pg.collect_time) = CURDATE() THEN pg.generation ELSE 0 END), 0) / 
        NULLIF(pd.capacity, 0) * 100, 2
    ) AS today_utilization_rate
FROM 
    pv_device pd
LEFT JOIN 
    pv_generation pg ON pd.device_id = pg.device_id AND pg.collect_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY 
    pd.device_id, pd.device_type, pd.location, pd.capacity, pd.operation_date, 
    pd.calibration_cycle, pd.status, pd.protocol
ORDER BY 
    maintenance_need DESC,
    device_status DESC,
    today_generation_kwh DESC;