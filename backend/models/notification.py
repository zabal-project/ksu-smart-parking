from database.db import execute_query


class Notification:
    @staticmethod
    def create(user_id, title, message, type="info", related_visit_id=None):
        """إنشاء إشعار جديد"""
        query = """
            INSERT INTO notifications (user_id, title, message, type, related_visit_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (user_id, title, message, type, related_visit_id))

    @staticmethod
    def get_by_user(user_id, unread_only=False):
        """جلب إشعارات مستخدم"""
        if unread_only:
            query = """
                SELECT * FROM notifications
                WHERE user_id = %s AND is_read = FALSE
                ORDER BY created_at DESC
            """
        else:
            query = """
                SELECT * FROM notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 50
            """
        return execute_query(query, (user_id,), fetch=True)

    @staticmethod
    def get_unread_count(user_id):
        """عدد الإشعارات غير المقروءة"""
        query = "SELECT COUNT(*) AS count FROM notifications WHERE user_id = %s AND is_read = FALSE"
        result = execute_query(query, (user_id,), fetch=True)
        return result[0]["count"] if result else 0

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """تحديد إشعار كمقروء"""
        query = """
            UPDATE notifications 
            SET is_read = TRUE
            WHERE notification_id = %s AND user_id = %s
        """
        return execute_query(query, (notification_id, user_id))

    @staticmethod
    def mark_all_as_read(user_id):
        """تحديد كل الإشعارات كمقروءة"""
        query = "UPDATE notifications SET is_read = TRUE WHERE user_id = %s"
        return execute_query(query, (user_id,))

    @staticmethod
    def delete(notification_id, user_id):
        """حذف إشعار"""
        query = "DELETE FROM notifications WHERE notification_id = %s AND user_id = %s"
        return execute_query(query, (notification_id, user_id))