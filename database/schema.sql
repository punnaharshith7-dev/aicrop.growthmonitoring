-- ============================================================
--  AI CROP GROWTH MONITORING - Database Schema
--  Run this script in MySQL to set up the database.
-- ============================================================

CREATE DATABASE IF NOT EXISTS crop_monitoring;
USE crop_monitoring;

-- Users / Farmers table
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(80)  NOT NULL UNIQUE,
    email           VARCHAR(120) NOT NULL UNIQUE,
    password_hash   VARCHAR(256) NOT NULL,
    full_name       VARCHAR(120),
    phone           VARCHAR(20),
    location        VARCHAR(150),
    farm_size       FLOAT,
    profile_image   VARCHAR(200),
    reset_token     VARCHAR(200),
    reset_expiry    DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Crop monitoring records
CREATE TABLE IF NOT EXISTS crops (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    crop_name       VARCHAR(100) NOT NULL,
    crop_type       VARCHAR(100),
    crop_variety    VARCHAR(100),
    planting_date   DATE NOT NULL,
    field_area      FLOAT,
    location        VARCHAR(150),
    growth_stage    VARCHAR(100),
    health_status   VARCHAR(50) DEFAULT 'Healthy',
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Disease detection history
CREATE TABLE IF NOT EXISTS disease_detections (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    crop_id         INT,
    image_path      VARCHAR(300),
    disease_name    VARCHAR(150),
    confidence      FLOAT,
    symptoms        TEXT,
    precautions     TEXT,
    is_healthy      TINYINT(1) DEFAULT 0,
    detected_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL
);

-- Environmental sensor readings
CREATE TABLE IF NOT EXISTS environmental_data (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    crop_id         INT,
    temperature     FLOAT,
    humidity        FLOAT,
    rainfall        FLOAT,
    soil_moisture   FLOAT,
    reading_date    DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes           VARCHAR(300),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL
);

-- Yield prediction history
CREATE TABLE IF NOT EXISTS yield_predictions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    crop_type       VARCHAR(100),
    area            FLOAT,
    rainfall        FLOAT,
    temperature     FLOAT,
    soil_type       VARCHAR(100),
    fertilizer      VARCHAR(100),
    fertilizer_amount FLOAT,
    predicted_yield FLOAT,
    yield_unit      VARCHAR(50) DEFAULT 'tonnes/hectare',
    predicted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Smart farming recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    crop_id         INT,
    rec_type        VARCHAR(100),
    recommendation  TEXT,
    priority        VARCHAR(20) DEFAULT 'Normal',
    is_read         TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX idx_crops_user ON crops(user_id);
CREATE INDEX idx_disease_user ON disease_detections(user_id);
CREATE INDEX idx_env_user ON environmental_data(user_id);
CREATE INDEX idx_yield_user ON yield_predictions(user_id);
CREATE INDEX idx_rec_user ON recommendations(user_id);

-- Insert demo admin user  (password: Admin@123)
INSERT INTO users (username, email, password_hash, full_name, phone, location, farm_size)
VALUES (
    'admin',
    'admin@cropmonitor.com',
    'pbkdf2:sha256:600000$aBcDeFgH12345678$abcdefgh1234567890abcdefgh1234567890abcdefgh1234567890abcdef12',
    'Admin User',
    '+91-9876543210',
    'Hyderabad, Telangana',
    25.5
);
