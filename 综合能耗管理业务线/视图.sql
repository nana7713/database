-- 视图 1：设备运行状态概览视图
-- 作用：供运维人员快速查看哪些能耗设备故障了
CREATE VIEW view_energy_device_status AS
SELECT 
    e.equipment_id,
    d.device_name,
    e.running_status,
    e.installation_location,
    p.plant_area_name
FROM 
    energy_metering_equipment e
JOIN 
    device d ON e.equipment_id = d.device_id
JOIN 
    plant_area p ON e.plant_area_id = p.plant_area_id;

-- 视图 2：待核实数据清单视图
-- 作用：供数据管理员每天上班查看，筛选出需要人工核实的数据
CREATE VIEW view_data_to_verify AS
SELECT 
    data_id,
    equipment_id,
    collection_time,
    energy_consumption,
    data_quality
FROM 
    energy_monitoring_data
WHERE 
    verification_status = '待核实' OR data_quality = '差';

-- 视图 3：能耗成本日报视图
-- 作用：供财务使用，只看钱，不看技术细节
CREATE VIEW view_daily_cost_report AS
SELECT 
    statistics_date,
    plant_area_id,
    SUM(energy_cost) AS total_daily_cost
FROM 
    peak_valley_energy_data
GROUP BY 
    statistics_date, plant_area_id;