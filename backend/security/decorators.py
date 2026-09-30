from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*allowed_roles):
    """Decorator للتحقق من صلاحيات المستخدم"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "غير مصرح لك بهذه العملية",
                    "required_roles": list(allowed_roles),
                    "your_role": user_role
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
