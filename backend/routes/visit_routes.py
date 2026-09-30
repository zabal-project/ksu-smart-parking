from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from models.visit import Visit, serialize_visit, serialize_visits
from models.host import Host
from models.permit import Permit
from models.notification import Notification
from security.decorators import role_required
from security.logging import log_activity

visit_bp = Blueprint("visit", __name__)


@visit_bp.route("/", methods=["POST"])
@role_required("visitor", "admin", "staff")
def create_visit():
    """إنشاء طلب زيارة جديد"""
    data = request.get_json()

    required = ["host_id", "scheduled_date", "scheduled_time"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"الحقل {field} مطلوب"}), 400

    user_id = int(get_jwt_identity())

    visit_id = Visit.create(
        visitor_id=user_id,
        host_id=data["host_id"],
        building_id=data.get("building_id"),
        purpose=data.get("purpose", ""),
        scheduled_date=data["scheduled_date"],
        scheduled_time=data["scheduled_time"],
        vehicle_plate=data.get("vehicle_plate", ""),
        vehicle_type=data.get("vehicle_type", ""),
        visitors_count=data.get("visitors_count", 1),
        expected_duration=data.get("expected_duration", 60)
    )

    if not visit_id:
        return jsonify({"error": "فشل إنشاء الزيارة"}), 500

    # إشعار المضيف
    try:
        host = Host.get_by_id(data["host_id"])
        if host:
            Notification.create(
                user_id=host["user_id"],
                title="طلب زيارة جديد",
                message="لديك طلب زيارة جديد بانتظار الموافقة",
                type="info",
                related_visit_id=visit_id
            )
    except Exception as e:
        print(f"Notification error: {e}")

    log_activity(user_id, "CREATE_VISIT", f"إنشاء زيارة: {visit_id}")

    visit = Visit.get_by_id(visit_id)
    visit = serialize_visit(visit)

    return jsonify({
        "message": "تم إنشاء طلب الزيارة بنجاح",
        "visit": visit
    }), 201


@visit_bp.route("/my", methods=["GET"])
@role_required("visitor", "admin", "staff")
def get_my_visits():
    """جلب زياراتي"""
    user_id = int(get_jwt_identity())
    visits = Visit.get_by_visitor(user_id)
    visits = serialize_visits(visits)
    return jsonify({"visits": visits, "count": len(visits)}), 200


@visit_bp.route("/<int:visit_id>", methods=["GET"])
@role_required("visitor", "admin", "staff", "host", "security")
def get_visit(visit_id):
    """جلب تفاصيل زيارة"""
    visit = Visit.get_by_id(visit_id)
    if not visit:
        return jsonify({"error": "الزيارة غير موجودة"}), 404
    visit = serialize_visit(visit)
    return jsonify({"visit": visit}), 200


@visit_bp.route("/code/<string:visit_code>", methods=["GET"])
@role_required("security", "admin", "staff")
def get_visit_by_code(visit_code):
    """جلب زيارة بالكود (للأمن)"""
    visit = Visit.get_by_code(visit_code)
    if not visit:
        return jsonify({"error": "الزيارة غير موجودة"}), 404
    visit = serialize_visit(visit)
    return jsonify({"visit": visit}), 200


@visit_bp.route("/<int:visit_id>/approve", methods=["PUT"])
@role_required("host", "admin")
def approve_visit(visit_id):
    """موافقة على زيارة"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    visit = Visit.get_by_id(visit_id)
    if not visit:
        return jsonify({"error": "الزيارة غير موجودة"}), 404

    if visit["status"] != "Pending":
        return jsonify({"error": "الزيارة ليست قيد الانتظار"}), 400

    if role == "host":
        host = Host.get_by_user_id(user_id)
        if not host or host["host_id"] != visit["host_id"]:
            return jsonify({"error": "غير مصرح لك"}), 403

    data = request.get_json() or {}
    Visit.approve(visit_id, data.get("notes", ""))

    # إنشاء تصريح QR
    visit_updated = Visit.get_by_id(visit_id)
    visit_serialized = serialize_visit(visit_updated.copy() if visit_updated else {})
    Permit.create(visit_id, visit_serialized)

    try:
        Notification.create(
            user_id=visit["visitor_id"],
            title="تمت الموافقة على زيارتك",
            message=f"تمت الموافقة على زيارتك. كود الزيارة: {visit['visit_code']}",
            type="success",
            related_visit_id=visit_id
        )
    except Exception as e:
        print(f"Notification error: {e}")

    log_activity(user_id, "APPROVE_VISIT", f"موافقة على زيارة: {visit_id}")

    permit = Permit.get_by_visit(visit_id)
    return jsonify({
        "message": "تمت الموافقة على الزيارة",
        "permit": permit
    }), 200


@visit_bp.route("/<int:visit_id>/reject", methods=["PUT"])
@role_required("host", "admin")
def reject_visit(visit_id):
    """رفض زيارة"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    visit = Visit.get_by_id(visit_id)
    if not visit:
        return jsonify({"error": "الزيارة غير موجودة"}), 404

    if role == "host":
        host = Host.get_by_user_id(user_id)
        if not host or host["host_id"] != visit["host_id"]:
            return jsonify({"error": "غير مصرح لك"}), 403

    data = request.get_json() or {}
    reason = data.get("reason", "لم يتم تحديد سبب")

    Visit.reject(visit_id, reason)

    try:
        Notification.create(
            user_id=visit["visitor_id"],
            title="تم رفض زيارتك",
            message=f"تم رفض زيارتك. السبب: {reason}",
            type="danger",
            related_visit_id=visit_id
        )
    except Exception as e:
        print(f"Notification error: {e}")

    log_activity(user_id, "REJECT_VISIT", f"رفض زيارة: {visit_id}")
    return jsonify({"message": "تم رفض الزيارة"}), 200


@visit_bp.route("/<int:visit_id>/cancel", methods=["PUT"])
@role_required("visitor", "admin")
def cancel_visit(visit_id):
    """إلغاء زيارة"""
    user_id = int(get_jwt_identity())
    Visit.cancel(visit_id, user_id)
    log_activity(user_id, "CANCEL_VISIT", f"إلغاء زيارة: {visit_id}")
    return jsonify({"message": "تم إلغاء الزيارة"}), 200


@visit_bp.route("/all", methods=["GET"])
@role_required("admin", "staff", "security")
def get_all_visits():
    """جلب جميع الزيارات"""
    status = request.args.get("status")
    visits = Visit.get_all(status)
    visits = serialize_visits(visits)
    return jsonify({"visits": visits, "count": len(visits)}), 200


@visit_bp.route("/stats", methods=["GET"])
@role_required("admin", "staff")
def get_visit_stats():
    """إحصائيات الزيارات"""
    stats = Visit.get_stats()
    return jsonify({"stats": stats}), 200