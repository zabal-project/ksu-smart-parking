from database.db import execute_query
from security.auth import hash_password

class User:
    @staticmethod
    def get_by_username(username):
        query = """
            SELECT u.user_id, u.username, u.password_hash, u.full_name,
                   u.email, u.role_id, r.role_name, u.is_active
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.username = %s
        """
        result = execute_query(query, (username,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_id(user_id):
        query = """
            SELECT u.user_id, u.username, u.full_name, u.email,
                   u.role_id, r.role_name, u.is_active, u.created_at, u.last_login
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.user_id = %s
        """
        result = execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def update_last_login(user_id):
        query = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
        execute_query(query, (user_id,))

    @staticmethod
    def get_all():
        query = """
            SELECT u.user_id, u.username, u.full_name, u.email,
                   r.role_name, u.is_active, u.created_at, u.last_login
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            ORDER BY u.created_at DESC
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def create(username, password, full_name, email, role_id):
        password_hash = hash_password(password)
        query = """
            INSERT INTO users (username, password_hash, full_name, email, role_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (username, password_hash, full_name, email, role_id))

    @staticmethod
    def update(user_id, full_name, email, role_id, is_active):
        query = """
            UPDATE users
            SET full_name = %s, email = %s, role_id = %s, is_active = %s
            WHERE user_id = %s
        """
        return execute_query(query, (full_name, email, role_id, is_active, user_id))

    @staticmethod
    def update_password(user_id, new_password):
        password_hash = hash_password(new_password)
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        return execute_query(query, (password_hash, user_id))

    @staticmethod
    def delete(user_id):
        query = "DELETE FROM users WHERE user_id = %s"
        return execute_query(query, (user_id,))

    @staticmethod
    def toggle_active(user_id):
        query = "UPDATE users SET is_active = NOT is_active WHERE user_id = %s"
        return execute_query(query, (user_id,))