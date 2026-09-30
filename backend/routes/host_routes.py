from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.host import Host
from models.visit import Visit, serialize_visit
from security.decorators import role_required
from security.logging import log_activity

host_bp = Blueprint("host", __name__)


def serialize_visits(visits):
    """تحويل قائمة زيارات"""
    if not visits:
        return []
    return [serialize_visit(v) for v in visits]


@host_bp.route("/", methods=["GET"])
@role_required("admin", "staff")
def get_all_hosts():
    """جلب جميع المضيفين (admin/staff)"""
    hosts = Host.get_all()
    return jsonify({"hosts": hosts, "count": len(hosts)}), 200


@host_bp.route("/public", methods=["GET"])
def get_public_hosts():
    """جلب المضيفين (للزوار - عام)"""
    hosts = Host.get_all()
    public_hosts = [
        {
            "host_id": h["host_id"],
            "full_name": h["full_name"],
            "department": h.get("department"),
            "building_name": h.get("building_name")
        }
        for h in hosts
    ]
    return jsonify({"hosts": public_hosts, "count": len(public_hosts)}), 200


@host_bp.route("/me", methods=["GET"])
@role_required("host", "admin")
def get_my_host_profile():
    """جلب ملفي كمضيف"""
    user_id = int(get_jwt_identity())
    host = Host.get_by_user_id(user_id)
    if not host:
        return jsonify({"error": "لست مضيفاً مسجلاً"}), 404
    return jsonify({"host": host}), 200


@host_bp.route("/me/visits", methods=["GET"])
@role_required("host", "admin")
def get_my_visits():
    """جلب زياراتي كمضيف"""
    user_id = int(get_jwt_identity())
    host = Host.get_by_user_id(user_id)
    if not host:
        return jsonify({"error": "لست مضيفاً مسجلاً"}), 404
    visits = Visit.get_by_host(host["host_id"])
    visits = serialize_visits(visits)
    return jsonify({"visits": visits, "count": len(visits)}), 200


@host_bp.route("/me/pending", methods=["GET"])
@role_required("host", "admin")
def get_my_pending_visits():
    """جلب الزيارات قيد الانتظار"""
    user_id = int(get_jwt_identity())
    host = Host.get_by_user_id(user_id)
    if not host:
        return jsonify({"error": "لست مضيفاً مسجلاً"}), 404
    visits = Visit.get_pending_by_host(host["host_id"])
    visits = serialize_visits(visits)
    return jsonify({"visits": visits, "count": len(visits)}), 200


@host_bp.route("/<int:host_id>", methods=["GET"])
@role_required("admin", "staff", "host")
def get_host(host_id):
    """جلب مضيف بالمعرف"""
    host = Host.get_by_id(host_id)
    if not host:
        return jsonify({"error": "المضيف غير موجود"}), 404
    return jsonify({"host": host}), 200


@host_bp.route("/", methods=["POST"])
@role_required("admin")
def create_host():
    """إنشاء مضيف جديد (admin)"""
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "معرف المستخدم مطلوب"}), 400

    existing = Host.get_by_user_id(user_id)
    if existing:
        return jsonify({"error": "المستخدم مضيف بالفعل"}), 409

    host_id = Host.create(
        user_id=user_id,
        department=data.get("department"),
        office_number=data.get("office_number"),
        building_id=data.get("building_id"),
        phone=data.get("phone")
    )

    admin_id = int(get_jwt_identity())
    log_activity(admin_id, "CREATE_HOST", f"إنشاء مضيف: {user_id}")

    return jsonify({"message": "تم إنشاء المضيف بنجاح", "host_id": host_id}), 201


@host_bp.route("/<int:host_id>", methods=["PUT"])
@role_required("admin")
def update_host(host_id):
    """تحديث بيانات مضيف (admin)"""
    data = request.get_json()
    Host.update(
        host_id=host_id,
        department=data.get("department"),
        office_number=data.get("office_number"),
        building_id=data.get("building_id"),
        phone=data.get("phone"),
        is_available=data.get("is_available", True)
    )
    admin_id = int(get_jwt_identity())
    log_activity(admin_id, "UPDATE_HOST", f"تحديث مضيف: {host_id}")
    return jsonify({"message": "تم تحديث المضيف بنجاح"}), 200


@host_bp.route("/<int:host_id>", methods=["DELETE"])
@role_required("admin")
def delete_host(host_id):
    """حذف مضيف (admin)"""
    Host.delete(host_id)
    admin_id = int(get_jwt_identity())
    log_activity(admin_id, "DELETE_HOST", f"حذف مضيف: {host_id}")
    return jsonify({"message": "تم حذف المضيف بنجاح"}), 200