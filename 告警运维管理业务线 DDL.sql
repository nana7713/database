CREATE TABLE user (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50),
    department VARCHAR(50),
    contact_info VARCHAR(100),
    role VARCHAR(30)
);

CREATE TABLE device (
    device_id VARCHAR(20) PRIMARY KEY,
    device_name VARCHAR(100),
    device_type VARCHAR(50),
    model_spec VARCHAR(100),
    install_date DATE,
    warranty_period VARCHAR(30),
    is_scrapped BOOLEAN
);

CREATE TABLE calibration_record (
    record_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(20),
    calibrator_id VARCHAR(20),
    calibration_time DATETIME,
    FOREIGN KEY (device_id) REFERENCES device(device_id),
    FOREIGN KEY (calibrator_id) REFERENCES user(user_id)
);

CREATE TABLE alarm (
    alarm_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(20),
    alarm_type VARCHAR(50),
    occur_time DATETIME,
    alarm_level VARCHAR(20),
    alarm_content TEXT,
    status VARCHAR(20),
    threshold_value DECIMAL(10,2),
    FOREIGN KEY (device_id) REFERENCES device(device_id)
);

CREATE TABLE maintenance_order (
    order_id VARCHAR(20) PRIMARY KEY,
    alarm_id VARCHAR(20),
    maintainer_id VARCHAR(20),
    dispatch_time DATETIME,
    response_time DATETIME,
    finish_time DATETIME,
    result TEXT,
    recheck_status VARCHAR(20),
    attachment_path VARCHAR(255),
    FOREIGN KEY (alarm_id) REFERENCES alarm(alarm_id),
    FOREIGN KEY (maintainer_id) REFERENCES user(user_id)
);
