from database.db import execute_query


class Building:
    @staticmethod
    def get_all():
        """جلب جميع المباني"""
        query = """
            SELECT building_id, building_code, building_name, building_name_en,
                   description, latitude, longitude, is_active
            FROM buildings
            WHERE is_active = TRUE
            ORDER BY building_name
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def get_by_id(building_id):
        """جلب مبنى بالمعرف"""
        query = "SELECT * FROM buildings WHERE building_id = %s"
        result = execute_query(query, (building_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_code(building_code):
        """جلب مبنى بالكود"""
        query = "SELECT * FROM buildings WHERE building_code = %s"
        result = execute_query(query, (building_code,), fetch=True)
        return result[0] if result else None