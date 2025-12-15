-- 1. 告警信息表 Alarm
CREATE TABLE Alarm (
    alarm_id VARCHAR(20) PRIMARY KEY COMMENT '告警编号',
    device_id VARCHAR(20) NOT NULL COMMENT '关联设备编号',
    alarm_type VARCHAR(50) COMMENT '告警类型',
    alarm_level VARCHAR(20) COMMENT '告警等级',
    alarm_threshold FLOAT COMMENT '告警阈值',
    alarm_time DATETIME COMMENT '告警时间',
    alarm_content TEXT COMMENT '告警内容',
    status VARCHAR(20) DEFAULT '未处理' COMMENT '告警状态',
    FOREIGN KEY (device_id) REFERENCES Device(device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警信息表';

-- 2. 运维人员表 Maintainer
CREATE TABLE Maintainer (
    maintainer_id VARCHAR(20) PRIMARY KEY COMMENT '运维人员编号',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) COMMENT '电话',
    email VARCHAR(50) COMMENT '邮箱',
    role_id VARCHAR(20),
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='运维人员表';

-- 3. 角色表 Role
CREATE TABLE Role (
    role_id VARCHAR(20) PRIMARY KEY COMMENT '角色编号',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    description VARCHAR(255) COMMENT '角色描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 4. 运维工单表 WorkOrder
CREATE TABLE WorkOrder (
    work_order_id VARCHAR(20) PRIMARY KEY COMMENT '工单编号',
    alarm_id VARCHAR(20) NOT NULL COMMENT '关联告警编号',
    maintainer_id VARCHAR(20) COMMENT '处理人编号',
    assign_time DATETIME COMMENT '派单时间',
    accept_time DATETIME COMMENT '接单时间',
    finish_time DATETIME COMMENT '完成时间',
    result TEXT COMMENT '处理结果',
    review_status VARCHAR(20) DEFAULT '未复核' COMMENT '复核状态',
    attachment_path VARCHAR(255) COMMENT '附件路径',
    FOREIGN KEY (alarm_id) REFERENCES Alarm(alarm_id),
    FOREIGN KEY (maintainer_id) REFERENCES Maintainer(maintainer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='运维工单表';
