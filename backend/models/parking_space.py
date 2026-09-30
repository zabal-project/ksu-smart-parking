from database.db import execute_query

class ParkingSpace:
    @staticmethod
    def get_all_with_status():
        query = """
            SELECT ps.space_id, ps.space_code, ps.row_zone, ps.space_number,
                   st.status, st.updated_at
            FROM parking_spaces ps
            JOIN parking_status st ON ps.space_id = st.space_id
            WHERE ps.is_active = TRUE
            ORDER BY ps.row_zone, ps.space_number
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def get_by_id(space_id):
        query = """
            SELECT ps.space_id, ps.space_code, ps.row_zone, ps.space_number,
                   st.status, st.updated_at
            FROM parking_spaces ps
            JOIN parking_status st ON ps.space_id = st.space_id
            WHERE ps.space_id = %s
        """
        result = execute_query(query, (space_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_available_zones():
        query = """
            SELECT ps.row_zone, COUNT(*) AS available_count,
                   (SELECT COUNT(*) FROM parking_spaces WHERE row_zone = ps.row_zone) AS total_count
            FROM parking_spaces ps
            JOIN parking_status st ON ps.space_id = st.space_id
            WHERE st.status = 'Available' AND ps.is_active = TRUE
            GROUP BY ps.row_zone
            ORDER BY ps.row_zone
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def update_status(space_id, status, user_id):
        query = """
            UPDATE parking_status
            SET status = %s, updated_by = %s, updated_at = NOW()
            WHERE space_id = %s
        """
        return execute_query(query, (status, user_id, space_id))

    @staticmethod
    def get_stats():
        query = """
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN st.status = 'Available' THEN 1 ELSE 0 END) AS available,
                SUM(CASE WHEN st.status = 'Occupied' THEN 1 ELSE 0 END) AS occupied
            FROM parking_spaces ps
            JOIN parking_status st ON ps.space_id = st.space_id
            WHERE ps.is_active = TRUE
        """
        result = execute_query(query, fetch=True)
        return result[0] if result else {"total": 0, "available": 0, "occupied": 0}
    @staticmethod
    def get_available_spaces():
        """جلب المواقف المتاحة فقط"""
        query = """
            SELECT ps.space_id, ps.space_code, ps.row_zone, ps.space_number,
                   st.status, st.updated_at
            FROM parking_spaces ps
            JOIN parking_status st ON ps.space_id = st.space_id
            WHERE ps.is_active = TRUE AND st.status = 'Available'
            ORDER BY ps.row_zone, ps.space_number
        """
        return execute_query(query, fetch=True)

    @staticmethod
    def get_zone_stats():
        query = """
            SELECT 
                ps.row_zone,
                COUNT(*) AS total,
                SUM(CASE WHEN st.status = 'Available' THEN 1 ELSE 0 END) AS available,
                SUM(CASE WHEN st.status = 'Occupied' THEN 1 ELSE 0 END) AS occupied
            FROM parking_spaces ps
            JOIN parking_status st ON ps.space_id = st.space_id
            WHERE ps.is_active = TRUE
            GROUP BY ps.row_zone
            ORDER BY ps.row_zone
        """
        
        return execute_query(query, fetch=True)