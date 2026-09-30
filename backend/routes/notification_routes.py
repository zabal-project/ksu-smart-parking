from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.notification import Notification
from security.decorators import role_required

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/my", methods=["GET"])
@role_required("visitor", "host", "admin", "staff", "security")
def get_my_notifications():
    """جلب إشعاراتي"""
    user_id = int(get_jwt_identity())
    unread_only = request.args.get("unread", "false").lower() == "true"

    notifications = Notification.get_by_user(user_id, unread_only)
    unread_count = Notification.get_unread_count(user_id)

    return jsonify({
        "notifications": notifications,
        "count": len(notifications),
        "unread_count": unread_count
    }), 200


@notification_bp.route("/unread-count", methods=["GET"])
@role_required("visitor", "host", "admin", "staff", "security")
def get_unread_count():
    """عدد الإشعارات غير المقروءة"""
    user_id = int(get_jwt_identity())
    count = Notification.get_unread_count(user_id)
    return jsonify({"unread_count": count}), 200


@notification_bp.route("/<int:notification_id>/read", methods=["PUT"])
@role_required("visitor", "host", "admin", "staff", "security")
def mark_read(notification_id):
    """تحديد إشعار كمقروء"""
    user_id = int(get_jwt_identity())
    Notification.mark_as_read(notification_id, user_id)
    return jsonify({"message": "تم تحديد الإشعار كمقروء"}), 200


@notification_bp.route("/read-all", methods=["PUT"])
@role_required("visitor", "host", "admin", "staff", "security")
def mark_all_read():
    """تحديد كل الإشعارات كمقروءة"""
    user_id = int(get_jwt_identity())
    Notification.mark_all_as_read(user_id)
    return jsonify({"message": "تم تحديد كل الإشعارات كمقروءة"}), 200


@notification_bp.route("/<int:notification_id>", methods=["DELETE"])
@role_required("visitor", "host", "admin", "staff", "security")
def delete_notification(notification_id):
    """حذف إشعار"""
    user_id = int(get_jwt_identity())
    Notification.delete(notification_id, user_id)
    return jsonify({"message": "تم حذف الإشعار"}), 200