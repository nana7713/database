-- 回路异常触发器

CREATE TRIGGER tr_circuit_abnormal_alert
AFTER INSERT ON circuit_monitoring_data
FOR EACH ROW
BEGIN
    DECLARE v_voltage_level VARCHAR(10);
    
    -- 获取电压等级
    SELECT voltage_level INTO v_voltage_level 
    FROM substation 
    WHERE substation_id = NEW.substation_id;
    
    -- 1. 数据不完整告警
    IF NEW.voltage IS NULL OR NEW.current IS NULL THEN
        INSERT INTO alert_info (
            alert_no, alert_type, related_device_no, 
            occur_time, alert_level, alert_content, 
            process_status
        ) VALUES (
            CONCAT('CD', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
            '数据异常',
            CONCAT('回路_', NEW.substation_id, '_', NEW.circuit_id),
            NEW.collection_time,
            '低',
            CONCAT('回路', NEW.circuit_id, '监测数据不完整'),
            '未处理'
        );
    
    -- 2. 35KV电压超37KV告警
    ELSEIF v_voltage_level = '35KV' AND NEW.voltage > 37.0 THEN
        INSERT INTO alert_info (
            alert_no, alert_type, related_device_no, 
            occur_time, alert_level, alert_content, 
            process_status, alert_threshold
        ) VALUES (
            CONCAT('CV', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
            '电压越限',
            CONCAT('回路_', NEW.substation_id, '_', NEW.circuit_id),
            NEW.collection_time,
            '中',
            CONCAT('35KV回路', NEW.circuit_id, '电压超限: ', 
                   ROUND(NEW.voltage, 2), 'KV > 37KV'),
            '未处理',
            '37.0 KV'
        );
    
    -- 3. 电流超限告警
    ELSEIF (v_voltage_level = '35KV' AND NEW.current > 2000) OR
           (v_voltage_level = '0.4KV' AND NEW.current > 3000) THEN
        INSERT INTO alert_info (
            alert_no, alert_type, related_device_no, 
            occur_time, alert_level, alert_content, 
            process_status, alert_threshold
        ) VALUES (
            CONCAT('CC', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
            '电流越限',
            CONCAT('回路_', NEW.substation_id, '_', NEW.circuit_id),
            NEW.collection_time,
            '中',
            CONCAT('回路', NEW.circuit_id, '电流超限: ', 
                   ROUND(NEW.current, 2), 'A'),
            '未处理',
            CASE 
                WHEN v_voltage_level = '35KV' THEN '2000A'
                WHEN v_voltage_level = '0.4KV' THEN '3000A'
            END
        );
    END IF;

END
