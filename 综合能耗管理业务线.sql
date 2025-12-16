-- 1. 能耗计量设备信息表（关联plant_area、device）
CREATE TABLE energy_metering_equipment (
    equipment_id VARCHAR(20) PRIMARY KEY COMMENT '设备编号，唯一标识一台计量设备',
    energy_type VARCHAR(10) NOT NULL COMMENT '能源类型',
    installation_location VARCHAR(255) NOT NULL COMMENT '安装位置（如“VOCS下面”“糕饼一厂东北角”）',
    pipe_diameter VARCHAR(10) COMMENT '管径规格（如DN25、DN50、DN100）',
    communication_protocol VARCHAR(10) NOT NULL COMMENT '通讯协议',
    running_status VARCHAR(10) DEFAULT '正常' COMMENT '运行状态',
    calibration_cycle INT NOT NULL COMMENT '校准周期（月）',
    manufacturer VARCHAR(100) COMMENT '生产厂家',
    plant_area_id VARCHAR(20) NOT NULL COMMENT '所属厂区编号',
    -- 外键关联：归属厂区（关联plant_area）、设备台账（关联device）
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    FOREIGN KEY (equipment_id) REFERENCES device(device_id),
    -- 约束条件
    CONSTRAINT ck_energy_type_eme CHECK (energy_type IN ('水', '蒸汽', '天然气')),
    CONSTRAINT ck_comm_protocol_eme CHECK (communication_protocol IN ('RS485', 'Lora')),
    CONSTRAINT ck_running_status_eme CHECK (running_status IN ('正常', '故障')),
    CONSTRAINT ck_calibration_cycle_eme CHECK (calibration_cycle > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='能耗计量设备信息表';

-- 2. 能耗监测数据表（关联：energy_metering_equipment、plant_area）
CREATE TABLE energy_monitoring_data (
    data_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '数据编号，唯一标识一条监测数据',
    equipment_id VARCHAR(20) NOT NULL COMMENT '关联的能耗计量设备编号',
    collection_time DATETIME NOT NULL COMMENT '采集时间',
    energy_consumption DECIMAL(15,2) NOT NULL COMMENT '能耗值',
    unit VARCHAR(10) NOT NULL COMMENT '单位（水：m³；蒸汽：t；天然气：m³）',
    data_quality VARCHAR(4) NOT NULL COMMENT '数据质量',
    plant_area_id VARCHAR(20) NOT NULL COMMENT '所属厂区编号',
    verification_status VARCHAR(10) DEFAULT '已核实' COMMENT '核实状态',
    -- 外键关联：能耗计量设备、厂区
    FOREIGN KEY (equipment_id) REFERENCES energy_metering_equipment(equipment_id),
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    -- 唯一约束：防止同一设备同一时间重复采集数据
    UNIQUE uk_equipment_time (equipment_id, collection_time),
    -- 约束条件
    CONSTRAINT ck_energy_consumption_emd CHECK (energy_consumption >= 0),
    CONSTRAINT ck_unit_emd CHECK (unit IN ('m³', 't')),
    CONSTRAINT ck_data_quality_emd CHECK (data_quality IN ('优', '良', '中', '差')),
    CONSTRAINT ck_verification_status_emd CHECK (verification_status IN ('已核实', '待核实'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='能耗监测数据表';

-- 3. 峰谷能耗数据表（关联：plant_area、realtime_summary_data）
CREATE TABLE peak_valley_energy_data (
    record_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录编号，唯一标识一条峰谷能耗记录',
    energy_type VARCHAR(10) NOT NULL COMMENT '能源类型',
    plant_area_id VARCHAR(20) NOT NULL COMMENT '所属厂区编号',
    statistics_date DATE NOT NULL COMMENT '统计日期',
    peak_energy DECIMAL(15,2) NOT NULL COMMENT '尖峰时段能耗（单位：kWh/m³/t）',
    high_peak_energy DECIMAL(15,2) NOT NULL COMMENT '高峰时段能耗（单位：kWh/m³/t）',
    flat_energy DECIMAL(15,2) NOT NULL COMMENT '平段能耗（单位：kWh/m³/t）',
    valley_energy DECIMAL(15,2) NOT NULL COMMENT '低谷时段能耗（单位：kWh/m³/t）',
    total_energy DECIMAL(15,2) NOT NULL COMMENT '总能耗（单位：kWh/m³/t）',
    peak_valley_price DECIMAL(10,4) COMMENT '峰谷电价（元/kWh，仅电能有效）',
    energy_cost DECIMAL(15,2) NOT NULL COMMENT '能耗成本（元）',
    summary_id BIGINT COMMENT '关联实时汇总数据ID',
    -- 外键关联：厂区、实时汇总数据
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    FOREIGN KEY (summary_id) REFERENCES realtime_summary_data(summary_id),
    -- 唯一约束：同一厂区同一能源类型同一日期仅一条统计记录
    UNIQUE uk_plant_energy_date (plant_area_id, energy_type, statistics_date),
    -- 约束条件
    CONSTRAINT ck_energy_type_pved CHECK (energy_type IN ('水', '蒸汽', '天然气')),
    CONSTRAINT ck_peak_energy_pved CHECK (peak_energy >= 0),
    CONSTRAINT ck_high_peak_energy_pved CHECK (high_peak_energy >= 0),
    CONSTRAINT ck_flat_energy_pved CHECK (flat_energy >= 0),
    CONSTRAINT ck_valley_energy_pved CHECK (valley_energy >= 0),
    CONSTRAINT ck_total_energy_pved CHECK (total_energy = peak_energy + high_peak_energy + flat_energy + valley_energy),
    CONSTRAINT ck_peak_valley_price_pved CHECK (peak_valley_price >= 0 OR peak_valley_price IS NULL),
    CONSTRAINT ck_energy_cost_pved CHECK (energy_cost >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='峰谷能耗数据表';

-- 4. 能耗校准记录表（关联：energy_metering_equipment、user、calibration_record）
CREATE TABLE energy_calibration_record (
    record_id VARCHAR(20) PRIMARY KEY COMMENT '校准记录编号',
    equipment_id VARCHAR(20) NOT NULL COMMENT '关联能耗计量设备编号',
    calibrator_id VARCHAR(20) NOT NULL COMMENT '校准人员ID',
    calibration_time DATETIME NOT NULL COMMENT '校准时间',
    calibration_result VARCHAR(50) NOT NULL COMMENT '校准结果（合格/不合格/待复检）',
    calibration_notes TEXT COMMENT '校准备注',
    -- 外键关联：能耗计量设备、校准人员（关联user）、全局校准记录（关联calibration_record）
    FOREIGN KEY (equipment_id) REFERENCES energy_metering_equipment(equipment_id),
    FOREIGN KEY (calibrator_id) REFERENCES user(user_id),
    FOREIGN KEY (record_id) REFERENCES calibration_record(record_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='能耗计量设备校准记录表';