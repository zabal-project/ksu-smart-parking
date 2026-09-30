import os

class Config:
    # إعدادات قاعدة البيانات
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ksu_smart_parking")
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # إعدادات JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ksu-smart-parking-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = 86400

    # إعدادات عامة
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 10000))