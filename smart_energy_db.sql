/*
 Navicat Premium Dump SQL

 Source Server         : JAVAWEB
 Source Server Type    : MySQL
 Source Server Version : 80044 (8.0.44)
 Source Host           : localhost:3306
 Source Schema         : smart_energy_db

 Target Server Type    : MySQL
 Target Server Version : 80044 (8.0.44)
 File Encoding         : 65001

 Date: 26/12/2025 18:09:04
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alarm
-- ----------------------------
DROP TABLE IF EXISTS `alarm`;
CREATE TABLE `alarm`  (
  `alarm_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '告警编号',
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '关联设备',
  `alarm_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '类型: 越限/故障/离线',
  `occur_time` datetime NOT NULL COMMENT '发生时间',
  `alarm_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '等级: 高/中/低',
  `alarm_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '详细内容',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '未处理' COMMENT '状态: 未处理/处理中/已结案',
  `threshold_value` decimal(10, 2) NULL DEFAULT NULL COMMENT '触发时的阈值',
  PRIMARY KEY (`alarm_id`) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  CONSTRAINT `alarm_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '告警信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for calibration_record
-- ----------------------------
DROP TABLE IF EXISTS `calibration_record`;
CREATE TABLE `calibration_record`  (
  `record_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '记录编号',
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备编号',
  `calibrator_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '校准人员ID',
  `calibration_time` datetime NOT NULL COMMENT '校准时间',
  `next_calibration_date` date NULL DEFAULT NULL COMMENT '下次校准日期',
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  INDEX `calibrator_id`(`calibrator_id` ASC) USING BTREE,
  CONSTRAINT `calibration_record_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `calibration_record_ibfk_2` FOREIGN KEY (`calibrator_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '设备校准记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for circuit_monitoring_data
-- ----------------------------
DROP TABLE IF EXISTS `circuit_monitoring_data`;
CREATE TABLE `circuit_monitoring_data`  (
  `circuit_data_id` bigint NOT NULL AUTO_INCREMENT,
  `substation_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `circuit_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `collection_time` datetime NOT NULL,
  `voltage` decimal(10, 2) NULL DEFAULT NULL COMMENT '单位: kV',
  `current` decimal(10, 2) NULL DEFAULT NULL COMMENT '单位: A',
  `active_power` decimal(10, 2) NULL DEFAULT NULL COMMENT '单位: kW',
  `reactive_power` decimal(10, 2) NULL DEFAULT NULL COMMENT '单位：kVar',
  `power_factor` decimal(3, 2) NULL DEFAULT NULL,
  `forward_active_energy` decimal(15, 2) NULL DEFAULT NULL COMMENT '单位：kWh',
  `reverse_active_energy` decimal(15, 2) NULL DEFAULT NULL COMMENT '单位：kWh',
  `switch_status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `cable_temp` decimal(5, 2) NULL DEFAULT NULL COMMENT '单位：℃',
  `capacitor_temp` decimal(5, 2) NULL DEFAULT NULL COMMENT '单位：℃',
  PRIMARY KEY (`circuit_data_id`) USING BTREE,
  UNIQUE INDEX `uk_circuit_time`(`substation_id` ASC, `circuit_id` ASC, `collection_time` ASC) USING BTREE,
  CONSTRAINT `circuit_monitoring_data_ibfk_1` FOREIGN KEY (`substation_id`) REFERENCES `substation` (`substation_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `circuit_monitoring_data_chk_1` CHECK ((`power_factor` < 1) and (`power_factor` > -(1))),
  CONSTRAINT `circuit_monitoring_data_chk_2` CHECK (`switch_status` in (_utf8mb4'分闸',_utf8mb4'合闸'))
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for dashboard_config
-- ----------------------------
DROP TABLE IF EXISTS `dashboard_config`;
CREATE TABLE `dashboard_config`  (
  `config_id` bigint NOT NULL AUTO_INCREMENT COMMENT '配置编号',
  `display_module` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '展示模块',
  `refresh_frequency` int NOT NULL COMMENT '数据刷新频率(秒)',
  `display_fields` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '展示字段',
  `sorting_rule` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '排序规则',
  `permission_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '权限等级',
  PRIMARY KEY (`config_id`) USING BTREE,
  CONSTRAINT `chk_display_module` CHECK (`display_module` in (_utf8mb4'能源总览',_utf8mb4'光伏总览',_utf8mb4'配电网运行状态',_utf8mb4'告警统计')),
  CONSTRAINT `chk_permission_level` CHECK (`permission_level` in (_utf8mb4'管理员',_utf8mb4'能源管理员',_utf8mb4'运维人员')),
  CONSTRAINT `chk_sorting_rule` CHECK (`sorting_rule` in (_utf8mb4'按时间降序',_utf8mb4'按能耗降序'))
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '大屏展示配置表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for data_quality_issues
-- ----------------------------
DROP TABLE IF EXISTS `data_quality_issues`;
CREATE TABLE `data_quality_issues`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `table_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `record_id` bigint NOT NULL,
  `issue_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `create_time` datetime NOT NULL,
  `resolved_time` datetime NULL DEFAULT NULL,
  `status` enum('OPEN','IN_PROGRESS','RESOLVED') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'OPEN',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for device
-- ----------------------------
DROP TABLE IF EXISTS `device`;
CREATE TABLE `device`  (
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备编号',
  `plant_area_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所属厂区',
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备名称',
  `device_category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '大类: 光伏/能耗/配电',
  `device_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '具体类型: 逆变器/水表/变压器',
  `model_spec` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '型号规格',
  `install_date` date NULL DEFAULT NULL COMMENT '安装日期',
  `warranty_period` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '质保期',
  `is_scrapped` tinyint(1) NULL DEFAULT 0 COMMENT '是否报废: 0否 1是',
  PRIMARY KEY (`device_id`) USING BTREE,
  INDEX `plant_area_id`(`plant_area_id` ASC) USING BTREE,
  CONSTRAINT `device_ibfk_1` FOREIGN KEY (`plant_area_id`) REFERENCES `plant_area` (`plant_area_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '设备台账主表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for energy_metering_equipment
-- ----------------------------
DROP TABLE IF EXISTS `energy_metering_equipment`;
CREATE TABLE `energy_metering_equipment`  (
  `equipment_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备编号',
  `energy_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '能源类型',
  `plant_area_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '所属厂区',
  `installation_location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '安装位置',
  `pipe_diameter` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '管径规格',
  `communication_protocol` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '通讯协议',
  `running_status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '运行状态',
  `calibration_cycle` int NOT NULL COMMENT '校准周期(月)',
  `manufacturer` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '生产厂家',
  PRIMARY KEY (`equipment_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for energy_monitoring_data
-- ----------------------------
DROP TABLE IF EXISTS `energy_monitoring_data`;
CREATE TABLE `energy_monitoring_data`  (
  `data_id` int NOT NULL AUTO_INCREMENT COMMENT '数据编号',
  `equipment_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `collection_time` datetime NOT NULL COMMENT '采集时间',
  `energy_consumption` decimal(15, 2) NOT NULL COMMENT '能耗值',
  `unit` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '单位',
  `data_quality` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '数据质量',
  `plant_area_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '冗余厂区ID',
  `verification_status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '核实状态',
  PRIMARY KEY (`data_id`) USING BTREE,
  INDEX `equipment_id`(`equipment_id` ASC) USING BTREE,
  CONSTRAINT `energy_monitoring_data_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `energy_metering_equipment` (`equipment_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for historical_trend_data
-- ----------------------------
DROP TABLE IF EXISTS `historical_trend_data`;
CREATE TABLE `historical_trend_data`  (
  `trend_id` bigint NOT NULL AUTO_INCREMENT COMMENT '趋势编号',
  `energy_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '能源类型',
  `statistical_cycle` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '统计周期',
  `statistical_date` date NOT NULL COMMENT '统计时间',
  `energy_value` decimal(15, 2) NOT NULL COMMENT '能耗/发电量数值',
  `yoy_growth_rate` decimal(5, 2) NULL DEFAULT NULL COMMENT '同比增长率(%)',
  `mom_growth_rate` decimal(5, 2) NULL DEFAULT NULL COMMENT '环比增长率(%)',
  `industry_average` decimal(15, 2) NULL DEFAULT NULL COMMENT '行业均值',
  PRIMARY KEY (`trend_id`) USING BTREE,
  CONSTRAINT `chk_energy_type` CHECK (`energy_type` in (_utf8mb4'电',_utf8mb4'水',_utf8mb4'蒸汽',_utf8mb4'天然气',_utf8mb4'光伏')),
  CONSTRAINT `chk_statistical_cycle` CHECK (`statistical_cycle` in (_utf8mb4'日',_utf8mb4'周',_utf8mb4'月'))
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '历史趋势数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for maintenance_order
-- ----------------------------
DROP TABLE IF EXISTS `maintenance_order`;
CREATE TABLE `maintenance_order`  (
  `order_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工单编号',
  `alarm_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '关联告警',
  `maintainer_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '运维人员ID',
  `dispatch_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '派单时间',
  `response_time` datetime NULL DEFAULT NULL COMMENT '响应时间',
  `finish_time` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `result` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '处理结果',
  `recheck_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '复查状态: 通过/未通过',
  `attachment_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '现场附件路径',
  PRIMARY KEY (`order_id`) USING BTREE,
  INDEX `alarm_id`(`alarm_id` ASC) USING BTREE,
  INDEX `maintainer_id`(`maintainer_id` ASC) USING BTREE,
  CONSTRAINT `maintenance_order_ibfk_1` FOREIGN KEY (`alarm_id`) REFERENCES `alarm` (`alarm_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `maintenance_order_ibfk_2` FOREIGN KEY (`maintainer_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '运维工单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for peak_valley_energy_data
-- ----------------------------
DROP TABLE IF EXISTS `peak_valley_energy_data`;
CREATE TABLE `peak_valley_energy_data`  (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `energy_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `plant_area_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `statistics_date` date NOT NULL,
  `peak_energy` decimal(15, 2) NULL DEFAULT NULL,
  `high_peak_energy` decimal(15, 2) NULL DEFAULT NULL,
  `flat_energy` decimal(15, 2) NULL DEFAULT NULL,
  `valley_energy` decimal(15, 2) NULL DEFAULT NULL,
  `total_energy` decimal(15, 2) NOT NULL,
  `peak_valley_price` decimal(10, 4) NULL DEFAULT NULL,
  `energy_cost` decimal(15, 2) NOT NULL,
  PRIMARY KEY (`record_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for plant_area
-- ----------------------------
DROP TABLE IF EXISTS `plant_area`;
CREATE TABLE `plant_area`  (
  `plant_area_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `plant_area_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location_desc` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `manager_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`plant_area_id`) USING BTREE,
  UNIQUE INDEX `plant_area_name`(`plant_area_name` ASC) USING BTREE,
  INDEX `manager_id`(`manager_id` ASC) USING BTREE,
  CONSTRAINT `plant_area_ibfk_1` FOREIGN KEY (`manager_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for pv_device
-- ----------------------------
DROP TABLE IF EXISTS `pv_device`;
CREATE TABLE `pv_device`  (
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `device_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `capacity` decimal(8, 2) NOT NULL,
  `operation_date` date NOT NULL,
  `calibration_cycle` int NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `protocol` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`device_id`) USING BTREE,
  CONSTRAINT `pv_device_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `pv_device_chk_1` CHECK (`device_type` in (_utf8mb4'逆变器',_utf8mb4'汇流箱')),
  CONSTRAINT `pv_device_chk_2` CHECK (`status` in (_utf8mb4'正常',_utf8mb4'故障',_utf8mb4'离线')),
  CONSTRAINT `pv_device_chk_3` CHECK (`protocol` in (_utf8mb4'RS485',_utf8mb4'Lora'))
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for pv_forecast
-- ----------------------------
DROP TABLE IF EXISTS `pv_forecast`;
CREATE TABLE `pv_forecast`  (
  `forecast_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `grid_point_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `forecast_date` date NOT NULL,
  `time_slot` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `forecast_generation` decimal(10, 2) NOT NULL,
  `actual_data_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `actual_generation` decimal(10, 2) NULL DEFAULT NULL,
  `deviation_rate` decimal(5, 2) NULL DEFAULT NULL,
  `model_version` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`forecast_id`) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  INDEX `actual_data_id`(`actual_data_id` ASC) USING BTREE,
  CONSTRAINT `pv_forecast_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `pv_device` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `pv_forecast_ibfk_2` FOREIGN KEY (`actual_data_id`) REFERENCES `pv_generation` (`data_id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for pv_generation
-- ----------------------------
DROP TABLE IF EXISTS `pv_generation`;
CREATE TABLE `pv_generation`  (
  `data_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `grid_point_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `collect_time` datetime NOT NULL,
  `generation` decimal(10, 2) NOT NULL,
  `feed_in` decimal(10, 2) NOT NULL,
  `self_use` decimal(10, 2) NOT NULL,
  `inverter_efficiency` decimal(5, 2) NULL DEFAULT NULL,
  `string_voltage` decimal(8, 2) NULL DEFAULT NULL,
  `string_current` decimal(8, 2) NULL DEFAULT NULL,
  PRIMARY KEY (`data_id`) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  CONSTRAINT `pv_generation_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `pv_device` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for realtime_summary_data
-- ----------------------------
DROP TABLE IF EXISTS `realtime_summary_data`;
CREATE TABLE `realtime_summary_data`  (
  `summary_id` bigint NOT NULL AUTO_INCREMENT COMMENT '汇总编号',
  `statistics_time` datetime NOT NULL COMMENT '统计时间',
  `total_electricity` decimal(15, 2) NULL DEFAULT NULL COMMENT '总用电量(kWh)',
  `total_water` decimal(15, 2) NULL DEFAULT NULL COMMENT '总用水量(m³)',
  `total_steam` decimal(15, 2) NULL DEFAULT NULL COMMENT '总蒸汽消耗量(t)',
  `total_gas` decimal(15, 2) NULL DEFAULT NULL COMMENT '总天然气消耗量(m³)',
  `pv_total_generation` decimal(15, 2) NULL DEFAULT NULL COMMENT '光伏总发电量(kWh)',
  `pv_self_use` decimal(15, 2) NULL DEFAULT NULL COMMENT '光伏自用电量(kWh)',
  `total_alarms` int NULL DEFAULT NULL COMMENT '总告警次数',
  `high_level_alarms` int NULL DEFAULT NULL COMMENT '高等级告警数',
  `medium_level_alarms` int NULL DEFAULT NULL COMMENT '中等级告警数',
  `low_level_alarms` int NULL DEFAULT NULL COMMENT '低等级告警数',
  PRIMARY KEY (`summary_id`) USING BTREE,
  UNIQUE INDEX `statistics_time`(`statistics_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '实时汇总数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `role_id` int NOT NULL,
  `role_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `role_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`role_id`) USING BTREE,
  UNIQUE INDEX `role_code`(`role_code` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for substation
-- ----------------------------
DROP TABLE IF EXISTS `substation`;
CREATE TABLE `substation`  (
  `substation_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `plant_area_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `substation_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `substation_location_desc` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `voltage_level` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `transformer_count` int NULL DEFAULT 0,
  `commissioning_date` date NULL DEFAULT NULL,
  `responsible_user_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`substation_id`) USING BTREE,
  INDEX `plant_area_id`(`plant_area_id` ASC) USING BTREE,
  INDEX `responsible_user_id`(`responsible_user_id` ASC) USING BTREE,
  CONSTRAINT `substation_ibfk_1` FOREIGN KEY (`plant_area_id`) REFERENCES `plant_area` (`plant_area_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `substation_ibfk_2` FOREIGN KEY (`responsible_user_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for system_notifications
-- ----------------------------
DROP TABLE IF EXISTS `system_notifications`;
CREATE TABLE `system_notifications`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `message_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `priority` enum('LOW','MEDIUM','HIGH','URGENT') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `create_time` datetime NOT NULL,
  `status` enum('PENDING','SENT','READ') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'PENDING',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for transformer_monitoring_data
-- ----------------------------
DROP TABLE IF EXISTS `transformer_monitoring_data`;
CREATE TABLE `transformer_monitoring_data`  (
  `transformer_data_id` bigint NOT NULL AUTO_INCREMENT,
  `substation_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `transformer_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `collection_time` datetime NOT NULL,
  `load_rate` decimal(5, 2) NULL DEFAULT NULL,
  `winding_temp` decimal(5, 2) NULL DEFAULT NULL COMMENT '单位：℃',
  `core_temp` decimal(5, 2) NULL DEFAULT NULL COMMENT '单位：℃',
  `ambient_temp` decimal(5, 2) NULL DEFAULT NULL COMMENT '单位：℃',
  `ambient_humidity` decimal(5, 2) NULL DEFAULT NULL COMMENT '单位：%',
  `running_status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`transformer_data_id`) USING BTREE,
  UNIQUE INDEX `uk_transformer_time`(`substation_id` ASC, `transformer_id` ASC, `collection_time` ASC) USING BTREE,
  CONSTRAINT `transformer_monitoring_data_ibfk_1` FOREIGN KEY (`substation_id`) REFERENCES `substation` (`substation_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `transformer_monitoring_data_chk_1` CHECK (`load_rate` >= 0),
  CONSTRAINT `transformer_monitoring_data_chk_2` CHECK (`running_status` in (_utf8mb4'正常',_utf8mb4'异常'))
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_roles
-- ----------------------------
DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles`  (
  `user_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for circuit_abnormal_view
-- ----------------------------
DROP VIEW IF EXISTS `circuit_abnormal_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `circuit_abnormal_view` AS select `c`.`substation_id` AS `配电房编号`,`s`.`substation_name` AS `配电房名称`,`p`.`plant_area_name` AS `所属厂区`,`c`.`circuit_id` AS `回路编号`,date_format(`c`.`collection_time`,'%Y-%m-%d %H:%i') AS `采集时间`,`c`.`voltage` AS `电压(kV)`,`c`.`current` AS `电流(A)`,`c`.`active_power` AS `有功功率(kW)`,`c`.`reactive_power` AS `无功功率(kVar)`,`c`.`power_factor` AS `功率因数`,`c`.`switch_status` AS `开关状态`,(case when ((`c`.`voltage` is null) or (`c`.`current` is null)) then '数据不完整' else '数据完整' end) AS `数据完整性`,(case when ((`s`.`voltage_level` = '35KV') and (`c`.`voltage` > 37.0)) then '电压超限' when ((`s`.`voltage_level` = '0.4KV') and (`c`.`voltage` > 0.44)) then '电压超限' else '电压正常' end) AS `电压状态`,(case when (((`s`.`voltage_level` = '35KV') and (`c`.`current` > 2000)) or ((`s`.`voltage_level` = '0.4KV') and (`c`.`current` > 3000))) then '电流超限' else '电流正常' end) AS `电流状态`,(case when ((`c`.`voltage` is null) or (`c`.`current` is null)) then '数据不完整异常' when (((`s`.`voltage_level` = '35KV') and (`c`.`voltage` > 37.0)) or ((`s`.`voltage_level` = '0.4KV') and (`c`.`current` > 3000))) then '运行参数异常' else '正常' end) AS `异常状态`,(case when ((`c`.`voltage` is null) or (`c`.`current` is null)) then '低' when ((`s`.`voltage_level` = '35KV') and (`c`.`voltage` > 37.0)) then '中' when ((`s`.`voltage_level` = '0.4KV') and (`c`.`current` > 3000)) then '中' else '正常' end) AS `异常等级` from ((`circuit_monitoring_data` `c` join `substation` `s` on((`c`.`substation_id` = `s`.`substation_id`))) join `plant_area` `p` on((`s`.`plant_area_id` = `p`.`plant_area_id`))) where (((`c`.`voltage` is null) or (`c`.`current` is null) or ((`s`.`voltage_level` = '35KV') and (`c`.`voltage` > 37.0)) or ((`s`.`voltage_level` = '35KV') and (`c`.`current` > 2000)) or ((`s`.`voltage_level` = '0.4KV') and (`c`.`current` > 3000))) and (`c`.`collection_time` >= (now() - interval 24 hour))) order by `c`.`collection_time` desc;

-- ----------------------------
-- View structure for pv_daily_generation_view
-- ----------------------------
DROP VIEW IF EXISTS `pv_daily_generation_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `pv_daily_generation_view` AS select cast(`pg`.`collect_time` as date) AS `generation_date`,`pd`.`device_type` AS `device_type`,`pd`.`location` AS `location`,count(distinct `pd`.`device_id`) AS `device_count`,sum(`pd`.`capacity`) AS `total_capacity_kwp`,round(sum(`pg`.`generation`),2) AS `total_generation_kwh`,round(sum(`pg`.`feed_in`),2) AS `total_feed_in_kwh`,round(sum(`pg`.`self_use`),2) AS `total_self_use_kwh`,round(avg(`pg`.`inverter_efficiency`),2) AS `avg_inverter_efficiency_percent`,round(((sum(`pg`.`self_use`) / nullif(sum(`pg`.`generation`),0)) * 100),2) AS `self_use_rate_percent`,(case when (sum(`pg`.`generation`) > 0) then '正常发电' else '无发电数据' end) AS `generation_status` from (`pv_generation` `pg` join `pv_device` `pd` on((`pg`.`device_id` = `pd`.`device_id`))) where (`pd`.`status` = '正常') group by cast(`pg`.`collect_time` as date),`pd`.`device_type`,`pd`.`location` order by `generation_date` desc,`total_generation_kwh` desc;

-- ----------------------------
-- View structure for pv_device_operation_status_view
-- ----------------------------
DROP VIEW IF EXISTS `pv_device_operation_status_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `pv_device_operation_status_view` AS select `pd`.`device_id` AS `device_id`,`pd`.`device_type` AS `device_type`,`pd`.`location` AS `location`,round(`pd`.`capacity`,2) AS `capacity_kwp`,`pd`.`operation_date` AS `operation_date`,`pd`.`calibration_cycle` AS `calibration_cycle`,`pd`.`status` AS `device_status`,`pd`.`protocol` AS `protocol`,max(`pg`.`collect_time`) AS `last_collect_time`,round(coalesce(max(`pg`.`generation`),0),2) AS `last_generation_kwh`,round(coalesce(max(`pg`.`inverter_efficiency`),0),2) AS `last_efficiency_percent`,round(coalesce(sum((case when (cast(`pg`.`collect_time` as date) = curdate()) then `pg`.`generation` else 0 end)),0),2) AS `today_generation_kwh`,round(coalesce(sum((case when ((month(`pg`.`collect_time`) = month(curdate())) and (year(`pg`.`collect_time`) = year(curdate()))) then `pg`.`generation` else 0 end))),2) AS `month_generation_kwh`,(case when (coalesce(avg(`pg`.`inverter_efficiency`),0) >= 90) then '效率优秀' when (coalesce(avg(`pg`.`inverter_efficiency`),0) >= 85) then '效率良好' when (coalesce(avg(`pg`.`inverter_efficiency`),0) >= 80) then '效率一般' when (coalesce(avg(`pg`.`inverter_efficiency`),0) > 0) then '效率较低' else '无效率数据' end) AS `efficiency_evaluation`,(case when (`pd`.`status` = '故障') then '需立即维修' when (`pd`.`status` = '离线') then '需检查通讯' when (timestampdiff(MONTH,`pd`.`operation_date`,curdate()) >= `pd`.`calibration_cycle`) then '需校准' when (coalesce(avg(`pg`.`inverter_efficiency`),0) < 85) then '需效率检查' when (timestampdiff(HOUR,max(`pg`.`collect_time`),now()) > 24) then '数据采集异常' else '运行正常' end) AS `maintenance_need`,timestampdiff(MONTH,`pd`.`operation_date`,curdate()) AS `operation_months`,(`pd`.`operation_date` + interval `pd`.`calibration_cycle` month) AS `next_calibration_date`,round(((coalesce(sum((case when (cast(`pg`.`collect_time` as date) = curdate()) then `pg`.`generation` else 0 end)),0) / nullif(`pd`.`capacity`,0)) * 100),2) AS `today_utilization_rate` from (`pv_device` `pd` left join `pv_generation` `pg` on(((`pd`.`device_id` = `pg`.`device_id`) and (`pg`.`collect_time` >= (curdate() - interval 30 day))))) group by `pd`.`device_id`,`pd`.`device_type`,`pd`.`location`,`pd`.`capacity`,`pd`.`operation_date`,`pd`.`calibration_cycle`,`pd`.`status`,`pd`.`protocol` order by `maintenance_need` desc,`device_status` desc,`today_generation_kwh` desc;

-- ----------------------------
-- View structure for pv_forecast_deviation_view
-- ----------------------------
DROP VIEW IF EXISTS `pv_forecast_deviation_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `pv_forecast_deviation_view` AS select `pf`.`forecast_id` AS `forecast_id`,`pf`.`device_id` AS `device_id`,`pd`.`device_type` AS `device_type`,`pd`.`location` AS `location`,`pf`.`grid_point_id` AS `grid_point_id`,`pf`.`forecast_date` AS `forecast_date`,`pf`.`time_slot` AS `time_slot`,`pf`.`model_version` AS `model_version`,round(`pf`.`forecast_generation`,2) AS `forecast_generation_kwh`,round(`pf`.`actual_generation`,2) AS `actual_generation_kwh`,round(`pf`.`deviation_rate`,2) AS `deviation_rate_percent`,(case when (`pf`.`deviation_rate` is null) then '未计算' when (`pf`.`deviation_rate` <= 5) then '偏差很小(≤5%)' when (`pf`.`deviation_rate` <= 10) then '偏差较小(5-10%)' when (`pf`.`deviation_rate` <= 15) then '偏差中等(10-15%)' when (`pf`.`deviation_rate` <= 20) then '偏差较大(15-20%)' else '偏差很大(>20%)' end) AS `deviation_level`,(case when (`pf`.`deviation_rate` > 15) then '需要优化' when (`pf`.`deviation_rate` > 10) then '建议关注' else '模型良好' end) AS `model_evaluation`,coalesce(`pg`.`collect_time`,NULL) AS `actual_collect_time`,coalesce(`pg`.`inverter_efficiency`,NULL) AS `actual_inverter_efficiency` from ((`pv_forecast` `pf` left join `pv_device` `pd` on((`pf`.`device_id` = `pd`.`device_id`))) left join `pv_generation` `pg` on((`pf`.`actual_data_id` = `pg`.`data_id`))) where (`pf`.`forecast_date` >= (curdate() - interval 30 day)) order by `pf`.`forecast_date` desc,if((`pf`.`deviation_rate` is null),1,0),`pf`.`deviation_rate` desc,`pd`.`location`;

-- ----------------------------
-- View structure for substation_realtime_status_view
-- ----------------------------
DROP VIEW IF EXISTS `substation_realtime_status_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `substation_realtime_status_view` AS select `s`.`substation_id` AS `配电房编号`,`s`.`substation_name` AS `配电房名称`,`p`.`plant_area_name` AS `所属厂区`,`s`.`voltage_level` AS `电压等级`,`s`.`transformer_count` AS `变压器数量`,`s`.`commissioning_date` AS `投运时间`,`u`.`full_name` AS `负责人`,(select count(distinct `c`.`circuit_id`) from `circuit_monitoring_data` `c` where ((`c`.`substation_id` = `s`.`substation_id`) and (`c`.`collection_time` >= (now() - interval 5 minute)))) AS `在线回路数`,(select avg(`c`.`voltage`) from `circuit_monitoring_data` `c` where ((`c`.`substation_id` = `s`.`substation_id`) and (`c`.`collection_time` >= (now() - interval 5 minute)))) AS `平均电压(kV)`,(select sum(`c`.`active_power`) from `circuit_monitoring_data` `c` where ((`c`.`substation_id` = `s`.`substation_id`) and (`c`.`collection_time` >= (now() - interval 5 minute)))) AS `总有功功率(kW)`,(select count(0) from `transformer_monitoring_data` `t` where ((`t`.`substation_id` = `s`.`substation_id`) and (`t`.`collection_time` >= (now() - interval 5 minute)) and (`t`.`running_status` = '异常'))) AS `异常变压器数`,(select avg(`t`.`load_rate`) from `transformer_monitoring_data` `t` where ((`t`.`substation_id` = `s`.`substation_id`) and (`t`.`collection_time` >= (now() - interval 5 minute)))) AS `平均负载率(%)`,(case when ((select count(0) from `transformer_monitoring_data` `t` where ((`t`.`substation_id` = `s`.`substation_id`) and (`t`.`running_status` = '异常') and (`t`.`collection_time` >= (now() - interval 5 minute)))) > 0) then '异常' when ((select avg(`t`.`load_rate`) from `transformer_monitoring_data` `t` where ((`t`.`substation_id` = `s`.`substation_id`) and (`t`.`collection_time` >= (now() - interval 5 minute)))) > 90) then '重载' when ((select avg(`t`.`load_rate`) from `transformer_monitoring_data` `t` where ((`t`.`substation_id` = `s`.`substation_id`) and (`t`.`collection_time` >= (now() - interval 5 minute)))) < 30) then '轻载' else '正常' end) AS `运行状态`,(select max(`c`.`collection_time`) from `circuit_monitoring_data` `c` where (`c`.`substation_id` = `s`.`substation_id`)) AS `最后数据时间` from ((`substation` `s` join `plant_area` `p` on((`s`.`plant_area_id` = `p`.`plant_area_id`))) left join `users` `u` on((`s`.`responsible_user_id` = `u`.`user_id`))) order by `p`.`plant_area_name`,`s`.`substation_name`;

-- ----------------------------
-- View structure for transformer_abnormal_view
-- ----------------------------
DROP VIEW IF EXISTS `transformer_abnormal_view`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `transformer_abnormal_view` AS select `t`.`substation_id` AS `配电房编号`,`s`.`substation_name` AS `配电房名称`,`p`.`plant_area_name` AS `所属厂区`,`t`.`transformer_id` AS `变压器编号`,date_format(`t`.`collection_time`,'%Y-%m-%d %H:%i') AS `采集时间`,`t`.`load_rate` AS `负载率(%)`,`t`.`winding_temp` AS `绕组温度(℃)`,`t`.`core_temp` AS `铁芯温度(℃)`,`t`.`ambient_temp` AS `环境温度(℃)`,`t`.`ambient_humidity` AS `环境湿度(%)`,`t`.`running_status` AS `运行状态`,(case when (`t`.`winding_temp` > 100) then '绕组温度过高' when (`t`.`core_temp` > 95) then '铁芯温度过高' when (`t`.`load_rate` > 100) then '过载运行' when (`t`.`running_status` = '异常') then '其他异常' else '正常' end) AS `异常原因` from ((`transformer_monitoring_data` `t` join `substation` `s` on((`t`.`substation_id` = `s`.`substation_id`))) join `plant_area` `p` on((`s`.`plant_area_id` = `p`.`plant_area_id`))) where ((`t`.`running_status` = '异常') and (`t`.`collection_time` >= (now() - interval 24 hour))) order by `t`.`collection_time` desc;

-- ----------------------------
-- View structure for v_alarm_statistics
-- ----------------------------
DROP VIEW IF EXISTS `v_alarm_statistics`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_alarm_statistics` AS select cast(`rs`.`statistics_time` as date) AS `统计日期`,`rs`.`high_level_alarms` AS `高等级告警数`,`rs`.`medium_level_alarms` AS `中等级告警数`,`rs`.`low_level_alarms` AS `低等级告警数`,`rs`.`total_alarms` AS `总告警数`,(case when (`rs`.`total_alarms` > 0) then round(((`rs`.`high_level_alarms` / `rs`.`total_alarms`) * 100),2) else 0 end) AS `高等级告警占比`,(case when (`rs`.`total_alarms` > lag(`rs`.`total_alarms`,1) OVER (ORDER BY cast(`rs`.`statistics_time` as date) ) ) then '告警上升' when (`rs`.`total_alarms` < lag(`rs`.`total_alarms`,1) OVER (ORDER BY cast(`rs`.`statistics_time` as date) ) ) then '告警下降' else '告警平稳' end) AS `告警趋势`,(select `htd`.`yoy_growth_rate` from `historical_trend_data` `htd` where ((`htd`.`energy_type` = '电') and (`htd`.`statistical_cycle` = '日') and (`htd`.`statistical_date` = (cast(`rs`.`statistics_time` as date) - interval 1 year)))) AS `去年同期增长率` from `realtime_summary_data` `rs` where (`rs`.`statistics_time` = (select max(`rs2`.`statistics_time`) from `realtime_summary_data` `rs2` where (cast(`rs2`.`statistics_time` as date) = cast(`rs`.`statistics_time` as date)))) order by `rs`.`statistics_time` desc;

-- ----------------------------
-- View structure for v_energy_overview
-- ----------------------------
DROP VIEW IF EXISTS `v_energy_overview`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_energy_overview` AS select `rs`.`statistics_time` AS `统计时间`,`rs`.`total_electricity` AS `总用电量`,`rs`.`total_water` AS `总用水量`,`rs`.`total_steam` AS `总蒸汽量`,`rs`.`total_gas` AS `总天然气量`,`rs`.`pv_total_generation` AS `光伏总发电量`,`rs`.`pv_self_use` AS `光伏自用电量`,`rs`.`total_alarms` AS `总告警数`,`rs`.`high_level_alarms` AS `高等级告警数`,`rs`.`medium_level_alarms` AS `中等级告警数`,`rs`.`low_level_alarms` AS `低等级告警数`,(case when (`rs`.`pv_total_generation` > 0) then round(((`rs`.`pv_self_use` / `rs`.`pv_total_generation`) * 100),2) else 0 end) AS `光伏自用率`,(case when (`rs`.`total_electricity` > (select avg(`realtime_summary_data`.`total_electricity`) from `realtime_summary_data` where (`realtime_summary_data`.`statistics_time` >= (now() - interval 7 day)))) then '能耗上升' else '能耗正常' end) AS `用电状态` from `realtime_summary_data` `rs` where (`rs`.`statistics_time` >= (now() - interval 1 day)) order by `rs`.`statistics_time` desc;

-- ----------------------------
-- View structure for v_pv_analysis
-- ----------------------------
DROP VIEW IF EXISTS `v_pv_analysis`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_pv_analysis` AS select cast(`rs`.`statistics_time` as date) AS `统计日期`,hour(`rs`.`statistics_time`) AS `时段`,avg(`rs`.`pv_total_generation`) AS `平均发电量`,avg(`rs`.`pv_self_use`) AS `平均自用电量`,max(`rs`.`pv_total_generation`) AS `最大发电量`,min(`rs`.`pv_total_generation`) AS `最小发电量`,(case when (max(`rs`.`pv_total_generation`) > 0) then round(((avg(`rs`.`pv_total_generation`) / max(`rs`.`pv_total_generation`)) * 100),2) else 0 end) AS `平均发电效率`,count(0) AS `数据点数` from `realtime_summary_data` `rs` where ((`rs`.`pv_total_generation` is not null) and (`rs`.`statistics_time` >= (now() - interval 30 day))) group by cast(`rs`.`statistics_time` as date),hour(`rs`.`statistics_time`) having (count(0) >= 10);

-- ----------------------------
-- View structure for view_critical_pending_alarms
-- ----------------------------
DROP VIEW IF EXISTS `view_critical_pending_alarms`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `view_critical_pending_alarms` AS select `a`.`alarm_id` AS `alarm_id`,`a`.`occur_time` AS `occur_time`,`p`.`plant_area_name` AS `所属厂区`,`d`.`device_name` AS `设备名称`,`a`.`alarm_type` AS `告警类型`,`a`.`alarm_content` AS `告警内容`,`a`.`threshold_value` AS `触发阈值` from ((`alarm` `a` join `device` `d` on((`a`.`device_id` = `d`.`device_id`))) left join `plant_area` `p` on((`d`.`plant_area_id` = `p`.`plant_area_id`))) where ((`a`.`status` = '未处理') and (`a`.`alarm_level` = '高'));

-- ----------------------------
-- View structure for view_daily_cost_report
-- ----------------------------
DROP VIEW IF EXISTS `view_daily_cost_report`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `view_daily_cost_report` AS select `peak_valley_energy_data`.`statistics_date` AS `statistics_date`,`peak_valley_energy_data`.`plant_area_id` AS `plant_area_id`,sum(`peak_valley_energy_data`.`energy_cost`) AS `total_daily_cost` from `peak_valley_energy_data` group by `peak_valley_energy_data`.`statistics_date`,`peak_valley_energy_data`.`plant_area_id`;

-- ----------------------------
-- View structure for view_data_to_verify
-- ----------------------------
DROP VIEW IF EXISTS `view_data_to_verify`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `view_data_to_verify` AS select `energy_monitoring_data`.`data_id` AS `data_id`,`energy_monitoring_data`.`equipment_id` AS `equipment_id`,`energy_monitoring_data`.`collection_time` AS `collection_time`,`energy_monitoring_data`.`energy_consumption` AS `energy_consumption`,`energy_monitoring_data`.`data_quality` AS `data_quality` from `energy_monitoring_data` where ((`energy_monitoring_data`.`verification_status` = '待核实') or (`energy_monitoring_data`.`data_quality` = '差'));

-- ----------------------------
-- View structure for view_energy_device_status
-- ----------------------------
DROP VIEW IF EXISTS `view_energy_device_status`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `view_energy_device_status` AS select `e`.`equipment_id` AS `equipment_id`,`d`.`device_name` AS `device_name`,`e`.`running_status` AS `running_status`,`e`.`installation_location` AS `installation_location`,`p`.`plant_area_name` AS `plant_area_name` from ((`energy_metering_equipment` `e` join `device` `d` on((`e`.`equipment_id` = `d`.`device_id`))) join `plant_area` `p` on((`e`.`plant_area_id` = `p`.`plant_area_id`)));

-- ----------------------------
-- Procedure structure for sp_generate_daily_report
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_generate_daily_report`;
delimiter ;;
CREATE PROCEDURE `sp_generate_daily_report`(IN report_date DATE)
BEGIN
    DECLARE total_electricity_today DECIMAL(15,2);
    DECLARE total_electricity_yesterday DECIMAL(15,2);
    DECLARE yoy_growth_rate DECIMAL(5,2);
    DECLARE mom_growth_rate DECIMAL(5,2);
    
    -- 获取当日总用电量
    SELECT COALESCE(SUM(total_electricity), 0) INTO total_electricity_today
    FROM realtime_summary_data 
    WHERE DATE(statistics_time) = report_date;
    
    -- 获取昨日总用电量（环比）
    SELECT COALESCE(SUM(total_electricity), 0) INTO total_electricity_yesterday
    FROM realtime_summary_data 
    WHERE DATE(statistics_time) = DATE_SUB(report_date, INTERVAL 1 DAY);
    
    -- 获取去年同期总用电量（同比）
    SELECT COALESCE(SUM(total_electricity), 0) INTO @total_electricity_last_year
    FROM realtime_summary_data 
    WHERE DATE(statistics_time) = DATE_SUB(report_date, INTERVAL 1 YEAR);
    
    -- 计算增长率
    IF total_electricity_yesterday > 0 THEN
        SET mom_growth_rate = ROUND(((total_electricity_today - total_electricity_yesterday) / total_electricity_yesterday) * 100, 2);
    ELSE
        SET mom_growth_rate = 0;
    END IF;
    
    IF @total_electricity_last_year > 0 THEN
        SET yoy_growth_rate = ROUND(((total_electricity_today - @total_electricity_last_year) / @total_electricity_last_year) * 100, 2);
    ELSE
        SET yoy_growth_rate = 0;
    END IF;
    
    -- 插入或更新历史趋势数据
    INSERT INTO historical_trend_data (
        trend_id, energy_type, statistical_cycle, statistical_date, 
        energy_value, yoy_growth_rate, mom_growth_rate, industry_average
    )
    SELECT 
        COALESCE(MAX(trend_id), 0) + 1,
        '电',
        '日',
        report_date,
        total_electricity_today,
        yoy_growth_rate,
        mom_growth_rate,
        NULL  -- 行业均值可后续手动更新
    FROM historical_trend_data
    ON DUPLICATE KEY UPDATE
        energy_value = total_electricity_today,
        yoy_growth_rate = yoy_growth_rate,
        mom_growth_rate = mom_growth_rate,
        industry_average = VALUES(industry_average);
    
    -- 输出报表摘要
    SELECT 
        report_date as 报表日期,
        total_electricity_today as 当日总用电量,
        total_electricity_yesterday as 昨日总用电量,
        @total_electricity_last_year as 去年同期用电量,
        yoy_growth_rate as 同比增长率,
        mom_growth_rate as 环比增长率,
        CASE 
            WHEN yoy_growth_rate > 0 THEN '能耗上升'
            ELSE '能耗下降'
        END as 能耗状态;
        
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table circuit_monitoring_data
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_circuit_abnormal_alert`;
delimiter ;;
CREATE TRIGGER `tr_circuit_abnormal_alert` AFTER INSERT ON `circuit_monitoring_data` FOR EACH ROW BEGIN
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
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table energy_monitoring_data
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_auto_verify_status`;
delimiter ;;
CREATE TRIGGER `trg_auto_verify_status` BEFORE INSERT ON `energy_monitoring_data` FOR EACH ROW BEGIN
    -- 如果插入的数据质量是 '差' 或 '中'
    IF NEW.data_quality IN ('差', '中') THEN
        -- 强制将核实状态设为 '待核实'
        SET NEW.verification_status = '待核实';
    ELSE
        -- 否则默认为 '已核实'
        SET NEW.verification_status = '已核实';
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table maintenance_order
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_auto_update_alarm_status`;
delimiter ;;
CREATE TRIGGER `trg_auto_update_alarm_status` AFTER INSERT ON `maintenance_order` FOR EACH ROW BEGIN
    -- NEW.alarm_id 代表刚刚插入工单表的那条记录里的 alarm_id
    UPDATE alarm 
    SET status = '处理中' 
    WHERE alarm_id = NEW.alarm_id;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table pv_forecast
-- ----------------------------
DROP TRIGGER IF EXISTS `trigger_pv_forecast_deviation`;
delimiter ;;
CREATE TRIGGER `trigger_pv_forecast_deviation` AFTER INSERT ON `pv_forecast` FOR EACH ROW BEGIN
    DECLARE v_alarm_id VARCHAR(20);
    DECLARE v_alarm_content VARCHAR(500);
    
    -- 检查偏差率是否超过15%
    IF NEW.deviation_rate > 15.00 THEN
        -- 生成告警ID
        SET v_alarm_id = CONCAT('ALARM', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), LPAD(FLOOR(RAND()*1000), 3, '0'));
        
        -- 构建告警内容
        SET v_alarm_content = CONCAT(
            '光伏预测偏差率超过15%：预测编号', 
            NEW.forecast_id, 
            '，设备编号', 
            NEW.device_id, 
            '，预测日期', 
            DATE_FORMAT(NEW.forecast_date, '%Y-%m-%d'), 
            '，时间槽', 
            NEW.time_slot, 
            '，预测发电量', 
            NEW.forecast_generation, 
            'kWh，实际发电量', 
            IFNULL(NEW.actual_generation, 'NULL'), 
            'kWh，偏差率', 
            NEW.deviation_rate, 
            '%，模型版本', 
            NEW.model_version, 
            '。请检查预测模型并进行优化。'
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
            '中',  -- 告警等级设为中等
            v_alarm_content,
            '未处理',
            15.00
        );
        
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table pv_forecast
-- ----------------------------
DROP TRIGGER IF EXISTS `trigger_pv_forecast_update_deviation`;
delimiter ;;
CREATE TRIGGER `trigger_pv_forecast_update_deviation` AFTER UPDATE ON `pv_forecast` FOR EACH ROW BEGIN
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
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table realtime_summary_data
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_high_alarm_notification`;
delimiter ;;
CREATE TRIGGER `trg_high_alarm_notification` AFTER INSERT ON `realtime_summary_data` FOR EACH ROW BEGIN
    DECLARE alarm_count INT;
    DECLARE notification_message VARCHAR(500);
    
    -- 检查是否有高等级告警
    IF NEW.high_level_alarms > 0 THEN
        -- 获取最近1小时内的高等级告警总数
        SELECT COUNT(*) INTO alarm_count
        FROM realtime_summary_data
        WHERE statistics_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
          AND high_level_alarms > 0;
        
        -- 如果高等级告警数量超过阈值，生成通知消息
        IF alarm_count >= 3 THEN  -- 1小时内出现3次以上高等级告警
            SET notification_message = CONCAT(
                '【紧急告警通知】\n',
                '时间: ', NOW(), '\n',
                '高等级告警次数: ', NEW.high_level_alarms, '\n',
                '最近1小时累计: ', alarm_count, '次\n',
                '请立即查看处理！'
            );
            
            -- 这里可以集成实际的告警通知机制，如：
            -- 1. 插入到消息通知表
            -- 2. 调用邮件/短信接口
            -- 3. 记录到系统日志
            
            INSERT INTO system_notifications (message_type, message_content, priority, create_time)
            VALUES ('HIGH_ALARM', notification_message, 'URGENT', NOW());
            
        END IF;
    END IF;
    
    -- 同时检查数据质量，标记异常数据
    IF NEW.total_electricity IS NULL OR NEW.total_electricity < 0 THEN
        -- 记录数据质量问题
        INSERT INTO data_quality_issues (table_name, record_id, issue_type, description, create_time)
        VALUES ('realtime_summary_data', NEW.summary_id, 'DATA_ANOMALY', 
                CONCAT('用电量数据异常: ', COALESCE(NEW.total_electricity, 'NULL')), NOW());
    END IF;
    
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table transformer_monitoring_data
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_transformer_abnormal_alert`;
delimiter ;;
CREATE TRIGGER `tr_transformer_abnormal_alert` AFTER INSERT ON `transformer_monitoring_data` FOR EACH ROW BEGIN
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
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
