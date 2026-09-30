from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.user import User
from models.role import Role
from security.logging import log_activity
from security.decorators import role_required

admin_bp = Blueprint("admin", __name__)


# ============================================
# إدارة المستخدمين
# ============================================

@admin_bp.route("/users", methods=["GET"])
@role_required("admin")
def get_users():
    """عرض جميع المستخدمين"""
    users = User.get_all()
    return jsonify({"users": users, "count": len(users)}), 200


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@role_required("admin")
def get_user(user_id):
    """عرض مستخدم معين"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    return jsonify({"user": user}), 200


@admin_bp.route("/users", methods=["POST"])
@role_required("admin")
def create_user():
    """إضافة مستخدم جديد"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name", "")
    email = data.get("email", "")
    role_id = data.get("role_id", 3)  # افتراضي: visitor

    if not username or not password:
        return jsonify({"error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400

    if len(password) < 6:
        return jsonify({"error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}), 400

    existing = User.get_by_username(username)
    if existing:
        return jsonify({"error": "اسم المستخدم موجود مسبقاً"}), 409

    admin_id = int(get_jwt_identity())
    new_id = User.create(username, password, full_name, email, role_id)
    log_activity(admin_id, "CREATE_USER", f"إنشاء مستخدم جديد: {username}")

    return jsonify({
        "message": "تم إنشاء المستخدم بنجاح",
        "user_id": new_id
    }), 201


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@role_required("admin")
def update_user(user_id):
    """تعديل مستخدم"""
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    role_id = data.get("role_id")
    is_active = data.get("is_active", True)

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    admin_id = int(get_jwt_identity())
    User.update(user_id, full_name, email, role_id, is_active)
    log_activity(admin_id, "UPDATE_USER", f"تعديل مستخدم: {user['username']}")

    return jsonify({"message": "تم تحديث المستخدم بنجاح"}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    """حذف مستخدم"""
    current_admin_id = int(get_jwt_identity())
    if user_id == current_admin_id:
        return jsonify({"error": "لا يمكنك حذف حسابك الخاص"}), 400

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    User.delete(user_id)
    log_activity(current_admin_id, "DELETE_USER", f"حذف مستخدم: {user['username']}")

    return jsonify({"message": "تم حذف المستخدم بنجاح"}), 200


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["PUT"])
@role_required("admin")
def toggle_user_active(user_id):
    """تفعيل/إلغاء تفعيل مستخدم"""
    current_admin_id = int(get_jwt_identity())
    if user_id == current_admin_id:
        return jsonify({"error": "لا يمكنك تعطيل حسابك الخاص"}), 400

    User.toggle_active(user_id)
    log_activity(current_admin_id, "TOGGLE_USER", f"تغيير حالة المستخدم {user_id}")

    return jsonify({"message": "تم تغيير حالة المستخدم"}), 200


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["PUT"])
@role_required("admin")
def reset_user_password(user_id):
    """إعادة تعيين كلمة مرور مستخدم"""
    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password or len(new_password) < 6:
        return jsonify({"error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}), 400

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    admin_id = int(get_jwt_identity())
    User.update_password(user_id, new_password)
    log_activity(admin_id, "RESET_PASSWORD", f"إعادة تعيين كلمة مرور: {user['username']}")

    return jsonify({"message": "تم إعادة تعيين كلمة المرور"}), 200


# ============================================
# الأدوار والصلاحيات
# ============================================

@admin_bp.route("/roles", methods=["GET"])
@role_required("admin", "staff")
def get_roles():
    """عرض الأدوار"""
    roles = Role.get_all()
    return jsonify({"roles": roles}), 200


@admin_bp.route("/roles/<int:role_id>/permissions", methods=["GET"])
@role_required("admin")
def get_role_permissions(role_id):
    """عرض صلاحيات دور"""
    permissions = Role.get_permissions(role_id)
    return jsonify({"permissions": permissions}), 200


@admin_bp.route("/permissions", methods=["GET"])
@role_required("admin")
def get_all_permissions():
    """عرض جميع الصلاحيات"""
    permissions = Role.get_all_permissions()
    return jsonify({"permissions": permissions}), 200