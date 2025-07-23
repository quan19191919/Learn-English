from flask import Blueprint, request, jsonify
import mysql.connector
from mysql.connector import Error

admin_bp = Blueprint('admin', __name__)

# Cấu hình DB (hoặc bạn import từ file db.py)
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        database='yagi_english',
        user='root',
        password='25102004'  # hoặc mật khẩu MySQL của bạn
    )

@admin_bp.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE email = %s AND password = %s", (email, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            return jsonify({"success": True, "username": admin['username'], "redirect": "/src/pages/Admin/Dashboard.html"})
        else:
            return jsonify({"success": False, "message": "Sai email hoặc mật khẩu"}), 401

    except Error as e:
        return jsonify({"success": False, "message": f"Lỗi hệ thống: {str(e)}"}), 500
