CREATE TRIGGER trigger_pv_forecast_update_deviation
AFTER UPDATE ON pv_forecast
FOR EACH ROW
BEGIN
    DECLARE v_alarm_id VARCHAR(20);
    DECLARE v_alarm_content VARCHAR(500);
    
    -- 检查偏差率是否从<=15%变为>15%
    IF (OLD.deviation_rate <= 15.00 OR OLD.deviation_rate IS NULL) 
       AND NEW.deviation_rate > 15.00 THEN
        
        -- 生成告警ID
        SET v_alarm_id = CONCAT('ALARM', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), LPAD(FLOOR(RAND()*1000), 3, '0'));
        
        -- 构建告警内容
        SET v_alarm_content = CONCAT(
            '光伏预测偏差率更新后超过15%：预测编号', 
            NEW.forecast_id, 
            '，设备编号', 
            NEW.device_id, 
            '，原偏差率', 
            IFNULL(OLD.deviation_rate, 'NULL'), 
            '%，新偏差率', 
            NEW.deviation_rate, 
            '%，超出阈值。请检查预测模型并进行优化。'
        );
        
        -- 插入告警信息
        INSERT INTO alarm_info (
            alarm_id,
            alarm_type,
            related_device_id,
            alarm_time,
            alarm_level,
            alarm_content,
            status,
            trigger_threshold
        ) VALUES (
            v_alarm_id,
            '预测模型优化提醒',
            NEW.device_id,
            NOW(),
            '中',
            v_alarm_content,
            '未处理',
            15.00
        );
    END IF;
END