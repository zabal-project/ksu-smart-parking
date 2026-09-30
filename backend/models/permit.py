from database.db import execute_query
import random
import string
import json
from datetime import datetime, timedelta


class Permit:
    @staticmethod
    def generate_code():
        """توليد كود تصريح فريد"""
        prefix = "PRM"
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{prefix}-{random_part}"

    @staticmethod
    def generate_qr_data(visit):
        """توليد بيانات QR Code"""
        qr_payload = {
            "permit_code": Permit.generate_code(),
            "visit_code": visit["visit_code"],
            "visitor_name": visit.get("visitor_name", ""),
            "vehicle_plate": visit.get("vehicle_plate", ""),
            "scheduled_date": str(visit.get("scheduled_date", "")),
            "scheduled_time": str(visit.get("scheduled_time", "")),
            "building": visit.get("building_name", ""),
            "issued_at": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        return json.dumps(qr_payload, ensure_ascii=False)

    @staticmethod
    def create(visit_id, visit_data):
        """إنشاء تصريح لزيارة"""
        permit_code = Permit.generate_code()
        qr_data = Permit.generate_qr_data(visit_data)
        expires_at = datetime.now() + timedelta(hours=24)

        query = """
            INSERT INTO permits (visit_id, permit_code, qr_data, expires_at)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (visit_id, permit_code, qr_data, expires_at))

    @staticmethod
    def get_by_visit(visit_id):
        """جلب تصريح بالزيارة"""
        query = "SELECT * FROM permits WHERE visit_id = %s"
        result = execute_query(query, (visit_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_by_code(permit_code):
        """جلب تصريح بالكود"""
        query = """
            SELECT p.*, 
                   v.visit_code, v.visitor_id, v.status AS visit_status,
                   v.vehicle_plate, v.scheduled_date, v.scheduled_time,
                   u.full_name AS visitor_name,
                   b.building_name
            FROM permits p
            JOIN visits v ON p.visit_id = v.visit_id
            JOIN users u ON v.visitor_id = u.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            WHERE p.permit_code = %s
        """
        result = execute_query(query, (permit_code,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def mark_as_used(permit_id):
        """تحديد التصريح كمستخدم"""
        query = """
            UPDATE permits 
            SET is_used = TRUE, used_at = NOW()
            WHERE permit_id = %s
        """
        return execute_query(query, (permit_id,))

    @staticmethod
    def verify(permit_code):
        """التحقق من صحة تصريح"""
        permit = Permit.get_by_code(permit_code)
        if not permit:
            return {"valid": False, "reason": "التصريح غير موجود"}

        if permit["is_used"]:
            return {"valid": False, "reason": "تم استخدام التصريح مسبقاً"}

        if permit["visit_status"] not in ["Approved", "Completed"]:
            return {"valid": False, "reason": f"حالة الزيارة: {permit['visit_status']}"}

        if permit["expires_at"] and permit["expires_at"] < datetime.now():
            return {"valid": False, "reason": "انتهت صلاحية التصريح"}

        return {"valid": True, "permit": permit}

    @staticmethod
    def get_all():
        """جلب جميع التصاريح"""
        query = """
            SELECT p.*, 
                   v.visit_code, v.visitor_id,
                   u.full_name AS visitor_name,
                   b.building_name
            FROM permits p
            JOIN visits v ON p.visit_id = v.visit_id
            JOIN users u ON v.visitor_id = u.user_id
            LEFT JOIN buildings b ON v.building_id = b.building_id
            ORDER BY p.issued_at DESC
        """
        return execute_query(query, fetch=True)