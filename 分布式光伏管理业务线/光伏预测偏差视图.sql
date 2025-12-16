CREATE OR REPLACE VIEW pv_forecast_deviation_view AS
SELECT 
    pf.forecast_id,
    pf.device_id,
    pd.device_type,
    pd.location,
    pf.grid_point_id,
    pf.forecast_date,
    pf.time_slot,
    pf.model_version,
    ROUND(pf.forecast_generation, 2) AS forecast_generation_kwh,
    ROUND(pf.actual_generation, 2) AS actual_generation_kwh,
    ROUND(pf.deviation_rate, 2) AS deviation_rate_percent,
    CASE 
        WHEN pf.deviation_rate IS NULL THEN '未计算'
        WHEN pf.deviation_rate <= 5 THEN '偏差很小(≤5%)'
        WHEN pf.deviation_rate <= 10 THEN '偏差较小(5-10%)'
        WHEN pf.deviation_rate <= 15 THEN '偏差中等(10-15%)'
        WHEN pf.deviation_rate <= 20 THEN '偏差较大(15-20%)'
        ELSE '偏差很大(>20%)'
    END AS deviation_level,
    CASE 
        WHEN pf.deviation_rate > 15 THEN '需要优化'
        WHEN pf.deviation_rate > 10 THEN '建议关注'
        ELSE '模型良好'
    END AS model_evaluation,
    COALESCE(pg.collect_time, NULL) AS actual_collect_time,
    COALESCE(pg.inverter_efficiency, NULL) AS actual_inverter_efficiency
FROM 
    pv_forecast pf
LEFT JOIN 
    pv_device pd ON pf.device_id = pd.device_id
LEFT JOIN 
    pv_generation pg ON pf.actual_data_id = pg.data_id
WHERE 
    pf.forecast_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)  -- 只显示最近30天的预测
ORDER BY 
    pf.forecast_date DESC, 
    IF(pf.deviation_rate IS NULL, 1, 0),
    pf.deviation_rate DESC,
    pd.location ASC;