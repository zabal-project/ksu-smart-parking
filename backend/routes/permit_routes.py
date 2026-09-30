from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.permit import Permit
from models.visit import Visit
from security.decorators import role_required
from security.logging import log_activity

permit_bp = Blueprint("permit", __name__)


@permit_bp.route("/verify/<string:permit_code>", methods=["GET"])
@role_required("security", "admin", "staff")
def verify_permit(permit_code):
    """التحقق من صحة تصريح (للأمن)"""
    result = Permit.verify(permit_code)
    return jsonify(result), 200 if result["valid"] else 400


@permit_bp.route("/visit/<int:visit_id>", methods=["GET"])
@role_required("visitor", "host", "admin", "staff", "security")
def get_permit_by_visit(visit_id):
    """جلب تصريح زيارة"""
    permit = Permit.get_by_visit(visit_id)
    if not permit:
        return jsonify({"error": "لا يوجد تصريح لهذه الزيارة"}), 404
    return jsonify({"permit": permit}), 200


@permit_bp.route("/code/<string:permit_code>", methods=["GET"])
@role_required("security", "admin", "staff")
def get_permit_by_code(permit_code):
    """جلب تصريح بالكود"""
    permit = Permit.get_by_code(permit_code)
    if not permit:
        return jsonify({"error": "التصريح غير موجود"}), 404
    return jsonify({"permit": permit}), 200


@permit_bp.route("/", methods=["GET"])
@role_required("admin", "staff", "security")
def get_all_permits():
    """جلب جميع التصاريح"""
    permits = Permit.get_all()
    return jsonify({"permits": permits, "count": len(permits)}), 200


@permit_bp.route("/<int:permit_id>/use", methods=["PUT"])
@role_required("security", "admin")
def mark_permit_used(permit_id):
    """تحديد تصريح كمستخدم"""
    user_id = int(get_jwt_identity())
    Permit.mark_as_used(permit_id)
    log_activity(user_id, "USE_PERMIT", f"استخدام تصريح: {permit_id}")
    return jsonify({"message": "تم استخدام التصريح"}), 200