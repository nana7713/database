-- 1. 能耗计量设备信息表
CREATE TABLE energy_metering_equipment (
    equipment_id VARCHAR(20) PRIMARY KEY COMMENT '设备编号，关联device主键',
    energy_type VARCHAR(10) NOT NULL COMMENT '能源类型：水/蒸汽/天然气',
    plant_area_id VARCHAR(20) NOT NULL COMMENT '所属厂区编号',
    installation_location VARCHAR(255) NOT NULL COMMENT '具体安装位置（如VOCS下面）',
    pipe_diameter VARCHAR(20) COMMENT '管径规格（如DN25）',
    communication_protocol VARCHAR(10) NOT NULL DEFAULT 'RS485' COMMENT '通讯协议',
    manufacturer VARCHAR(100) COMMENT '生产厂家',
    calibration_cycle INT DEFAULT 12 COMMENT '校准周期（月）',
    running_status VARCHAR(10) DEFAULT '正常' COMMENT '运行状态',
    
    -- 外部关联：核心握手点
    FOREIGN KEY (equipment_id) REFERENCES device(device_id) ON DELETE CASCADE,
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    
    -- 数据完整性约束
    CONSTRAINT ck_energy_type CHECK (energy_type IN ('水', '蒸汽', '天然气')),
    CONSTRAINT ck_protocol CHECK (communication_protocol IN ('RS485', 'Lora', 'NB-IoT')),
    CONSTRAINT ck_status CHECK (running_status IN ('正常', '故障', '离线'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='能耗计量设备扩展信息表';

-- 2. 能耗监测数据表
CREATE TABLE energy_monitoring_data (
    data_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    equipment_id VARCHAR(20) NOT NULL COMMENT '设备编号',
    plant_area_id VARCHAR(20) NOT NULL COMMENT '厂区编号（冗余字段）',
    collection_time DATETIME NOT NULL COMMENT '采集时间',
    energy_consumption DECIMAL(15,2) NOT NULL COMMENT '能耗数值',
    unit VARCHAR(10) NOT NULL COMMENT '单位（m³ 或 t）',
    data_quality VARCHAR(4) DEFAULT '优' COMMENT '数据质量',
    verification_status VARCHAR(10) DEFAULT '已核实' COMMENT '核实状态',
    
    -- 外部关联
    FOREIGN KEY (equipment_id) REFERENCES energy_metering_equipment(equipment_id),
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    
    -- 索引：极大提升按时间和设备查询的速度
    UNIQUE KEY uk_equip_time (equipment_id, collection_time),
    INDEX idx_time_area (collection_time, plant_area_id),
    
    -- 约束
    CONSTRAINT ck_quality CHECK (data_quality IN ('优', '良', '中', '差')),
    CONSTRAINT ck_verify CHECK (verification_status IN ('已核实', '待核实'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='能耗监测原始数据表';

-- 3. 峰谷能耗统计表
CREATE TABLE peak_valley_energy_data (
    record_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录编号',
    plant_area_id VARCHAR(20) NOT NULL COMMENT '厂区编号',
    energy_type VARCHAR(10) NOT NULL COMMENT '能源类型',
    statistics_date DATE NOT NULL COMMENT '统计日期',
    
    -- 能耗量字段 (使用默认值0防止NULL计算错误)
    peak_energy DECIMAL(15,2) DEFAULT 0.00 COMMENT '尖峰能耗',
    high_peak_energy DECIMAL(15,2) DEFAULT 0.00 COMMENT '高峰能耗',
    flat_energy DECIMAL(15,2) DEFAULT 0.00 COMMENT '平段能耗',
    valley_energy DECIMAL(15,2) DEFAULT 0.00 COMMENT '低谷能耗',
    total_energy DECIMAL(15,2) DEFAULT 0.00 COMMENT '总能耗',
    
    -- 成本字段
    peak_valley_price DECIMAL(10,4) COMMENT '当日综合电价/单价',
    energy_cost DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '总成本(元)',
    
    -- 外部关联
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    
    -- 约束：确保同一厂区同一天同种能源只有一条记录
    UNIQUE KEY uk_daily_stat (plant_area_id, energy_type, statistics_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='峰谷能耗日统计表';
