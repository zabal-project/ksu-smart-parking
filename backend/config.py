import os

class Config:
    # إعدادات قاعدة البيانات
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ksu_smart_parking")

    # إعدادات JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ksu-smart-parking-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 ساعة

    # إعدادات عامة
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000