DELIMITER //

CREATE TRIGGER trg_auto_verify_status
BEFORE INSERT ON energy_monitoring_data
FOR EACH ROW
BEGIN
    -- 如果插入的数据质量是 '差' 或 '中'
    IF NEW.data_quality IN ('差', '中') THEN
        -- 强制将核实状态设为 '待核实'
        SET NEW.verification_status = '待核实';
    ELSE
        -- 否则默认为 '已核实'
        SET NEW.verification_status = '已核实';
    END IF;
END;
//

DELIMITER ;