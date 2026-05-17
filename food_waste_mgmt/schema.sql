-- ============================================================
-- Food Waste Management System - MySQL Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS food_waste_mgmt;
USE food_waste_mgmt;

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role ENUM('donor', 'ngo', 'admin') NOT NULL DEFAULT 'donor',
    phone VARCHAR(20),
    organization_name VARCHAR(200),
    address TEXT,
    city VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT TRUE,
    profile_image VARCHAR(300),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- FOOD DONATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS food_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    food_name VARCHAR(200) NOT NULL,
    food_type ENUM('veg', 'non-veg', 'mixed') NOT NULL,
    quantity INT NOT NULL COMMENT 'Number of people it can serve',
    description TEXT,
    expiry_time DATETIME NOT NULL,
    pickup_start_time DATETIME NOT NULL,
    pickup_end_time DATETIME NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT NOT NULL,
    contact_person VARCHAR(150),
    contact_phone VARCHAR(20),
    status ENUM('available', 'accepted', 'collected', 'completed', 'expired', 'removed') DEFAULT 'available',
    image_url VARCHAR(300),
    special_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- PICKUP REQUESTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS pickup_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL,
    ngo_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'in_transit', 'collected', 'completed', 'cancelled') DEFAULT 'pending',
    pickup_time DATETIME,
    collected_time DATETIME,
    completed_time DATETIME,
    notes TEXT,
    beneficiaries_count INT DEFAULT 0 COMMENT 'Actual number of people fed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES food_donations(id) ON DELETE CASCADE,
    FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'danger') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    related_donation_id INT,
    related_request_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (related_donation_id) REFERENCES food_donations(id) ON DELETE SET NULL,
    FOREIGN KEY (related_request_id) REFERENCES pickup_requests(id) ON DELETE SET NULL
);

-- ============================================================
-- DONATION ANALYTICS TABLE (for stats)
-- ============================================================
CREATE TABLE IF NOT EXISTS donation_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_donations INT DEFAULT 0,
    total_meals_saved INT DEFAULT 0,
    total_ngos_active INT DEFAULT 0,
    total_donors_active INT DEFAULT 0,
    stat_date DATE DEFAULT (CURRENT_DATE),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_donations_status ON food_donations(status);
CREATE INDEX idx_donations_expiry ON food_donations(expiry_time);
CREATE INDEX idx_donations_location ON food_donations(latitude, longitude);
CREATE INDEX idx_pickup_requests_status ON pickup_requests(status);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- ============================================================
-- DEFAULT ADMIN USER (password: Admin@123)
-- ============================================================
INSERT INTO users (name, email, password_hash, role, organization_name, phone) VALUES
('System Admin', 'admin@foodwaste.com',
 'pbkdf2:sha256:260000$placeholder$placeholder',  -- Will be replaced on first run
 'admin', 'Food Waste Management System', '9999999999');
