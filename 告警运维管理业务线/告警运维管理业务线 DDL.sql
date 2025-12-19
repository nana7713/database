CREATE DATABASE smart_energy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE smart_energy_db;

-- =========================================================
-- 2. 全局基础表构建 (支撑所有业务线)
-- =========================================================

-- 2.1 厂区表 (能耗业务线依赖此表)
CREATE TABLE plant_area (
    plant_area_id VARCHAR(20) PRIMARY KEY COMMENT '厂区编号',
    area_name VARCHAR(50) NOT NULL COMMENT '厂区名称',
    location_desc VARCHAR(200) COMMENT '位置描述'
) COMMENT='厂区信息表';

-- 2.2 用户表 (全局人员信息)
CREATE TABLE user (
    user_id VARCHAR(20) PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '姓名',
    department VARCHAR(50) COMMENT '部门',
    contact_info VARCHAR(100) COMMENT '联系方式',
    role VARCHAR(30) NOT NULL COMMENT '角色: 运维人员/系统管理员/能源管理员/数据分析师'
) COMMENT='用户信息表';

-- 2.3 设备台账主表 (所有业务线的父表)
-- 光伏设备、能耗设备都应在此表有基础记录，通过 device_id 关联扩展信息
CREATE TABLE device (
    device_id VARCHAR(20) PRIMARY KEY COMMENT '设备编号',
    plant_area_id VARCHAR(20) COMMENT '所属厂区',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_category VARCHAR(50) NOT NULL COMMENT '大类: 光伏/能耗/配电',
    device_type VARCHAR(50) COMMENT '具体类型: 逆变器/水表/变压器',
    model_spec VARCHAR(100) COMMENT '型号规格',
    install_date DATE COMMENT '安装日期',
    warranty_period VARCHAR(30) COMMENT '质保期',
    is_scrapped BOOLEAN DEFAULT 0 COMMENT '是否报废: 0否 1是',
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id)
) COMMENT='设备台账主表';

-- =========================================================
-- 3. 告警运维业务线核心表
-- =========================================================

-- 3.1 告警信息表
CREATE TABLE alarm (
    alarm_id VARCHAR(30) PRIMARY KEY COMMENT '告警编号',
    device_id VARCHAR(20) NOT NULL COMMENT '关联设备',
    alarm_type VARCHAR(50) COMMENT '类型: 越限/故障/离线',
    occur_time DATETIME NOT NULL COMMENT '发生时间',
    alarm_level VARCHAR(20) NOT NULL COMMENT '等级: 高/中/低',
    alarm_content TEXT COMMENT '详细内容',
    status VARCHAR(20) DEFAULT '未处理' COMMENT '状态: 未处理/处理中/已结案',
    threshold_value DECIMAL(10,2) COMMENT '触发时的阈值',
    FOREIGN KEY (device_id) REFERENCES device(device_id) ON DELETE CASCADE
) COMMENT='告警信息表';

-- 3.2 运维工单表
CREATE TABLE maintenance_order (
    order_id VARCHAR(30) PRIMARY KEY COMMENT '工单编号',
    alarm_id VARCHAR(30) NOT NULL COMMENT '关联告警',
    maintainer_id VARCHAR(20) NOT NULL COMMENT '运维人员ID',
    dispatch_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '派单时间',
    response_time DATETIME COMMENT '响应时间',
    finish_time DATETIME COMMENT '完成时间',
    result TEXT COMMENT '处理结果',
    recheck_status VARCHAR(20) COMMENT '复查状态: 通过/未通过',
    attachment_path VARCHAR(255) COMMENT '现场附件路径',
    FOREIGN KEY (alarm_id) REFERENCES alarm(alarm_id) ON DELETE CASCADE,
    FOREIGN KEY (maintainer_id) REFERENCES user(user_id)
) COMMENT='运维工单表';

-- 3.3 校准记录表
CREATE TABLE calibration_record (
    record_id VARCHAR(30) PRIMARY KEY COMMENT '记录编号',
    device_id VARCHAR(20) NOT NULL COMMENT '设备编号',
    calibrator_id VARCHAR(20) NOT NULL COMMENT '校准人员ID',
    calibration_time DATETIME NOT NULL COMMENT '校准时间',
    next_calibration_date DATE COMMENT '下次校准日期',
    FOREIGN KEY (device_id) REFERENCES device(device_id) ON DELETE CASCADE,
    FOREIGN KEY (calibrator_id) REFERENCES user(user_id)
) COMMENT='设备校准记录表';

-- =========================================================
-- 4. 预置基础测试数据 (防止外键报错)
-- =========================================================
INSERT INTO plant_area VALUES ('AREA_01', '一号厂区', '东侧工业园');
INSERT INTO user VALUES ('u001', '张工', '运维部', '13800000000', '运维人员');
INSERT INTO device VALUES ('d001', 'AREA_01', '1#逆变器', '光伏', '逆变器', 'SG110CX', '2024-01-01', '5年', 0);