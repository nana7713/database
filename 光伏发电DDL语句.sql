CREATE TABLE pv_device (
    device_id VARCHAR(20) PRIMARY KEY,
    device_type VARCHAR(10) NOT NULL CHECK (device_type IN ('逆变器', '汇流箱')),
    location VARCHAR(50) NOT NULL,
    capacity DECIMAL(8,2) NOT NULL,
    operation_date DATE NOT NULL,
    calibration_cycle INT NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('正常', '故障', '离线')),
    protocol VARCHAR(10) NOT NULL CHECK (protocol IN ('RS485', 'Lora'))
);


CREATE TABLE pv_generation (
    data_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(20) NOT NULL,
    grid_point_id VARCHAR(20) NOT NULL,
    collect_time DATETIME NOT NULL,
    generation DECIMAL(10,2) NOT NULL,
    feed_in DECIMAL(10,2) NOT NULL,
    self_use DECIMAL(10,2) NOT NULL,
    inverter_efficiency DECIMAL(5,2),
    string_voltage DECIMAL(8,2),
    string_current DECIMAL(8,2),
    FOREIGN KEY (device_id) REFERENCES pv_device(device_id) ON DELETE CASCADE
);


CREATE TABLE pv_forecast (
    forecast_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(20) NOT NULL,
    grid_point_id VARCHAR(20) NOT NULL,
    forecast_date DATE NOT NULL,
    time_slot VARCHAR(20) NOT NULL,
    forecast_generation DECIMAL(10,2) NOT NULL,
    actual_data_id VARCHAR(20),
    actual_generation DECIMAL(10,2),
    deviation_rate DECIMAL(5,2),
    model_version VARCHAR(10) NOT NULL,
    FOREIGN KEY (device_id) REFERENCES pv_device(device_id) ON DELETE CASCADE,
    FOREIGN KEY (actual_data_id) REFERENCES pv_generation(data_id) ON DELETE SET NULL
);