from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.visit import Visit
from models.permit import Permit
from models.access_log import AccessLog
from security.decorators import role_required
from security.logging import log_activity

security_bp = Blueprint("security", __name__)


@security_bp.route("/verify-qr", methods=["POST"])
@role_required("security", "admin")
def verify_qr():
    """التحقق من QR Code (للأمن)"""
    data = request.get_json()
    permit_code = data.get("permit_code")

    if not permit_code:
        return jsonify({"error": "كود التصريح مطلوب"}), 400

    result = Permit.verify(permit_code)
    return jsonify(result), 200 if result["valid"] else 400


@security_bp.route("/search", methods=["GET"])
@role_required("security", "admin", "staff")
def search_vehicle():
    """البحث عن زيارة برقم اللوحة أو كود الزيارة"""
    query_param = request.args.get("q")

    if not query_param:
        return jsonify({"error": "مطلوب البحث عن رقم اللوحة أو كود الزيارة"}), 400

    # البحث برقم اللوحة أولاً
    visits = Visit.get_all()
    matching = [
        v for v in visits
        if (v.get("vehicle_plate") and query_param.lower() in v["vehicle_plate"].lower())
        or (v.get("visit_code") and query_param in v["visit_code"])
    ]

    return jsonify({"visits": matching, "count": len(matching)}), 200


@security_bp.route("/entry", methods=["POST"])
@role_required("security", "admin")
def log_entry():
    """تسجيل دخول زائر"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    visit_id = data.get("visit_id")
    gate_number = data.get("gate_number", "Main Gate")
    notes = data.get("notes", "")

    if not visit_id:
        return jsonify({"error": "معرف الزيارة مطلوب"}), 400

    visit = Visit.get_by_id(visit_id)
    if not visit:
        return jsonify({"error": "الزيارة غير موجودة"}), 404

    if visit["status"] != "Approved":
        return jsonify({"error": f"حالة الزيارة: {visit['status']}. يجب أن تكون Approved"}), 400

    # تسجيل الدخول
    Visit.log_entry(visit_id, user_id, gate_number, notes)
    AccessLog.create(
        visit_id=visit_id,
        action="Entry",
        verified_by=user_id,
        gate_number=gate_number,
        vehicle_plate=visit.get("vehicle_plate"),
        notes=notes
    )

    # تحديد التصريح كمستخدم
    permit = Permit.get_by_visit(visit_id)
    if permit:
        Permit.mark_as_used(permit["permit_id"])

    log_activity(user_id, "LOG_ENTRY", f"تسجيل دخول زيارة: {visit_id}")

    return jsonify({"message": "تم تسجيل الدخول بنجاح"}), 200


@security_bp.route("/exit", methods=["POST"])
@role_required("security", "admin")
def log_exit():
    """تسجيل خروج زائر"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    visit_id = data.get("visit_id")
    gate_number = data.get("gate_number", "Main Gate")
    notes = data.get("notes", "")

    if not visit_id:
        return jsonify({"error": "معرف الزيارة مطلوب"}), 400

    visit = Visit.get_by_id(visit_id)
    if not visit:
        return jsonify({"error": "الزيارة غير موجودة"}), 404

    if not visit.get("entry_time"):
        return jsonify({"error": "لم يتم تسجيل الدخول بعد"}), 400

    Visit.log_exit(visit_id, user_id, gate_number, notes)
    AccessLog.create(
        visit_id=visit_id,
        action="Exit",
        verified_by=user_id,
        gate_number=gate_number,
        vehicle_plate=visit.get("vehicle_plate"),
        notes=notes
    )

    log_activity(user_id, "LOG_EXIT", f"تسجيل خروج زيارة: {visit_id}")

    return jsonify({"message": "تم تسجيل الخروج بنجاح"}), 200


@security_bp.route("/logs", methods=["GET"])
@role_required("security", "admin")
def get_access_logs():
    """جلب سجلات الدخول والخروج"""
    limit = int(request.args.get("limit", 100))
    logs = AccessLog.get_recent(limit)
    return jsonify({"logs": logs, "count": len(logs)}), 200


@security_bp.route("/logs/today", methods=["GET"])
@role_required("security", "admin")
def get_today_logs():
    """سجلات اليوم"""
    logs = AccessLog.get_today()
    return jsonify({"logs": logs, "count": len(logs)}), 200


@security_bp.route("/stats", methods=["GET"])
@role_required("security", "admin", "staff")
def get_security_stats():
    """إحصائيات الأمن"""
    stats = AccessLog.get_stats()
    return jsonify({"stats": stats}), 200