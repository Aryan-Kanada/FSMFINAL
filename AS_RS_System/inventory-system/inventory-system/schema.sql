-- Database Schema for Inventory Management System
CREATE DATABASE IF NOT EXISTS inventory_management;
USE inventory_management;

-- Boxes Table
CREATE TABLE IF NOT EXISTS Boxes (
  box_id INT AUTO_INCREMENT PRIMARY KEY,
  column_name VARCHAR(10) NOT NULL,
  row_number INT NOT NULL
);

-- Items Table
CREATE TABLE IF NOT EXISTS Items (
  item_id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  added_on DATETIME NOT NULL
);

-- SubCompartments Table
CREATE TABLE IF NOT EXISTS SubCompartments (
  subcom_place VARCHAR(20) PRIMARY KEY,
  box_id INT NOT NULL,
  sub_id VARCHAR(10) NOT NULL,
  item_id INT,
  status ENUM('Empty', 'Occupied') NOT NULL DEFAULT 'Empty',
  FOREIGN KEY (box_id) REFERENCES Boxes(box_id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE SET NULL
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS Transactions (
  tran_id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT,
  subcom_place VARCHAR(20),
  action ENUM('added', 'retrieved') NOT NULL,
  time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE SET NULL,
  FOREIGN KEY (subcom_place) REFERENCES SubCompartments(subcom_place) ON DELETE SET NULL
);

-- Initial Sample Data
INSERT INTO Boxes (column_name, row_number) VALUES ('A', 1), ('A', 2), ('B', 1), ('B', 2);
INSERT INTO Items (item_id, name, description, added_on) VALUES 
  (1, 'Widget', 'Standard widget for general use', NOW()),
  (2, 'Gadget', 'Electronic gadget with multiple functions', NOW()),
  (3, 'Tool', 'Handheld tool for repairs', NOW());
