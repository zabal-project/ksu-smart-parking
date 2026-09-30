from flask import Blueprint, request, jsonify
from models.activity_log import ActivityLog
from security.decorators import role_required

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/", methods=["GET"])
@role_required("admin")
def get_logs():
    """عرض سجلات النشاط (admin فقط)"""
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))

    if limit > 500:
        limit = 500

    logs = ActivityLog.get_all(limit=limit, offset=offset)
    total = ActivityLog.get_count()

    return jsonify({
        "logs": logs,
        "count": len(logs),
        "total": total,
        "limit": limit,
        "offset": offset
    }), 200


@logs_bp.route("/user/<int:user_id>", methods=["GET"])
@role_required("admin")
def get_user_logs(user_id):
    """سجلات مستخدم معين"""
    limit = int(request.args.get("limit", 50))
    logs = ActivityLog.get_by_user(user_id, limit=limit)
    return jsonify({"logs": logs, "count": len(logs)}), 200