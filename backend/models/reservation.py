from database.db import execute_query
import random
import string
from datetime import datetime, timedelta


class Reservation:
    @staticmethod
    def generate_code():
        """توليد كود حجز فريد"""
        prefix = "KSU"
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}-{random_part}"

    @staticmethod
    def create(user_id, space_id, notes=None):
        """إنشاء حجز جديد"""
        code = Reservation.generate_code()
        expires_at = datetime.now() + timedelta(hours=2)

        query = """
            INSERT INTO reservations 
            (user_id, space_id, reservation_code, status, expires_at, notes)
            VALUES (%s, %s, %s, 'Pending', %s, %s)
        """
        return execute_query(query, (user_id, space_id, code, expires_at, notes))

    @staticmethod
    def get_by_id(reservation_id):
        """جلب حجز بالمعرف"""
        query = """
            SELECT r.*, 
                   u.username, u.full_name AS user_name, u.email AS user_email,
                   ps.space_code, ps.row_zone, ps.space_number
            FROM reservations r
            JOIN users u ON r.user_id = u.user_id
            JOIN parking_spaces ps ON r.space_id = ps.space_id
            WHERE r.reservation_id = %s
        """
        result = execute_query(query, (reservation_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_user(user_id):
        """جلب حجوزات مستخدم"""
        query = """
            SELECT r.*, 
                   ps.space_code, ps.row_zone, ps.space_number
            FROM reservations r
            JOIN parking_spaces ps ON r.space_id = ps.space_id
            WHERE r.user_id = %s
            ORDER BY r.reserved_at DESC
        """
        return execute_query(query, (user_id,), fetch=True)

    @staticmethod
    def get_all(status=None):
        """جلب جميع الحجوزات (للموظفين)"""
        if status:
            query = """
                SELECT r.*, 
                       u.username, u.full_name AS user_name, u.email AS user_email,
                       ps.space_code, ps.row_zone, ps.space_number
                FROM reservations r
                JOIN users u ON r.user_id = u.user_id
                JOIN parking_spaces ps ON r.space_id = ps.space_id
                WHERE r.status = %s
                ORDER BY r.reserved_at DESC
            """
            return execute_query(query, (status,), fetch=True)
        else:
            query = """
                SELECT r.*, 
                       u.username, u.full_name AS user_name, u.email AS user_email,
                       ps.space_code, ps.row_zone, ps.space_number
                FROM reservations r
                JOIN users u ON r.user_id = u.user_id
                JOIN parking_spaces ps ON r.space_id = ps.space_id
                ORDER BY r.reserved_at DESC
            """
            return execute_query(query, fetch=True)

    @staticmethod
    def get_pending():
        """جلب الحجوزات قيد الانتظار (للموظف)"""
        query = """
            SELECT r.*, 
                   u.username, u.full_name AS user_name, u.email AS user_email,
                   ps.space_code, ps.row_zone, ps.space_number
            FROM reservations r
            JOIN users u ON r.user_id = u.user_id
            JOIN parking_spaces ps ON r.space_id = ps.space_id
            WHERE r.status = 'Pending'
            ORDER BY r.reserved_at ASC
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def update_status(reservation_id, status, confirmed_by=None):
        """تحديث حالة الحجز"""
        if status == 'Confirmed':
            query = """
                UPDATE reservations 
                SET status = %s, confirmed_at = NOW(), confirmed_by = %s
                WHERE reservation_id = %s
            """
            return execute_query(query, (status, confirmed_by, reservation_id))
        else:
            query = """
                UPDATE reservations 
                SET status = %s, confirmed_at = NOW(), confirmed_by = %s
                WHERE reservation_id = %s
            """
            return execute_query(query, (status, confirmed_by, reservation_id))

    @staticmethod
    def cancel(reservation_id, user_id):
        """إلغاء حجز"""
        query = """
            UPDATE reservations 
            SET status = 'Cancelled'
            WHERE reservation_id = %s AND user_id = %s AND status = 'Pending'
        """
        return execute_query(query, (reservation_id, user_id))

    @staticmethod
    def get_stats():
        """إحصائيات الحجوزات"""
        query = """
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed,
                SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
            FROM reservations
        """
        result = execute_query(query, fetch=True)
        return result[0] if result else {
            "total": 0, "pending": 0, "confirmed": 0, 
            "cancelled": 0, "rejected": 0, "completed": 0
        }

    @staticmethod
    def has_active_reservation(user_id):
        """التحقق من وجود حجز نشط"""
        query = """
            SELECT COUNT(*) AS count
            FROM reservations
            WHERE user_id = %s AND status IN ('Pending', 'Confirmed')
        """
        result = execute_query(query, (user_id,), fetch=True)
        return result[0]["count"] > 0 if result else False