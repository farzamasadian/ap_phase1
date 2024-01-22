-- Users Table
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('patient', 'staff') NOT NULL
);

-- Clinics Table
CREATE TABLE IF NOT EXISTS Clinics (
    clinic_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_info VARCHAR(20)
);

-- Appointments Table
CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    status ENUM('pending', 'confirmed', 'canceled') NOT NULL,
    date_time DATETIME NOT NULL,
    user_id INTEGER NOT NULL,
    clinic_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY(clinic_id) REFERENCES Clinics(clinic_id)
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS Notifications (
    notification_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    date_time DATETIME NOT NULL,
    FOREIGN KEY(username) REFERENCES Users(username)
);

-- Services Table
CREATE TABLE IF NOT EXISTS Services (
    service_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    clinic_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    FOREIGN KEY(clinic_id) REFERENCES Clinics(clinic_id)
);
