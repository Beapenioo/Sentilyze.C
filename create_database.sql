-- Drop database if exists
DROP DATABASE IF EXISTS sentilyze;

-- Create database
CREATE DATABASE sentilyze CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use database
USE sentilyze;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

-- Create settings table
CREATE TABLE settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    theme VARCHAR(50),
    language VARCHAR(50),
    notifications_enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create text_entries table
CREATE TABLE text_entries (
    text_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    text_content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create analysis_results table
CREATE TABLE analysis_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    text_id INT NOT NULL,
    sentiment VARCHAR(20),
    sentiment_score FLOAT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (text_id) REFERENCES text_entries(text_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create feedbacks table
CREATE TABLE feedbacks (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    text_id INT NOT NULL,
    feedback_text TEXT,
    rating INT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (text_id) REFERENCES text_entries(text_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create session_logs table
CREATE TABLE session_logs (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB; 