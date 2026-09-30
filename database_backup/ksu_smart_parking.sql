-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 24, 2026 at 05:05 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ksu_smart_parking`
--

-- --------------------------------------------------------

--
-- Table structure for table `activity_logs`
--

CREATE TABLE `activity_logs` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `parking_spaces`
--

CREATE TABLE `parking_spaces` (
  `space_id` int(11) NOT NULL,
  `space_code` varchar(10) NOT NULL,
  `row_zone` varchar(10) NOT NULL,
  `space_number` int(11) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `parking_spaces`
--

INSERT INTO `parking_spaces` (`space_id`, `space_code`, `row_zone`, `space_number`, `is_active`) VALUES
(1, 'A1', 'A', 1, 1),
(2, 'A2', 'A', 2, 1),
(3, 'A3', 'A', 3, 1),
(4, 'A4', 'A', 4, 1),
(5, 'A5', 'A', 5, 1),
(6, 'A6', 'A', 6, 1),
(7, 'A7', 'A', 7, 1),
(8, 'A8', 'A', 8, 1),
(9, 'A9', 'A', 9, 1),
(10, 'A10', 'A', 10, 1),
(11, 'B1', 'B', 1, 1),
(12, 'B2', 'B', 2, 1),
(13, 'B3', 'B', 3, 1),
(14, 'B4', 'B', 4, 1),
(15, 'B5', 'B', 5, 1),
(16, 'B6', 'B', 6, 1),
(17, 'B7', 'B', 7, 1),
(18, 'B8', 'B', 8, 1),
(19, 'B9', 'B', 9, 1),
(20, 'B10', 'B', 10, 1),
(21, 'C1', 'C', 1, 1),
(22, 'C2', 'C', 2, 1),
(23, 'C3', 'C', 3, 1),
(24, 'C4', 'C', 4, 1),
(25, 'C5', 'C', 5, 1),
(26, 'C6', 'C', 6, 1),
(27, 'C7', 'C', 7, 1),
(28, 'C8', 'C', 8, 1),
(29, 'C9', 'C', 9, 1),
(30, 'C10', 'C', 10, 1);

-- --------------------------------------------------------

--
-- Table structure for table `parking_status`
--

CREATE TABLE `parking_status` (
  `status_id` int(11) NOT NULL,
  `space_id` int(11) NOT NULL,
  `status` enum('Available','Occupied') NOT NULL DEFAULT 'Available',
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `updated_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `parking_status`
--

INSERT INTO `parking_status` (`status_id`, `space_id`, `status`, `updated_at`, `updated_by`) VALUES
(1, 1, 'Available', '2026-09-24 14:45:49', NULL),
(2, 10, 'Available', '2026-09-24 14:45:49', NULL),
(3, 2, 'Available', '2026-09-24 14:45:49', NULL),
(4, 3, 'Available', '2026-09-24 14:45:49', NULL),
(5, 4, 'Available', '2026-09-24 14:45:49', NULL),
(6, 5, 'Available', '2026-09-24 14:45:49', NULL),
(7, 6, 'Available', '2026-09-24 14:45:49', NULL),
(8, 7, 'Available', '2026-09-24 14:45:49', NULL),
(9, 8, 'Available', '2026-09-24 14:45:49', NULL),
(10, 9, 'Available', '2026-09-24 14:45:49', NULL),
(11, 11, 'Available', '2026-09-24 14:45:49', NULL),
(12, 20, 'Available', '2026-09-24 14:45:49', NULL),
(13, 12, 'Available', '2026-09-24 14:45:49', NULL),
(14, 13, 'Available', '2026-09-24 14:45:49', NULL),
(15, 14, 'Available', '2026-09-24 14:45:49', NULL),
(16, 15, 'Available', '2026-09-24 14:45:49', NULL),
(17, 16, 'Available', '2026-09-24 14:45:49', NULL),
(18, 17, 'Available', '2026-09-24 14:45:49', NULL),
(19, 18, 'Available', '2026-09-24 14:45:49', NULL),
(20, 19, 'Available', '2026-09-24 14:45:49', NULL),
(21, 21, 'Available', '2026-09-24 14:45:49', NULL),
(22, 30, 'Available', '2026-09-24 14:45:49', NULL),
(23, 22, 'Available', '2026-09-24 14:45:49', NULL),
(24, 23, 'Available', '2026-09-24 14:45:49', NULL),
(25, 24, 'Available', '2026-09-24 14:45:49', NULL),
(26, 25, 'Available', '2026-09-24 14:45:49', NULL),
(27, 26, 'Available', '2026-09-24 14:45:49', NULL),
(28, 27, 'Available', '2026-09-24 14:45:49', NULL),
(29, 28, 'Available', '2026-09-24 14:45:49', NULL),
(30, 29, 'Available', '2026-09-24 14:45:49', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `permissions`
--

CREATE TABLE `permissions` (
  `permission_id` int(11) NOT NULL,
  `permission_name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `permissions`
--

INSERT INTO `permissions` (`permission_id`, `permission_name`, `description`) VALUES
(1, 'view_parking', 'عرض حالة المواقف'),
(2, 'update_parking', 'تعديل حالة المواقف'),
(3, 'manage_users', 'إدارة المستخدمين'),
(4, 'view_logs', 'عرض سجلات النشاط');

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`role_id`, `role_name`, `description`) VALUES
(1, 'admin', 'مدير النظام - صلاحيات كاملة'),
(2, 'staff', 'موظف - صلاحيات محدودة'),
(3, 'visitor', 'زائر - عرض فقط');

-- --------------------------------------------------------

--
-- Table structure for table `role_permissions`
--

CREATE TABLE `role_permissions` (
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `role_permissions`
--

INSERT INTO `role_permissions` (`role_id`, `permission_id`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(2, 1),
(2, 2),
(3, 1);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `role_id` int(11) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password_hash`, `full_name`, `email`, `role_id`, `is_active`, `created_at`, `last_login`) VALUES
(1, 'admin', 'HASH_PLACEHOLDER', 'مدير النظام', 'admin@ksu.edu.sa', 1, 1, '2026-09-24 14:45:49', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `parking_spaces`
--
ALTER TABLE `parking_spaces`
  ADD PRIMARY KEY (`space_id`),
  ADD UNIQUE KEY `space_code` (`space_code`);

--
-- Indexes for table `parking_status`
--
ALTER TABLE `parking_status`
  ADD PRIMARY KEY (`status_id`),
  ADD KEY `space_id` (`space_id`),
  ADD KEY `updated_by` (`updated_by`);

--
-- Indexes for table `permissions`
--
ALTER TABLE `permissions`
  ADD PRIMARY KEY (`permission_id`),
  ADD UNIQUE KEY `permission_name` (`permission_name`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `role_name` (`role_name`);

--
-- Indexes for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD PRIMARY KEY (`role_id`,`permission_id`),
  ADD KEY `permission_id` (`permission_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `role_id` (`role_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activity_logs`
--
ALTER TABLE `activity_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `parking_spaces`
--
ALTER TABLE `parking_spaces`
  MODIFY `space_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `parking_status`
--
ALTER TABLE `parking_status`
  MODIFY `status_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `permissions`
--
ALTER TABLE `permissions`
  MODIFY `permission_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `parking_status`
--
ALTER TABLE `parking_status`
  ADD CONSTRAINT `parking_status_ibfk_1` FOREIGN KEY (`space_id`) REFERENCES `parking_spaces` (`space_id`),
  ADD CONSTRAINT `parking_status_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`),
  ADD CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- =========================================
-- KSU Smart Parking v2.0
-- إضافة نظام الحجوزات
-- =========================================

USE ksu_smart_parking;

-- =========================================
-- 1. جدول الحجوزات
-- =========================================
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    space_id INT NOT NULL,
    reservation_code VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('Pending', 'Confirmed', 'Cancelled', 'Completed', 'Rejected') 
           NOT NULL DEFAULT 'Pending',
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL,
    confirmed_by INT NULL,
    expires_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (space_id) REFERENCES parking_spaces(space_id),
    FOREIGN KEY (confirmed_by) REFERENCES users(user_id)
);

-- =========================================
-- 2. إضافة عمود reservation_id لجدول المواقف
-- =========================================
ALTER TABLE parking_status 
ADD COLUMN current_reservation_id INT NULL,
ADD FOREIGN KEY (current_reservation_id) REFERENCES reservations(reservation_id);

-- =========================================
-- 3. فهارس للأداء
-- =========================================
CREATE INDEX idx_reservations_user ON reservations(user_id);
CREATE INDEX idx_reservations_space ON reservations(space_id);
CREATE INDEX idx_reservations_status ON reservations(status);

-- =========================================
-- 4. تحديث دور الزائر للسماح بالحجز
-- =========================================
INSERT INTO permissions (permission_name, description) VALUES
('make_reservation', 'إنشاء حجز'),
('view_own_reservations', 'عرض الحجوزات الخاصة'),
('manage_reservations', 'إدارة الحجوزات')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- منح الزوار صلاحية الحجز
INSERT IGNORE INTO role_permissions (role_id, permission_id) 
SELECT 3, permission_id FROM permissions WHERE permission_name IN ('make_reservation', 'view_own_reservations');

-- منح الموظفين صلاحية إدارة الحجوزات
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT 2, permission_id FROM permissions WHERE permission_name IN ('make_reservation', 'view_own_reservations', 'manage_reservations');

-- منح المدير كل الصلاحيات
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT 1, permission_id FROM permissions WHERE permission_name IN ('make_reservation', 'view_own_reservations', 'manage_reservations');