CREATE OR REPLACE VIEW pv_daily_generation_view AS
SELECT 
    DATE(pg.collect_time) AS generation_date,
    pd.device_type,
    pd.location,
    COUNT(DISTINCT pd.device_id) AS device_count,
    SUM(pd.capacity) AS total_capacity_kwp,
    ROUND(SUM(pg.generation), 2) AS total_generation_kwh,
    ROUND(SUM(pg.feed_in), 2) AS total_feed_in_kwh,
    ROUND(SUM(pg.self_use), 2) AS total_self_use_kwh,
    ROUND(AVG(pg.inverter_efficiency), 2) AS avg_inverter_efficiency_percent,
    ROUND(SUM(pg.self_use) / NULLIF(SUM(pg.generation), 0) * 100, 2) AS self_use_rate_percent,
    CASE 
        WHEN SUM(pg.generation) > 0 THEN '正常发电'
        ELSE '无发电数据'
    END AS generation_status
FROM 
    pv_generation pg
JOIN 
    pv_device pd ON pg.device_id = pd.device_id
WHERE 
    pd.status = '正常'  -- 只统计正常运行的设备
GROUP BY 
    DATE(pg.collect_time), pd.device_type, pd.location
ORDER BY 
    generation_date DESC, total_generation_kwh DESC;