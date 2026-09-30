from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

# استيراد Blueprints
from routes.auth_routes import auth_bp
from routes.parking_routes import parking_bp
from routes.admin_routes import admin_bp
from routes.logs_routes import logs_bp
from routes.reservation_routes import reservation_bp
from routes.building_routes import building_bp
from routes.host_routes import host_bp
from routes.visit_routes import visit_bp
from routes.permit_routes import permit_bp
from routes.security_routes import security_bp
from routes.notification_routes import notification_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, 
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=False)
jwt = JWTManager(app)

# تسجيل Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(parking_bp, url_prefix="/api/parking")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(logs_bp, url_prefix="/api/logs")
app.register_blueprint(reservation_bp, url_prefix="/api/reservations")
app.register_blueprint(building_bp, url_prefix="/api/buildings")
app.register_blueprint(host_bp, url_prefix="/api/hosts")
app.register_blueprint(visit_bp, url_prefix="/api/visits")
app.register_blueprint(permit_bp, url_prefix="/api/permits")
app.register_blueprint(security_bp, url_prefix="/api/security")
app.register_blueprint(notification_bp, url_prefix="/api/notifications")


@app.route("/")
def home():
    return jsonify({
        "message": "KSU Visitor Parking API",
        "version": "3.0",
        "status": "Running",
        "endpoints": {
            "auth": "/api/auth",
            "parking": "/api/parking",
            "admin": "/api/admin",
            "logs": "/api/logs",
            "reservations": "/api/reservations",
            "buildings": "/api/buildings",
            "hosts": "/api/hosts",
            "visits": "/api/visits",
            "permits": "/api/permits",
            "security": "/api/security",
            "notifications": "/api/notifications"
        }
    }), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "المسار غير موجود"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "خطأ في السيرفر"}), 500


if __name__ == "__main__":
    print("=" * 70)
    print("  KSU Visitor Parking API v3.0")
    print("  نظام إدارة زوار ومواقف جامعة الملك سعود")
    print("=" * 70)
    print("Server: http://localhost:5000")
    print("=" * 70)
    print("\nAvailable Endpoints:")
    print("  🔐 Auth:          /api/auth")
    print("  🅿️  Parking:       /api/parking")
    print("  👤 Admin:         /api/admin")
    print("  📋 Logs:          /api/logs")
    print("  📅 Reservations:  /api/reservations")
    print("  🏢 Buildings:     /api/buildings")
    print("  👥 Hosts:         /api/hosts")
    print("  🎫 Visits:        /api/visits")
    print("  🎟️  Permits:       /api/permits")
    print("  🛡️  Security:      /api/security")
    print("  🔔 Notifications: /api/notifications")
    print("=" * 70)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)