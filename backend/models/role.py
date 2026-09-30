from database.db import execute_query

class Role:
    @staticmethod
    def get_all():
        query = "SELECT * FROM roles ORDER BY role_id"
        return execute_query(query, fetch=True)

    @staticmethod
    def get_permissions(role_id):
        query = """
            SELECT p.permission_id, p.permission_name, p.description
            FROM permissions p
            JOIN role_permissions rp ON p.permission_id = rp.permission_id
            WHERE rp.role_id = %s
        """
        return execute_query(query, (role_id,), fetch=True)

    @staticmethod
    def get_all_permissions():
        query = "SELECT * FROM permissions ORDER BY permission_id"
        return execute_query(query, fetch=True)