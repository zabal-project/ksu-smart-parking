from database.db import execute_query

class ActivityLog:
    @staticmethod
    def create(user_id, action, details, ip_address=None):
        query = """
            INSERT INTO activity_logs (user_id, action, details, ip_address)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (user_id, action, details, ip_address))

    @staticmethod
    def get_all(limit=100, offset=0):
        query = """
            SELECT al.log_id, u.username, al.action, al.details,
                   al.ip_address, al.created_at
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.user_id
            ORDER BY al.created_at DESC
            LIMIT %s OFFSET %s
        """
        return execute_query(query, (limit, offset), fetch=True)

    @staticmethod
    def get_by_user(user_id, limit=50):
        query = """
            SELECT al.log_id, u.username, al.action, al.details,
                   al.ip_address, al.created_at
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.user_id
            WHERE al.user_id = %s
            ORDER BY al.created_at DESC
            LIMIT %s
        """
        return execute_query(query, (user_id, limit), fetch=True)

    @staticmethod
    def get_count():
        query = "SELECT COUNT(*) AS total FROM activity_logs"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0