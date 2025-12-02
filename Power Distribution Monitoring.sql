CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE roles (
    role_id INT PRIMARY KEY,
    role_code VARCHAR(20) NOT NULL UNIQUE, 
    role_name VARCHAR(50) NOT NULL, 
    description VARCHAR(255)
);

CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
) ;

CREATE TABLE plant_area (
    plant_area_id VARCHAR(20) PRIMARY KEY,
    plant_area_name VARCHAR(100) NOT NULL UNIQUE,
    location_desc VARCHAR(255), 
    manager_id VARCHAR(20),
    contact_phone VARCHAR(20),
    FOREIGN KEY (manager_id) REFERENCES users(user_id)
);

CREATE TABLE substation (
    substation_id VARCHAR(20) PRIMARY KEY,
    plant_area_id VARCHAR(20) NOT NULL,
    substation_name VARCHAR(100) NOT NULL,
    substation_location_desc VARCHAR(255),
    voltage_level VARCHAR(10),
    transformer_count INT DEFAULT 0,
    commissioning_date DATE,
    responsible_user_id VARCHAR(20),
    contact_phone VARCHAR(20),
    FOREIGN KEY (plant_area_id) REFERENCES plant_area(plant_area_id),
    FOREIGN KEY (responsible_user_id) REFERENCES users(user_id) 
);


CREATE TABLE circuit_monitoring_data (
    circuit_data_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    substation_id VARCHAR(20) NOT NULL,
    circuit_id VARCHAR(20) NOT NULL,
    collection_time DATETIME NOT NULL,
    voltage DECIMAL(10,2) COMMENT '单位: kV',
    current DECIMAL(10,2) COMMENT '单位: A',
    active_power DECIMAL(10,2) COMMENT '单位: kW',
    reactive_power DECIMAL(10,2) COMMENT '单位：kVar',
    power_factor DECIMAL(3,2) CHECK(power_factor<1 AND power_factor>-1),
    forward_active_energy DECIMAL(15,2) COMMENT '单位：kWh',
    reverse_active_energy DECIMAL(15,2) COMMENT '单位：kWh',
    switch_status VARCHAR(10) CHECK(switch_status IN ('分闸','合闸')),
    cable_temp DECIMAL(5,2) COMMENT '单位：℃',
    capacitor_temp DECIMAL(5,2) COMMENT '单位：℃',
    FOREIGN KEY (substation_id) REFERENCES substation(substation_id),
    UNIQUE uk_circuit_time (substation_id, circuit_id, collection_time) -- 防止重复数据
);

CREATE TABLE transformer_monitoring_data (
    transformer_data_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    substation_id VARCHAR(20) NOT NULL,
    transformer_id VARCHAR(20) NOT NULL,
    collection_time DATETIME NOT NULL,
    load_rate DECIMAL(5,2) CHECK(load_rate>=0),
    winding_temp DECIMAL(5,2) COMMENT '单位：℃',
    core_temp DECIMAL(5,2) COMMENT '单位：℃',
    ambient_temp DECIMAL(5,2) COMMENT '单位：℃',
    ambient_humidity DECIMAL(5,2) COMMENT '单位：%',
    running_status VARCHAR(10) CHECK(running_status IN('正常','异常')),
    FOREIGN KEY (substation_id) REFERENCES substation(substation_id),
    UNIQUE uk_transformer_time (substation_id, transformer_id, collection_time) -- 防止重复数据
);
