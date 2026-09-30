from database.db import execute_query
import random
import string
from datetime import datetime, timedelta


# ============================================
# دالة تحويل الزيارة إلى JSON
# ============================================
def serialize_visit(visit):
    """تحويل الحقول الخاصة في الزيارة إلى صيغة قابلة للـ JSON"""
    if not visit:
        return visit

    # timedelta → seconds (باستثناء scheduled_time)
    for key, value in list(visit.items()):
        if isinstance(value, timedelta):
            if key == "scheduled_time":
                # تحويل إلى HH:MM
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                visit[key] = f"{hours:02d}:{minutes:02d}"
            else:
                visit[key] = int(value.total_seconds())

    # date/time → string
    for key in ["scheduled_date", "requested_at", "approved_at",
                "entry_time", "exit_time", "created_at"]:
        if key in visit and visit[key] is not None:
            if hasattr(visit[key], "isoformat"):
                visit[key] = str(visit[key])

    return visit


def serialize_visits(visits):
    """تحويل قائمة زيارات إلى JSON"""
    if not visits:
        return []
    return [serialize_visit(v) for v in visits]


# ============================================
# كلاس الزيارة
# ============================================
class Visit:
    @staticmethod
    def generate_code():
        """توليد كود زيارة فريد"""
        prefix = "VIS"
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}-{random_part}"

    @staticmethod
    def create(visitor_id, host_id, building_id, purpose, scheduled_date,
               scheduled_time, vehicle_plate, vehicle_type, visitors_count=1,
               expected_duration=60):
        """إنشاء طلب زيارة جديد"""
        code = Visit.generate_code()

        query = """
            INSERT INTO visits 
            (visitor_id, host_id, building_id, visit_code, purpose,
             scheduled_date, scheduled_time, vehicle_plate, vehicle_type,
             visitors_count, expected_duration, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """
        return execute_query(query, (
            visitor_id, host_id, building_id, code, purpose,
            scheduled_date, scheduled_time, vehicle_plate, vehicle_type,
            visitors_count, expected_duration
        ))

    @staticmethod
    def get_by_id(visit_id):
        """جلب زيارة بالمعرف"""
        query = """
            SELECT v.*, 
                   u.username AS visitor_username, u.full_name AS visitor_name,
                   u.email AS visitor_email,
                   hu.username AS host_username, hu.full_name AS host_name,
                   h.department, h.office_number,
                   b.building_code, b.building_name
            FROM visits v
            JOIN users u ON v.visitor_id = u.user_id
            JOIN hosts h ON v.host_id = h.host_id
            JOIN users hu ON h.user_id = hu.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            WHERE v.visit_id = %s
        """
        result = execute_query(query, (visit_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_code(visit_code):
        """جلب زيارة بالكود"""
        query = """
            SELECT v.*, 
                   u.username AS visitor_username, u.full_name AS visitor_name,
                   u.email AS visitor_email,
                   hu.full_name AS host_name,
                   b.building_code, b.building_name
            FROM visits v
            JOIN users u ON v.visitor_id = u.user_id
            JOIN hosts h ON v.host_id = h.host_id
            JOIN users hu ON h.user_id = hu.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            WHERE v.visit_code = %s
        """
        result = execute_query(query, (visit_code,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_visitor(visitor_id):
        """جلب زيارات زائر"""
        query = """
            SELECT v.*, 
                   hu.full_name AS host_name,
                   b.building_code, b.building_name,
                   p.permit_code, p.qr_data
            FROM visits v
            JOIN hosts h ON v.host_id = h.host_id
            JOIN users hu ON h.user_id = hu.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            LEFT JOIN permits p ON v.visit_id = p.visit_id
            WHERE v.visitor_id = %s
            ORDER BY v.scheduled_date DESC, v.scheduled_time DESC
        """
        return execute_query(query, (visitor_id,), fetch=True)

    @staticmethod
    def get_by_host(host_id):
        """جلب زيارات مضيف"""
        query = """
            SELECT v.*, 
                   u.full_name AS visitor_name, u.email AS visitor_email,
                   b.building_code, b.building_name
            FROM visits v
            JOIN users u ON v.visitor_id = u.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            WHERE v.host_id = %s
            ORDER BY v.status, v.scheduled_date DESC, v.scheduled_time DESC
        """
        return execute_query(query, (host_id,), fetch=True)

    @staticmethod
    def get_pending_by_host(host_id):
        """جلب الزيارات قيد الانتظار لمضيف"""
        query = """
            SELECT v.*, 
                   u.full_name AS visitor_name, u.email AS visitor_email,
                   b.building_code, b.building_name
            FROM visits v
            JOIN users u ON v.visitor_id = u.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            WHERE v.host_id = %s AND v.status = 'Pending'
            ORDER BY v.scheduled_date ASC, v.scheduled_time ASC
        """
        return execute_query(query, (host_id,), fetch=True)

    @staticmethod
    def get_all(status=None):
        """جلب جميع الزيارات"""
        if status:
            query = """
                SELECT v.*, 
                       u.full_name AS visitor_name, u.email AS visitor_email,
                       hu.full_name AS host_name,
                       b.building_code, b.building_name
                FROM visits v
                JOIN users u ON v.visitor_id = u.user_id
                JOIN hosts h ON v.host_id = h.host_id
                JOIN users hu ON h.user_id = hu.user_id
                LEFT JOIN buildings b ON v.building_id = b.building_id
                WHERE v.status = %s
                ORDER BY v.scheduled_date DESC
            """
            return execute_query(query, (status,), fetch=True)
        else:
            query = """
                SELECT v.*, 
                       u.full_name AS visitor_name, u.email AS visitor_email,
                       hu.full_name AS host_name,
                       b.building_code, b.building_name
                FROM visits v
                JOIN users u ON v.visitor_id = u.user_id
                JOIN hosts h ON v.host_id = h.host_id
                JOIN users hu ON h.user_id = hu.user_id
                LEFT JOIN buildings b ON v.building_id = b.building_id
                ORDER BY v.requested_at DESC
            """
            return execute_query(query, fetch=True)

    @staticmethod
    def approve(visit_id, host_notes=None):
        """موافقة على زيارة"""
        query = """
            UPDATE visits 
            SET status = 'Approved', approved_at = NOW(), host_notes = %s
            WHERE visit_id = %s AND status = 'Pending'
        """
        return execute_query(query, (host_notes, visit_id))

    @staticmethod
    def reject(visit_id, reason):
        """رفض زيارة"""
        query = """
            UPDATE visits 
            SET status = 'Rejected', approved_at = NOW(), rejection_reason = %s
            WHERE visit_id = %s AND status = 'Pending'
        """
        return execute_query(query, (reason, visit_id))

    @staticmethod
    def cancel(visit_id, visitor_id):
        """إلغاء زيارة"""
        query = """
            UPDATE visits 
            SET status = 'Cancelled'
            WHERE visit_id = %s AND visitor_id = %s 
            AND status IN ('Pending', 'Approved')
        """
        return execute_query(query, (visit_id, visitor_id))

    @staticmethod
    def log_entry(visit_id, verified_by, gate_number=None, notes=None):
        """تسجيل دخول"""
        query = """
            UPDATE visits 
            SET entry_time = NOW(), entry_by = %s, status = 'Completed'
            WHERE visit_id = %s AND status = 'Approved'
        """
        return execute_query(query, (verified_by, visit_id))

    @staticmethod
    def log_exit(visit_id, verified_by, gate_number=None, notes=None):
        """تسجيل خروج"""
        query = """
            UPDATE visits 
            SET exit_time = NOW(), exit_by = %s
            WHERE visit_id = %s
        """
        return execute_query(query, (verified_by, visit_id))

    @staticmethod
    def get_stats():
        """إحصائيات الزيارات"""
        query = """
            SELECT 
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END), 0) AS pending,
                COALESCE(SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END), 0) AS approved,
                COALESCE(SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END), 0) AS rejected,
                COALESCE(SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed,
                COALESCE(SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END), 0) AS cancelled
            FROM visits
        """
        result = execute_query(query, fetch=True)
        if result and result[0]:
            return result[0]
        return {
            "total": 0, "pending": 0, "approved": 0,
            "rejected": 0, "completed": 0, "cancelled": 0
        }