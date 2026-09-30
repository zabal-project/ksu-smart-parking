import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            ssl_disabled=False,
            ssl_verify_cert=False
        )
        return connection
    except Error as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None


def execute_query(query, params=None, fetch=False):
    connection = get_connection()
    if not connection:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.lastrowid
    except Error as e:
        print(f"خطأ في تنفيذ الاستعلام: {e}")
        return None
    finally:
        cursor.close()
        connection.close()