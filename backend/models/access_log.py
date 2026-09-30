from database.db import execute_query


class AccessLog:
    @staticmethod
    def create(visit_id, action, verified_by, gate_number=None, vehicle_plate=None, notes=None):
        """تسجيل عملية دخول أو خروج"""
        query = """
            INSERT INTO access_logs (visit_id, action, verified_by, gate_number, vehicle_plate, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (visit_id, action, verified_by, gate_number, vehicle_plate, notes))

    @staticmethod
    def get_by_visit(visit_id):
        """جلب سجلات زيارة"""
        query = """
            SELECT al.*, u.full_name AS verified_by_name
            FROM access_logs al
            JOIN users u ON al.verified_by = u.user_id
            WHERE al.visit_id = %s
            ORDER BY al.created_at
        """
        return execute_query(query, (visit_id,), fetch=True)

    @staticmethod
    def get_recent(limit=100):
        """جلب أحدث السجلات"""
        query = """
            SELECT al.*, 
                   u.full_name AS verified_by_name,
                   v.visit_code,
                   vu.full_name AS visitor_name,
                   v.vehicle_plate
            FROM access_logs al
            JOIN users u ON al.verified_by = u.user_id
            JOIN visits v ON al.visit_id = v.visit_id
            JOIN users vu ON v.visitor_id = vu.user_id
            ORDER BY al.created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch=True)

    @staticmethod
    def get_today():
        """سجلات اليوم"""
        query = """
            SELECT al.*, 
                   u.full_name AS verified_by_name,
                   v.visit_code,
                   vu.full_name AS visitor_name
            FROM access_logs al
            JOIN users u ON al.verified_by = u.user_id
            JOIN visits v ON al.visit_id = v.visit_id
            JOIN users vu ON v.visitor_id = vu.user_id
            WHERE DATE(al.created_at) = CURDATE()
            ORDER BY al.created_at DESC
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def get_stats():
        """إحصائيات الدخول والخروج (بدون null)"""
        query = """
            SELECT 
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN action = 'Entry' THEN 1 ELSE 0 END), 0) AS entries,
                COALESCE(SUM(CASE WHEN action = 'Exit' THEN 1 ELSE 0 END), 0) AS exits,
                COALESCE(SUM(CASE WHEN DATE(created_at) = CURDATE() THEN 1 ELSE 0 END), 0) AS today
            FROM access_logs
        """
        result = execute_query(query, fetch=True)
        if result and result[0]:
            return result[0]
        return {"total": 0, "entries": 0, "exits": 0, "today": 0}