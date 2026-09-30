from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.parking_space import ParkingSpace
from security.logging import log_activity
from security.decorators import role_required

parking_bp = Blueprint("parking", __name__)


@parking_bp.route("/spaces", methods=["GET"])
def get_all_spaces():
    """عرض جميع المواقف (متاح للجميع)"""
    spaces = ParkingSpace.get_all_with_status()
    return jsonify({"spaces": spaces, "count": len(spaces)}), 200


@parking_bp.route("/spaces/<int:space_id>", methods=["GET"])
def get_space(space_id):
    """تفاصيل موقف معين"""
    space = ParkingSpace.get_by_id(space_id)
    if not space:
        return jsonify({"error": "الموقف غير موجود"}), 404
    return jsonify({"space": space}), 200


@parking_bp.route("/zones", methods=["GET"])
def get_available_zones():
    """الصفوف المتاحة"""
    zones = ParkingSpace.get_available_zones()
    return jsonify({"zones": zones}), 200


@parking_bp.route("/stats", methods=["GET"])
def get_stats():
    """إحصائيات شاملة"""
    overall = ParkingSpace.get_stats()
    by_zone = ParkingSpace.get_zone_stats()
    return jsonify({
        "overall": overall,
        "by_zone": by_zone
    }), 200


@parking_bp.route("/spaces/<int:space_id>", methods=["PUT"])
@role_required("admin", "staff")
def update_space_status(space_id):
    """تحديث حالة موقف (admin/staff فقط)"""
    data = request.get_json()
    status = data.get("status")

    if status not in ["Available", "Occupied"]:
        return jsonify({"error": "الحالة يجب أن تكون Available أو Occupied"}), 400

    space = ParkingSpace.get_by_id(space_id)
    if not space:
        return jsonify({"error": "الموقف غير موجود"}), 404

    user_id = int(get_jwt_identity())
    ParkingSpace.update_status(space_id, status, user_id)
    log_activity(user_id, "UPDATE_STATUS", f"تحديث الموقف {space['space_code']} إلى {status}")

    return jsonify({
        "message": "تم تحديث الحالة بنجاح",
        "space_id": space_id,
        "new_status": status
    }), 200


@parking_bp.route("/spaces/bulk-update", methods=["POST"])
@role_required("admin")
def bulk_update():
    """تحديث جماعي (admin فقط)"""
    data = request.get_json()
    updates = data.get("updates", [])

    if not isinstance(updates, list) or len(updates) == 0:
        return jsonify({"error": "قائمة التحديثات مطلوبة"}), 400

    user_id = int(get_jwt_identity())
    success_count = 0
    failed = []

    for item in updates:
        space_id = item.get("space_id")
        status = item.get("status")

        if status not in ["Available", "Occupied"]:
            failed.append({"space_id": space_id, "reason": "حالة غير صحيحة"})
            continue

        result = ParkingSpace.update_status(space_id, status, user_id)
        if result is not None:
            success_count += 1
        else:
            failed.append({"space_id": space_id, "reason": "فشل التحديث"})

    log_activity(user_id, "BULK_UPDATE", f"تحديث جماعي: {success_count} نجح، {len(failed)} فشل")

    return jsonify({
        "message": f"تم تحديث {success_count} موقف",
        "success_count": success_count,
        "failed": failed
    }), 200