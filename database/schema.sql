-- SysRecover MySQL Database Schema
-- Run this in MySQL Workbench to create the database and tables

CREATE DATABASE IF NOT EXISTS sysrecover_db;
USE sysrecover_db;

-- Simulation Runs Table
CREATE TABLE IF NOT EXISTS simulation_run (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME
);

-- Processes Table
CREATE TABLE IF NOT EXISTS process (
    process_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    arrival_time INT DEFAULT 0,
    burst_time INT NOT NULL,
    priority INT DEFAULT 0,
    state VARCHAR(20) DEFAULT 'ready',
    completion_time INT,
    turnaround_time INT,
    waiting_time INT,
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    process_id INT,
    type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    start_time DATETIME,
    commit_time DATETIME,
    rollback_time DATETIME,
    two_phase_state VARCHAR(50) DEFAULT 'growing',
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES process(process_id) ON DELETE SET NULL
);

-- Resources Table
CREATE TABLE IF NOT EXISTS resource (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) DEFAULT 'general',
    total_instances INT DEFAULT 1,
    available_instances INT DEFAULT 1,
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE
);

-- Locks Table
CREATE TABLE IF NOT EXISTS locks (
    lock_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    resource_id INT NOT NULL,
    lock_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'granted',
    granted_at DATETIME,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resource(resource_id) ON DELETE CASCADE
);

-- Memory Pages Table
CREATE TABLE IF NOT EXISTS memory_page (
    page_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    page_number INT NOT NULL,
    frame_number INT,
    status VARCHAR(50) DEFAULT 'not_in_memory',
    last_accessed INT DEFAULT 0,
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE
);

-- Event Log Table
CREATE TABLE IF NOT EXISTS event_log (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'info',
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE
);

-- Recovery Log Table
CREATE TABLE IF NOT EXISTS recovery_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    transaction_id INT NOT NULL,
    lsn INT NOT NULL,
    operation VARCHAR(100) NOT NULL,
    data_item VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
);

-- Checkpoints Table
CREATE TABLE IF NOT EXISTS checkpoint (
    checkpoint_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    lsn INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    active_transactions TEXT,
    FOREIGN KEY (run_id) REFERENCES simulation_run(run_id) ON DELETE CASCADE
);

