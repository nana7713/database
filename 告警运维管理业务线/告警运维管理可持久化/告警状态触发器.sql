-- =========================================================
-- 触发器：派单后自动更新告警状态
-- 触发时机：当 maintenance_order 表插入新记录之后 (AFTER INSERT)
-- 执行逻辑：将对应的 alarm 表记录状态改为 '处理中'
-- =========================================================
DELIMITER $$

CREATE TRIGGER trg_auto_update_alarm_status
AFTER INSERT ON maintenance_order
FOR EACH ROW
BEGIN
    -- NEW.alarm_id 代表刚刚插入工单表的那条记录里的 alarm_id
    UPDATE alarm 
    SET status = '处理中' 
    WHERE alarm_id = NEW.alarm_id;
END$$

DELIMITER ;