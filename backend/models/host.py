from database.db import execute_query


class Host:
    @staticmethod
    def get_all():
        """جلب جميع المضيفين"""
        query = """
            SELECT h.host_id, h.user_id, h.department, h.office_number,
                   h.phone, h.is_available,
                   u.username, u.full_name, u.email,
                   b.building_code, b.building_name
            FROM hosts h
            JOIN users u ON h.user_id = u.user_id
            LEFT JOIN buildings b ON h.building_id = b.building_id
            ORDER BY u.full_name
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def get_by_id(host_id):
        """جلب مضيف بالمعرف"""
        query = """
            SELECT h.*, u.username, u.full_name, u.email,
                   b.building_code, b.building_name
            FROM hosts h
            JOIN users u ON h.user_id = u.user_id
            LEFT JOIN buildings b ON h.building_id = b.building_id
            WHERE h.host_id = %s
        """
        result = execute_query(query, (host_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_user_id(user_id):
        """جلب مضيف بمعرف المستخدم"""
        query = """
            SELECT h.*, u.username, u.full_name, u.email,
                   b.building_code, b.building_name
            FROM hosts h
            JOIN users u ON h.user_id = u.user_id
            LEFT JOIN buildings b ON h.building_id = b.building_id
            WHERE h.user_id = %s
        """
        result = execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def create(user_id, department=None, office_number=None, building_id=None, phone=None):
        """إنشاء مضيف جديد"""
        query = """
            INSERT INTO hosts (user_id, department, office_number, building_id, phone)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (user_id, department, office_number, building_id, phone))

    @staticmethod
    def update(host_id, department, office_number, building_id, phone, is_available):
        """تحديث بيانات مضيف"""
        query = """
            UPDATE hosts
            SET department = %s, office_number = %s, building_id = %s,
                phone = %s, is_available = %s
            WHERE host_id = %s
        """
        return execute_query(query, (department, office_number, building_id,
                                      phone, is_available, host_id))

    @staticmethod
    def delete(host_id):
        """حذف مضيف"""
        query = "DELETE FROM hosts WHERE host_id = %s"
        return execute_query(query, (host_id,))