CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(30) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type CHAR(1) NOT NULL CHECK (user_type IN ("A", "R", "V")),
    PRIMARY KEY (user_id)
);

CREATE TABLE locations (
    location_id INT NOT NULL AUTO_INCREMENT,
    user_id INT ,
    location_name VARCHAR(255) NOT NULL, --2
    description VARCHAR(6000),
    latitude DECIMAL(8, 6),
    longitude DECIMAL(9, 6),
    PRIMARY KEY (location_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE data (
    data_id INT NOT NULL AUTO_INCREMENT, 
    location_id INT,
    user_id INT,
    date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ph FLOAT, --4
    bod FLOAT,
    cod FLOAT,
    temperature FLOAT,
    ammonia FLOAT,
    arsenic FLOAT,
    calcium FLOAT,
    ec FLOAT,
    coliform FLOAT,
    hardness FLOAT,
    lead_pb FLOAT,
    nitrogen FLOAT,
    sodium FLOAT,
    sulfate FLOAT,
    tss FLOAT,
    turbidity FLOAT,
    PRIMARY KEY (data_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- DROP
DROP TABLE locations;
DROP TABLE users;
DROP TABLE data;