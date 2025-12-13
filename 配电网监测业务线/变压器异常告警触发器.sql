-- 变压器异常关联告警触发器

CREATE TRIGGER tr_transformer_abnormal_alert
AFTER INSERT ON transformer_monitoring_data
FOR EACH ROW
BEGIN
    DECLARE v_substation_name VARCHAR(100);
    DECLARE v_plant_area_name VARCHAR(100);
    DECLARE v_circuit_count INT;
    DECLARE v_circuit_list TEXT;
    
    -- 只有当状态为异常时才触发
    IF NEW.running_status = '异常' THEN
    
        -- 获取配电房信息
        SELECT s.substation_name, p.plant_area_name 
        INTO v_substation_name, v_plant_area_name
        FROM substation s
        JOIN plant_area p ON s.plant_area_id = p.plant_area_id
        WHERE s.substation_id = NEW.substation_id;
        
        -- 获取关联回路信息（最近5分钟内的回路）
        SELECT 
            COUNT(DISTINCT c.circuit_id),
            GROUP_CONCAT(DISTINCT c.circuit_id)
        INTO v_circuit_count, v_circuit_list
        FROM circuit_monitoring_data c
        WHERE c.substation_id = NEW.substation_id
        AND c.collection_time >= DATE_SUB(NEW.collection_time, INTERVAL 5 MINUTE)
        AND c.collection_time <= NEW.collection_time;
        
        -- 1. 变压器本身告警
        INSERT INTO alert_info (
            alert_no, alert_type, related_device_no, 
            occur_time, alert_level, alert_content, 
            process_status
        ) VALUES (
            CONCAT('TA', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
            '变压器异常',
            CONCAT('变压器_', NEW.transformer_id),
            NEW.collection_time,
            '高',
            CONCAT('变压器', NEW.transformer_id, '运行异常，',
                   '负载率', ROUND(NEW.load_rate, 1), '%，',
                   '绕组温度', ROUND(NEW.winding_temp, 1), '℃'),
            '未处理'
        );
        
        -- 2. 关联告警：影响相关回路
        IF v_circuit_count > 0 THEN
            INSERT INTO alert_info (
                alert_no, alert_type, related_device_no, 
                occur_time, alert_level, alert_content, 
                process_status
            ) VALUES (
                CONCAT('CA', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
                '关联影响告警',
                CONCAT('配电房_', NEW.substation_id),
                NEW.collection_time,
                CASE 
                    WHEN NEW.load_rate > 90 THEN '紧急'
                    WHEN NEW.winding_temp > 100 THEN '紧急'
                    ELSE '高'
                END,
                CONCAT(v_plant_area_name, '-', v_substation_name, 
                       '变压器', NEW.transformer_id, '异常，',
                       '影响', v_circuit_count, '个回路(', v_circuit_list, ')'),
                '未处理'
            );
        END IF;
        

    END IF;
END
