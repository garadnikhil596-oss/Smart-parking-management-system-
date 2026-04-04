- ==============================
-- DATABASE
-- ==============================

CREATE DATABASE nikhil;

-- ==============================
-- USE DATABASE
-- ==============================

\c nikhil;





-- ==============================
-- ADMIN TABLE
-- ==============================

CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    username VARCHAR(50),
    password VARCHAR(50)
);


-- =============================
-- CATEGORY TABLE
-- ==============================

CREATE TABLE category (
    cat_id SERIAL PRIMARY KEY,
    parking_area_no VARCHAR(100),
    vehicle_type VARCHAR(50),
    vehicle_limit INT,
    parking_charge INT,
    status INT,
    doc TIMESTAMP
);

-- ==============================
-- ADD VEHICLE TABLE
-- ==============================+

CREATE TABLE add_vehicle (
    id SERIAL PRIMARY KEY,
    vehicle_no VARCHAR(20),
    parking_area_no VARCHAR(50),
    vehicle_type VARCHAR(50),
    parking_charge INT,
    status VARCHAR(20),
    arrival_time TIMESTAMP
);


-- ==============================
-- INSERT ADMIN DATA
-- ==============================

INSERT INTO admin (id,name,username,password) VALUES
(1,'Nikhil Garad','Nikhil','Garad123'),
(2,'Omkar Garad','Omkar','Nagar123'),
(6,'Amol Garad','Amol','Amol123'),
(7,'Akshay yedhe','Akshay','Nagar123'),
(8,'Akshay yedhe','Akshay','Nagar123'),
(9,'Akshay yedhe','Akshay','Pass123');

-- ==============================
-- INSERT DATA INTO CATEGORY
-- ==============================

INSERT INTO category
(parking_area_no, vehicle_type, vehicle_limit, parking_charge, status, doc)
VALUES
('7','Pickup Van',11,50,1,'2021-05-15 22:21:51'),
('2','Mini Van',8,50,1,'2021-05-15 20:10:39'),
('6','Motorcycle',26,20,1,'2021-05-15 19:04:41'),
('10','Bus',20,80,1,'2026-03-05 18:34:35');

-- ==============================
-- INSERT DATA INTO VEHICLE
-- ==============================

INSERT INTO add_vehicle
(vehicle_no, parking_area_no, vehicle_type, parking_charge, status, arrival_time)
VALUES
('MH20AB1234','7','Pickup Van',50,'Parked',NOW()),
('MH20CD5678','2','Mini Van',50,'Parked',NOW()),
('MH20EF2222','6','Motorcycle',20,'Parked',NOW());
