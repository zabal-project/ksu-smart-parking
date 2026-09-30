import random
import time
import requests
from datetime import datetime

# إعدادات المحاكي
BASE_URL = "http://localhost:5000"
UPDATE_INTERVAL = 5  # كل 5 ثوانٍ

# بيانات تسجيل الدخول (للإداري)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"

# قائمة المواقف (30 موقف)
SPACE_IDS = list(range(1, 31))


def login():
    """تسجيل الدخول والحصول على JWT Token"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"✅ تم تسجيل الدخول بنجاح")
        return token
    else:
        print(f"❌ فشل تسجيل الدخول: {response.text}")
        return None


def update_space_status(token, space_id, status):
    """تحديث حالة موقف"""
    url = f"{BASE_URL}/api/parking/spaces/{space_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"status": status}
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200


def run_simulator():
    """تشغيل المحاكي"""
    print("=" * 60)
    print("🚗 KSU Smart Parking Simulator")
    print("=" * 60)

    token = login()
    if not token:
        print("❌ لا يمكن تشغيل المحاكي بدون تسجيل دخول")
        return

    print(f"⏱️  زمن التحديث: كل {UPDATE_INTERVAL} ثوانٍ")
    print(f"🅿️  عدد المواقف: {len(SPACE_IDS)}")
    print("=" * 60)
    print("اضغط Ctrl+C للإيقاف\n")

    try:
        while True:
            # اختيار 5 مواقف عشوائية لتغيير حالتها
            spaces_to_update = random.sample(SPACE_IDS, 5)

            for space_id in spaces_to_update:
                # اختيار حالة عشوائية
                new_status = random.choice(["Available", "Occupied"])

                # تحديث الحالة
                success = update_space_status(token, space_id, new_status)

                if success:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] الموقف {space_id}: {new_status}")
                else:
                    print(f"❌ فشل تحديث الموقف {space_id}")

            # انتظار قبل التحديث التالي
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n⏹️  تم إيقاف المحاكي")


if __name__ == "__main__":
    run_simulator()