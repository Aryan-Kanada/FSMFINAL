-- MySQL dump 10.13  Distrib 5.7.24, for osx11.1 (x86_64)
--
-- Host: localhost    Database: inventory_management
-- ------------------------------------------------------
-- Server version	9.3.0
USE inventory_management;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Boxes`
--

DROP TABLE IF EXISTS `Boxes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Boxes` (
  `box_id` varchar(2) NOT NULL,
  `column_name` char(1) NOT NULL,
  `row_number` int NOT NULL,
  PRIMARY KEY (`box_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Boxes`
--

LOCK TABLES `Boxes` WRITE;
/*!40000 ALTER TABLE `Boxes` DISABLE KEYS */;
INSERT INTO `Boxes` VALUES ('A1','A',1),('A2','A',2),('A3','A',3),('A4','A',4),('A5','A',5),('A6','A',6),('A7','A',7),('B1','B',1),('B2','B',2),('B3','B',3),('B4','B',4),('B5','B',5),('B6','B',6),('B7','B',7),('C1','C',1),('C2','C',2),('C3','C',3),('C4','C',4),('C5','C',5),('C6','C',6),('C7','C',7),('D1','D',1),('D2','D',2),('D3','D',3),('D4','D',4),('D5','D',5),('D6','D',6),('D7','D',7),('E1','E',1),('E2','E',2),('E3','E',3),('E4','E',4),('E5','E',5),('E6','E',6),('E7','E',7);
/*!40000 ALTER TABLE `Boxes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Items`
--

DROP TABLE IF EXISTS `Items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Items` (
  `item_id` int NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `added_on` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Items`
--

LOCK TABLES `Items` WRITE;
/*!40000 ALTER TABLE `Items` DISABLE KEYS */;
INSERT INTO `Items` VALUES (1,'Bearing','Steel ball bearing','2025-06-16 16:24:54'),(2,'Gear','24T spur gear','2025-06-16 16:24:54'),(3,'Bolt Set','M6 bolts with washers','2025-06-16 16:24:54');
/*!40000 ALTER TABLE `Items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OrderItems`
--

DROP TABLE IF EXISTS `OrderItems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `OrderItems` (
  `order_item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `item_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_item_id`),
  KEY `order_id` (`order_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `Items` (`item_id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OrderItems`
--

LOCK TABLES `OrderItems` WRITE;
/*!40000 ALTER TABLE `OrderItems` DISABLE KEYS */;
INSERT INTO `OrderItems` VALUES (4,4,1,1,29.99,29.99,'2025-08-26 02:58:07'),(5,5,3,1,23.00,23.00,'2025-08-26 05:13:59'),(6,6,1,1,2399.20,2399.20,'2025-08-26 21:42:39'),(7,7,3,1,55.00,55.00,'2025-08-27 00:41:50'),(8,8,3,1,55.00,55.00,'2025-08-27 01:07:22'),(13,13,3,1,55.00,55.00,'2025-08-27 01:17:29'),(14,14,2,1,150.00,150.00,'2025-08-27 01:19:17'),(15,15,2,1,150.00,150.00,'2025-08-27 01:27:17'),(16,16,2,1,150.00,150.00,'2025-08-27 01:40:31'),(17,17,2,1,150.00,150.00,'2025-08-27 02:01:22'),(18,18,2,1,150.00,150.00,'2025-08-27 02:30:28'),(19,19,2,1,150.00,150.00,'2025-08-29 16:16:27'),(20,20,2,1,150.00,150.00,'2025-08-30 14:01:19');
/*!40000 ALTER TABLE `OrderItems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Orders`
--

DROP TABLE IF EXISTS `Orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) NOT NULL,
  `customer_email` varchar(100) NOT NULL,
  `customer_phone` varchar(20) NOT NULL,
  `shipping_address` text NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `order_status` enum('pending','processing','shipped','delivered','cancelled') NOT NULL DEFAULT 'pending',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Orders`
--

LOCK TABLES `Orders` WRITE;
/*!40000 ALTER TABLE `Orders` DISABLE KEYS */;
INSERT INTO `Orders` VALUES (4,'Test Customer','test@example.com','123-456-7890','123 Test Street, Test City, TC 12345',29.99,'pending','2025-08-26 02:58:07','2025-08-26 02:58:07'),(5,'Devisha','devisha@gmail.com','6969696969','A/29, Shantivan Bunglows, Jivraj Park, Ambika Township, Nana Mava Road',23.00,'pending','2025-08-26 05:13:59','2025-08-26 05:13:59'),(6,'Test Customer','test@example.com','123-456-7890','123 Test Street, Test City, TC 12345',2399.20,'pending','2025-08-26 21:42:39','2025-08-26 21:42:39'),(7,'Devisha','devisha@gmail.com','6969696969','A/29, Shantivan Bunglows, Jivraj Park, Ambika Township, Nana Mava Road',55.00,'pending','2025-08-27 00:41:50','2025-08-27 00:41:50'),(8,'Test Fix','test@fix.com','123-456-7890','123 Fix Street',55.00,'pending','2025-08-27 01:07:22','2025-08-27 01:07:22'),(13,'Test Customer','test@example.com','123-456-7890','123 Test Street, Test City, TC 12345',55.00,'pending','2025-08-27 01:17:29','2025-08-27 01:17:29'),(14,'Devisha','tomcruiseop76@gmail.com','6969696969','A/29, Shantivan Bunglows, Jivraj Park, Ambika Township, Nana Mava Road',150.00,'pending','2025-08-27 01:19:17','2025-08-27 01:19:17'),(15,'Test Customer','test@example.com','1234567890','123 Test St',150.00,'pending','2025-08-27 01:27:17','2025-08-27 01:27:17'),(16,'Test Customer','test@example.com','1234567890','Test Address',150.00,'pending','2025-08-27 01:40:31','2025-08-27 01:40:31'),(17,'Devisha','devisha@gmail.com','6969696969','A/29, Shantivan Bunglows, Jivraj Park, Ambika Township, Nana Mava Road',150.00,'pending','2025-08-27 02:01:22','2025-08-27 02:01:22'),(18,'Devisha','devisha@gmail.com','6969696969','vhv',150.00,'pending','2025-08-27 02:30:28','2025-08-27 02:30:28'),(19,'Harshil','tomcruiseop76@gmail.com','8469288844','VV Nagar',150.00,'pending','2025-08-29 16:16:27','2025-08-29 16:16:27'),(20,'Harshil','tomcruiseop76@gmail.com','8469288844','VV Nagar',150.00,'pending','2025-08-30 14:01:19','2025-08-30 14:01:19');
/*!40000 ALTER TABLE `Orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SubCompartments`
--

DROP TABLE IF EXISTS `SubCompartments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SubCompartments` (
  `subcom_place` varchar(3) NOT NULL,
  `box_id` varchar(2) DEFAULT NULL,
  `sub_id` char(1) DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`subcom_place`),
  KEY `fk_subcompartments_boxes` (`box_id`),
  KEY `hvk_idx` (`item_id`),
  CONSTRAINT `fk_subcompartments_boxes` FOREIGN KEY (`box_id`) REFERENCES `Boxes` (`box_id`),
  CONSTRAINT `fk_subcompartments_items` FOREIGN KEY (`item_id`) REFERENCES `Items` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SubCompartments`
--

LOCK TABLES `SubCompartments` WRITE;
/*!40000 ALTER TABLE `SubCompartments` DISABLE KEYS */;
INSERT INTO `SubCompartments` VALUES ('A1a','A1','a',NULL,'Empty'),('A1b','A1','b',NULL,'Empty'),('A1c','A1','c',NULL,'Empty'),('A1d','A1','d',NULL,'Empty'),('A1e','A1','e',NULL,'Empty'),('A1f','A1','f',NULL,'Empty'),('A2a','A2','a',NULL,'Empty'),('A2b','A2','b',NULL,'Empty'),('A2c','A2','c',NULL,'Empty'),('A2d','A2','d',NULL,'Empty'),('A2e','A2','e',NULL,'Empty'),('A2f','A2','f',NULL,'Empty'),('A3a','A3','a',NULL,'Empty'),('A3b','A3','b',NULL,'Empty'),('A3c','A3','c',NULL,'Empty'),('A3d','A3','d',NULL,'Empty'),('A3e','A3','e',NULL,'Empty'),('A3f','A3','f',NULL,'Empty'),('A4a','A4','a',NULL,'Empty'),('A4b','A4','b',NULL,'Empty'),('A4c','A4','c',NULL,'Empty'),('A4d','A4','d',NULL,'Empty'),('A4e','A4','e',NULL,'Empty'),('A4f','A4','f',NULL,'Empty'),('A5a','A5','a',NULL,'Empty'),('A5b','A5','b',NULL,'Empty'),('A5c','A5','c',1,'Occupied'),('A5d','A5','d',NULL,'Empty'),('A5e','A5','e',NULL,'Empty'),('A5f','A5','f',NULL,'Empty'),('A6a','A6','a',NULL,'Empty'),('A6b','A6','b',NULL,'Empty'),('A6c','A6','c',NULL,'Empty'),('A6d','A6','d',NULL,'Empty'),('A6e','A6','e',NULL,'Empty'),('A6f','A6','f',NULL,'Empty'),('A7a','A7','a',NULL,'Empty'),('A7b','A7','b',NULL,'Empty'),('A7c','A7','c',1,'Occupied'),('A7d','A7','d',NULL,'Empty'),('A7e','A7','e',NULL,'Empty'),('A7f','A7','f',NULL,'Empty'),('B1a','B1','a',NULL,'Empty'),('B1b','B1','b',NULL,'Empty'),('B1c','B1','c',3,'Occupied'),('B1d','B1','d',NULL,'Empty'),('B1e','B1','e',NULL,'Empty'),('B1f','B1','f',NULL,'Empty'),('B2a','B2','a',NULL,'Empty'),('B2b','B2','b',NULL,'Empty'),('B2c','B2','c',NULL,'Empty'),('B2d','B2','d',NULL,'Empty'),('B2e','B2','e',NULL,'Empty'),('B2f','B2','f',NULL,'Empty'),('B3a','B3','a',NULL,'Empty'),('B3b','B3','b',NULL,'Empty'),('B3c','B3','c',1,'Occupied'),('B3d','B3','d',NULL,'Empty'),('B3e','B3','e',NULL,'Empty'),('B3f','B3','f',NULL,'Empty'),('B4a','B4','a',NULL,'Empty'),('B4b','B4','b',NULL,'Empty'),('B4c','B4','c',3,'Occupied'),('B4d','B4','d',NULL,'Empty'),('B4e','B4','e',NULL,'Empty'),('B4f','B4','f',NULL,'Empty'),('B5a','B5','a',NULL,'Empty'),('B5b','B5','b',NULL,'Empty'),('B5c','B5','c',NULL,'Empty'),('B5d','B5','d',NULL,'Empty'),('B5e','B5','e',NULL,'Empty'),('B5f','B5','f',NULL,'Empty'),('B6a','B6','a',NULL,'Empty'),('B6b','B6','b',NULL,'Empty'),('B6c','B6','c',3,'Occupied'),('B6d','B6','d',NULL,'Empty'),('B6e','B6','e',NULL,'Empty'),('B6f','B6','f',NULL,'Empty'),('B7a','B7','a',NULL,'Empty'),('B7b','B7','b',NULL,'Empty'),('B7c','B7','c',3,'Occupied'),('B7d','B7','d',NULL,'Empty'),('B7e','B7','e',NULL,'Empty'),('B7f','B7','f',NULL,'Empty'),('C1a','C1','a',NULL,'Empty'),('C1b','C1','b',NULL,'Empty'),('C1c','C1','c',NULL,'Empty'),('C1d','C1','d',NULL,'Empty'),('C1e','C1','e',NULL,'Empty'),('C1f','C1','f',NULL,'Empty'),('C2a','C2','a',NULL,'Empty'),('C2b','C2','b',NULL,'Empty'),('C2c','C2','c',NULL,'Empty'),('C2d','C2','d',NULL,'Empty'),('C2e','C2','e',NULL,'Empty'),('C2f','C2','f',NULL,'Empty'),('C3a','C3','a',NULL,'Empty'),('C3b','C3','b',NULL,'Empty'),('C3c','C3','c',3,'Occupied'),('C3d','C3','d',NULL,'Empty'),('C3e','C3','e',NULL,'Empty'),('C3f','C3','f',NULL,'Empty'),('C4a','C4','a',NULL,'Empty'),('C4b','C4','b',NULL,'Empty'),('C4c','C4','c',1,'Occupied'),('C4d','C4','d',NULL,'Empty'),('C4e','C4','e',NULL,'Empty'),('C4f','C4','f',NULL,'Empty'),('C5a','C5','a',NULL,'Empty'),('C5b','C5','b',NULL,'Empty'),('C5c','C5','c',1,'Occupied'),('C5d','C5','d',NULL,'Empty'),('C5e','C5','e',NULL,'Empty'),('C5f','C5','f',NULL,'Empty'),('C6a','C6','a',NULL,'Empty'),('C6b','C6','b',NULL,'Empty'),('C6c','C6','c',3,'Occupied'),('C6d','C6','d',NULL,'Empty'),('C6e','C6','e',NULL,'Empty'),('C6f','C6','f',NULL,'Empty'),('C7a','C7','a',NULL,'Empty'),('C7b','C7','b',NULL,'Empty'),('C7c','C7','c',NULL,'Empty'),('C7d','C7','d',NULL,'Empty'),('C7e','C7','e',NULL,'Empty'),('C7f','C7','f',NULL,'Empty'),('D1a','D1','a',NULL,'Empty'),('D1b','D1','b',NULL,'Empty'),('D1c','D1','c',1,'Occupied'),('D1d','D1','d',NULL,'Empty'),('D1e','D1','e',NULL,'Empty'),('D1f','D1','f',NULL,'Empty'),('D2a','D2','a',NULL,'Empty'),('D2b','D2','b',NULL,'Empty'),('D2c','D2','c',NULL,'Empty'),('D2d','D2','d',NULL,'Empty'),('D2e','D2','e',NULL,'Empty'),('D2f','D2','f',NULL,'Empty'),('D3a','D3','a',NULL,'Empty'),('D3b','D3','b',NULL,'Empty'),('D3c','D3','c',1,'Occupied'),('D3d','D3','d',NULL,'Empty'),('D3e','D3','e',NULL,'Empty'),('D3f','D3','f',NULL,'Empty'),('D4a','D4','a',NULL,'Empty'),('D4b','D4','b',NULL,'Empty'),('D4c','D4','c',2,'Occupied'),('D4d','D4','d',NULL,'Empty'),('D4e','D4','e',NULL,'Empty'),('D4f','D4','f',NULL,'Empty'),('D5a','D5','a',NULL,'Empty'),('D5b','D5','b',NULL,'Empty'),('D5c','D5','c',2,'Occupied'),('D5d','D5','d',NULL,'Empty'),('D5e','D5','e',NULL,'Empty'),('D5f','D5','f',NULL,'Empty'),('D6a','D6','a',NULL,'Empty'),('D6b','D6','b',NULL,'Empty'),('D6c','D6','c',2,'Occupied'),('D6d','D6','d',NULL,'Empty'),('D6e','D6','e',NULL,'Empty'),('D6f','D6','f',NULL,'Empty'),('D7a','D7','a',NULL,'Empty'),('D7b','D7','b',NULL,'Empty'),('D7c','D7','c',2,'Occupied'),('D7d','D7','d',NULL,'Empty'),('D7e','D7','e',NULL,'Empty'),('D7f','D7','f',NULL,'Empty'),('E1a','E1','a',NULL,'Empty'),('E1b','E1','b',NULL,'Empty'),('E1c','E1','c',2,'Occupied'),('E1d','E1','d',NULL,'Empty'),('E1e','E1','e',NULL,'Empty'),('E1f','E1','f',NULL,'Empty'),('E2a','E2','a',NULL,'Empty'),('E2b','E2','b',NULL,'Empty'),('E2c','E2','c',2,'Occupied'),('E2d','E2','d',NULL,'Empty'),('E2e','E2','e',NULL,'Empty'),('E2f','E2','f',NULL,'Empty'),('E3a','E3','a',NULL,'Empty'),('E3b','E3','b',NULL,'Empty'),('E3c','E3','c',1,'Occupied'),('E3d','E3','d',NULL,'Empty'),('E3e','E3','e',NULL,'Empty'),('E3f','E3','f',NULL,'Empty'),('E4a','E4','a',NULL,'Empty'),('E4b','E4','b',NULL,'Empty'),('E4c','E4','c',2,'Occupied'),('E4d','E4','d',NULL,'Empty'),('E4e','E4','e',NULL,'Empty'),('E4f','E4','f',NULL,'Empty'),('E5a','E5','a',NULL,'Empty'),('E5b','E5','b',NULL,'Empty'),('E5c','E5','c',1,'Occupied'),('E5d','E5','d',NULL,'Empty'),('E5e','E5','e',NULL,'Empty'),('E5f','E5','f',NULL,'Empty'),('E6a','E6','a',NULL,'Empty'),('E6b','E6','b',NULL,'Empty'),('E6c','E6','c',3,'Occupied'),('E6d','E6','d',NULL,'Empty'),('E6e','E6','e',NULL,'Empty'),('E6f','E6','f',NULL,'Empty'),('E7a','E7','a',NULL,'Empty'),('E7b','E7','b',NULL,'Empty'),('E7c','E7','c',3,'Occupied'),('E7d','E7','d',NULL,'Empty'),('E7e','E7','e',NULL,'Empty'),('E7f','E7','f',NULL,'Empty');
/*!40000 ALTER TABLE `SubCompartments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Transactions`
--

DROP TABLE IF EXISTS `Transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Transactions` (
  `tran_id` int NOT NULL AUTO_INCREMENT,
  `item_id` int DEFAULT NULL,
  `subcom_place` varchar(3) DEFAULT NULL,
  `action` varchar(45) DEFAULT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tran_id`),
  KEY `fk_transactions_items` (`item_id`),
  KEY `fk_transactions_subcom` (`subcom_place`),
  CONSTRAINT `fk_transactions_items` FOREIGN KEY (`item_id`) REFERENCES `Items` (`item_id`),
  CONSTRAINT `fk_transactions_subcom` FOREIGN KEY (`subcom_place`) REFERENCES `SubCompartments` (`subcom_place`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Transactions`
--

LOCK TABLES `Transactions` WRITE;
/*!40000 ALTER TABLE `Transactions` DISABLE KEYS */;
INSERT INTO `Transactions` VALUES (1,2,'A1a','retrieved','2025-06-18 01:16:11'),(2,1,'A1a','added','2025-06-18 01:17:11'),(3,2,'A1d','retrieved','2025-06-18 01:25:03'),(4,2,'A1d','added','2025-06-18 01:25:16'),(5,2,'A1d','retrieved','2025-06-18 13:19:49'),(6,2,'A1f','retrieved','2025-06-18 13:19:49'),(7,2,'A2b','retrieved','2025-06-18 13:19:49'),(8,2,'A2d','retrieved','2025-06-18 13:19:49'),(9,3,'A1d','added','2025-06-18 13:22:10'),(10,2,'A3a','retrieved','2025-06-19 00:57:37'),(11,2,'A4c','retrieved','2025-06-19 00:57:37'),(12,2,'A5a','retrieved','2025-06-19 00:57:37'),(13,2,'A5b','retrieved','2025-06-19 00:57:37'),(14,2,'A5e','retrieved','2025-06-19 00:57:37'),(15,2,'A5f','retrieved','2025-06-19 00:57:37'),(16,2,'A6a','retrieved','2025-06-19 00:57:37'),(17,1,'A6a','added','2025-06-19 01:01:14'),(18,3,'A1c','retrieved','2025-06-23 16:11:19'),(19,1,'A1c','added','2025-06-23 23:38:40'),(20,3,'A1d','retrieved','2025-06-25 16:31:41'),(21,1,'A1d','added','2025-06-25 16:31:55'),(22,1,'A1a','retrieved','2025-06-25 16:53:08'),(23,1,'A1b','retrieved','2025-06-25 16:53:08'),(24,1,'A1c','retrieved','2025-06-25 16:53:08'),(25,1,'A1d','retrieved','2025-06-25 16:53:08'),(26,1,'A2a','retrieved','2025-06-25 16:53:08'),(27,1,'A2c','retrieved','2025-06-25 16:53:08'),(28,1,'A3b','retrieved','2025-06-25 16:53:08'),(29,1,'A3c','retrieved','2025-06-25 16:53:08'),(30,1,'A3f','retrieved','2025-06-25 16:53:08'),(31,1,'A4a','retrieved','2025-06-25 16:53:08'),(32,1,'A4a','added','2025-06-25 16:56:03'),(33,1,'A1e','added','2025-06-25 22:13:13'),(34,2,'A1f','retrieved','2025-06-26 13:49:23'),(35,1,'A1c','added','2025-06-26 17:06:46'),(36,1,'A1c','retrieved','2025-06-26 17:07:44'),(37,2,'A6c','retrieved','2025-07-19 15:28:05'),(38,2,'A6d','retrieved','2025-07-19 15:28:22'),(39,1,'A1d','added','2025-07-19 15:28:50'),(40,1,'A1d','retrieved','2025-08-26 02:58:07'),(41,3,'A2e','retrieved','2025-08-26 05:13:59'),(42,1,'A4a','retrieved','2025-08-26 21:42:39'),(43,3,'A2f','retrieved','2025-08-27 00:41:50'),(44,3,'A6b','retrieved','2025-08-27 01:07:22'),(46,2,'B2c','ordered','2025-08-27 01:40:31'),(47,2,'B5c','ordered','2025-08-27 02:01:22'),(48,2,'C1c','ordered','2025-08-27 02:30:28'),(49,2,'A1c','added','2025-08-29 16:09:43'),(50,2,'A1c','retrieved','2025-08-29 16:10:25'),(51,2,'C2c','retrieved','2025-08-29 16:10:26'),(52,2,'C7c','ordered','2025-08-29 16:16:27'),(53,2,'D2c','ordered','2025-08-30 14:01:19');
/*!40000 ALTER TABLE `Transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-09 21:07:34
