from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from models.reservation import Reservation
from models.parking_space import ParkingSpace
from security.logging import log_activity
from security.decorators import role_required

reservation_bp = Blueprint("reservation", __name__)


@reservation_bp.route("/", methods=["POST"])
@role_required("visitor", "admin", "staff")
def create_reservation():
    """إنشاء حجز جديد (للزوار)"""
    data = request.get_json()
    space_id = data.get("space_id")
    notes = data.get("notes", "")

    if not space_id:
        return jsonify({"error": "يجب تحديد الموقف"}), 400

    user_id = int(get_jwt_identity())

    # التحقق من عدم وجود حجز نشط
    if Reservation.has_active_reservation(user_id):
        return jsonify({"error": "لديك حجز نشط بالفعل"}), 409

    # التحقق من توفر الموقف
    space = ParkingSpace.get_by_id(space_id)
    if not space:
        return jsonify({"error": "الموقف غير موجود"}), 404

    if space["status"] != "Available":
        return jsonify({"error": "الموقف غير متاح حالياً"}), 409

    # إنشاء الحجز
    reservation_id = Reservation.create(user_id, space_id, notes)

    if reservation_id:
        # تحديث حالة الموقف مؤقتاً
        ParkingSpace.update_status(space_id, "Occupied", user_id)
        log_activity(user_id, "CREATE_RESERVATION", f"حجز الموقف {space['space_code']}")

        reservation = Reservation.get_by_id(reservation_id)
        return jsonify({
            "message": "تم إنشاء الحجز بنجاح",
            "reservation": reservation
        }), 201

    return jsonify({"error": "فشل إنشاء الحجز"}), 500


@reservation_bp.route("/my", methods=["GET"])
@role_required("visitor", "admin", "staff")
def get_my_reservations():
    """جلب حجوزات المستخدم الحالي"""
    user_id = int(get_jwt_identity())
    reservations = Reservation.get_by_user(user_id)
    return jsonify({"reservations": reservations, "count": len(reservations)}), 200


@reservation_bp.route("/<int:reservation_id>", methods=["GET"])
@role_required("visitor", "admin", "staff")
def get_reservation(reservation_id):
    """جلب تفاصيل حجز"""
    reservation = Reservation.get_by_id(reservation_id)
    if not reservation:
        return jsonify({"error": "الحجز غير موجود"}), 404
    return jsonify({"reservation": reservation}), 200


@reservation_bp.route("/<int:reservation_id>/cancel", methods=["PUT"])
@role_required("visitor", "admin", "staff")
def cancel_reservation(reservation_id):
    """إلغاء حجز"""
    user_id = int(get_jwt_identity())
    reservation = Reservation.get_by_id(reservation_id)

    if not reservation:
        return jsonify({"error": "الحجز غير موجود"}), 404

    # التحقق من الملكية أو الصلاحية
    claims = get_jwt()
    role = claims.get("role")

    if role == "visitor" and reservation["user_id"] != user_id:
        return jsonify({"error": "غير مصرح لك بإلغاء هذا الحجز"}), 403

    if reservation["status"] not in ["Pending", "Confirmed"]:
        return jsonify({"error": "لا يمكن إلغاء هذا الحجز"}), 400

    Reservation.cancel(reservation_id, reservation["user_id"])
    log_activity(user_id, "CANCEL_RESERVATION", f"إلغاء حجز {reservation['reservation_code']}")

    return jsonify({"message": "تم إلغاء الحجز بنجاح"}), 200


@reservation_bp.route("/pending", methods=["GET"])
@role_required("staff", "admin")
def get_pending_reservations():
    """جلب الحجوزات قيد الانتظار (للموظف)"""
    reservations = Reservation.get_pending()
    return jsonify({"reservations": reservations, "count": len(reservations)}), 200


@reservation_bp.route("/all", methods=["GET"])
@role_required("staff", "admin")
def get_all_reservations():
    """جلب جميع الحجوزات (للموظف والمدير)"""
    status = request.args.get("status")
    reservations = Reservation.get_all(status)
    return jsonify({"reservations": reservations, "count": len(reservations)}), 200


@reservation_bp.route("/<int:reservation_id>/confirm", methods=["PUT"])
@role_required("staff", "admin")
def confirm_reservation(reservation_id):
    """تأكيد حجز (للموظف)"""
    user_id = int(get_jwt_identity())
    reservation = Reservation.get_by_id(reservation_id)

    if not reservation:
        return jsonify({"error": "الحجز غير موجود"}), 404

    if reservation["status"] != "Pending":
        return jsonify({"error": "الحجز ليس قيد الانتظار"}), 400

    Reservation.update_status(reservation_id, "Confirmed", user_id)
    log_activity(user_id, "CONFIRM_RESERVATION", f"تأكيد حجز {reservation['reservation_code']}")

    return jsonify({"message": "تم تأكيد الحجز بنجاح"}), 200


@reservation_bp.route("/<int:reservation_id>/reject", methods=["PUT"])
@role_required("staff", "admin")
def reject_reservation(reservation_id):
    """رفض حجز (للموظف)"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    reason = data.get("reason", "")

    reservation = Reservation.get_by_id(reservation_id)
    if not reservation:
        return jsonify({"error": "الحجز غير موجود"}), 404

    if reservation["status"] != "Pending":
        return jsonify({"error": "الحجز ليس قيد الانتظار"}), 400

    Reservation.update_status(reservation_id, "Rejected", user_id)
    # إعادة الموقف إلى متاح
    ParkingSpace.update_status(reservation["space_id"], "Available", user_id)

    log_activity(user_id, "REJECT_RESERVATION", 
                 f"رفض حجز {reservation['reservation_code']}: {reason}")

    return jsonify({"message": "تم رفض الحجز"}), 200


@reservation_bp.route("/<int:reservation_id>/complete", methods=["PUT"])
@role_required("staff", "admin")
def complete_reservation(reservation_id):
    """إكمال حجز (مغادرة الزائر)"""
    user_id = int(get_jwt_identity())
    reservation = Reservation.get_by_id(reservation_id)

    if not reservation:
        return jsonify({"error": "الحجز غير موجود"}), 404

    Reservation.update_status(reservation_id, "Completed", user_id)
    ParkingSpace.update_status(reservation["space_id"], "Available", user_id)

    log_activity(user_id, "COMPLETE_RESERVATION", 
                 f"إكمال حجز {reservation['reservation_code']}")

    return jsonify({"message": "تم إكمال الحجز"}), 200


@reservation_bp.route("/stats", methods=["GET"])
@role_required("staff", "admin")
def get_reservation_stats():
    """إحصائيات الحجوزات"""
    stats = Reservation.get_stats()
    return jsonify({"stats": stats}), 200