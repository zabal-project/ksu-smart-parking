from flask import Blueprint, request, jsonify
from models.user import User
from security.auth import verify_password, generate_token
from security.logging import log_activity

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400

    user = User.get_by_username(username)
    if not user:
        return jsonify({"error": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

    if not user["is_active"]:
        return jsonify({"error": "الحساب غير مفعل"}), 403

    if not verify_password(user["password_hash"], password):
        return jsonify({"error": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

    token = generate_token(user["user_id"], user["role_name"])
    User.update_last_login(user["user_id"])
    log_activity(user["user_id"], "LOGIN", f"تسجيل دخول: {username}")

    return jsonify({
        "message": "تم تسجيل الدخول بنجاح",
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role_name"]
        }
    }), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    تسجيل زائر جديد (self-registration)
    - الزوار فقط يمكنهم التسجيل بأنفسهم
    - الأدوار الأخرى (admin, staff) تُنشأ بواسطة المدير
    """
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip()

    # التحقق من المدخلات
    if not username or not password:
        return jsonify({"error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400

    if len(username) < 3:
        return jsonify({"error": "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"}), 400

    if len(password) < 6:
        return jsonify({"error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}), 400

    if email and "@" not in email:
        return jsonify({"error": "البريد الإلكتروني غير صحيح"}), 400

    # التحقق من عدم وجود المستخدم
    existing = User.get_by_username(username)
    if existing:
        return jsonify({"error": "اسم المستخدم موجود مسبقاً"}), 409

    # إنشاء الحساب كـ visitor (role_id = 3)
    # ⚠️ مهم: لا نسمح للزائر باختيار دوره
    VISITOR_ROLE_ID = 3

    try:
        new_id = User.create(username, password, full_name, email, VISITOR_ROLE_ID)

        if new_id:
            log_activity(new_id, "REGISTER", f"تسجيل حساب جديد: {username}")

            return jsonify({
                "message": "تم إنشاء الحساب بنجاح",
                "user_id": new_id,
                "role": "visitor"
            }), 201
        else:
            return jsonify({"error": "فشل إنشاء الحساب"}), 500

    except Exception as e:
        print(f"Register Error: {e}")
        return jsonify({"error": "حدث خطأ أثناء إنشاء الحساب"}), 500