from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
from utils.mail_otp import send_otp
from flask_bcrypt import Bcrypt
from chat_api import chat_with_gemini


app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)
app.secret_key = "bi-mat-cua-bo"
bcrypt = Bcrypt(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="25102004",
        database="yagi_english"
    )

# ✅ Đăng ký người dùng mới (role mặc định là student)
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([username, email, password]):
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    # Hash mật khẩu
    password_hash = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Kiểm tra email đã tồn tại chưa
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email đã tồn tại"}), 400

        # Thêm tài khoản mới
        cursor.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, 'student')
        """, (username, email, password_hash))
        conn.commit()

    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {str(e)}"}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return jsonify({"success": True, "redirect": "/src/Auth/LoginForm.html"}), 200

# Gửi mã OTP (chỉ student mới được gửi)
@app.route('/send-otp', methods=['POST'])
def send_otp_route():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email không được để trống"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return jsonify({"success": False, "message": "Không tìm thấy người dùng"}), 400
    if user["role"] == "admin":
        return jsonify({"success": False, "message": "Admin không cần OTP"}), 400
    otp_code = str(random.randint(100000, 999999))
    try:
        send_otp(email, otp_code)
        print(f"OTP {otp_code} đã được gửi đến {email}")
        session['otp'] = otp_code
        session['email'] = email
        return jsonify({"success": True, "message": "Đã gửi OTP"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Gửi OTP thất bại: {str(e)}"}), 500

# Kiểm tra mật khẩu trước khi gửi OTP
@app.route('/check-password', methods=['POST'])
def check_password():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Thiếu email hoặc mật khẩu"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"success": False, "message": "Email không tồn tại"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Sai mật khẩu"}), 401

    return jsonify({"success": True}), 200

# Đăng nhập (admin bỏ OTP, student cần OTP)
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.form.get("email")
    password = request.form.get("password")
    otp = request.form.get("otp")
    if not email or not password:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return jsonify({"success": False, "message": "Không tìm thấy tài khoản"}), 400
    if not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Sai mật khẩu"}), 400
    if user["role"] == "admin":
        return jsonify({
            "success": True,
            "username": user["username"],
            "role": user["role"],
            "redirect": "/Admin/Dashboard/Home.html"
        }), 200
    if not otp:
        return jsonify({"success": False, "message": "Vui lòng nhập mã OTP"}), 400
    if otp != session.get("otp"):
        return jsonify({"success": False, "message": "Sai mã OTP"}), 400
    session.pop("otp", None)
    return jsonify({
        "success": True,
        "username": user["username"],
        "role": user["role"],
        "redirect": "/src/pages/Home.html"
    }), 200

#  API lấy danh sách tài khoản trẻ (student)
@app.route("/api/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, password FROM users WHERE role = 'student'")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

#  API thêm học sinh mới (đã sửa: mã hóa mật khẩu)
@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")

    if not all([username, email, password]):
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

#  Mã hóa mật khẩu trước khi lưu
    password_hash = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, password_hash, role))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Thêm thành công"}), 201
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500

#  API cập nhật học sinh theo ID (chưa mã hóa lại password)

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

#  Mã hóa lại mật khẩu khi cập nhật
    password_hash = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET username = %s, email = %s, password = %s
            WHERE id = %s AND role = 'student'
        """, (username, email, password_hash, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Cập nhật thành công"}), 200
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500

# API xóa học sinh theo ID
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s AND role = 'student'", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Xóa thành công"}), 200
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500

#change password
@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not email or not old_password or not new_password:
        return jsonify({'message': 'Thiếu thông tin'}), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'message': 'Không tìm thấy người dùng'}), 404
        hashed_password = row[0]
        if not check_password_hash(hashed_password, old_password):
            return jsonify({'message': 'Mật khẩu cũ không đúng'}), 401
        new_hashed = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_hashed, email))
        conn.commit()
        return jsonify({'message': 'Đổi mật khẩu thành công'}), 200
    except Exception as e:
        print("Lỗi máy chủ:", e)
        return jsonify({'message': 'Lỗi máy chủ: ' + str(e)}), 500
    finally:
        try:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        except:
            pass
        
# API Chat Gemini
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Vui lòng nhập câu hỏi."}), 400
    try:
        response = chat_with_gemini(message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Quên mật khẩu - xác nhận OTP và đổi mật khẩu mới

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    if not all([email, otp, new_password]):
        return jsonify({'success': False, 'message': 'Thiếu thông tin'}), 400
    if session.get('otp') != otp or session.get('email') != email:
        return jsonify({'success': False, 'message': 'OTP không đúng hoặc đã hết hạn'}), 400
    hashed_password = generate_password_hash(new_password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        session.pop('otp', None)
        session.pop('email', None)
        return jsonify({'success': True, 'message': 'Đặt lại mật khẩu thành công'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi máy chủ: {str(e)}'}), 500
    
@app.route('/Auth/ForgotPassword.html')
def serve_forgot_password():
    return send_from_directory(os.path.join(app.static_folder, 'src/Auth'), 'ForgotPassword.html')

# ✅ Admin Dashboard
@app.route('/Admin/Dashboard/Home.html')
def serve_admin_home():
    return send_from_directory(os.path.join(app.static_folder, 'Admin/Dashboard'), 'Home.html')

@app.route('/Admin/Dashboard/qlyuser.html')
def serve_admin_qlyuser():
    return send_from_directory(os.path.join(app.static_folder, 'Admin/Dashboard'), 'qlyuser.html')

# Trang chủ (cho student)
@app.route('/')
def serve_home():
    return send_from_directory(os.path.join(app.static_folder, 'src/pages'), 'Home.html')

# Serve trang bộ từ vựng
@app.route('/BoTuVung/botuvung.html')
def serve_vocab():
    return send_from_directory(os.path.join(app.static_folder, 'src/pages/BoTuVung'), 'botuvung.html')

# Serve trang minigame
@app.route('/Minigame/minigame_index.html')
def serve_minigame():
    return send_from_directory(os.path.join(app.static_folder, 'src/pages/Minigame'), 'minigame_index.html')

# Serve trang đăng nhập
@app.route('/Auth/LoginForm.html')
def serve_login():
    return send_from_directory(os.path.join(app.static_folder, 'src/Auth'), 'LoginForm.html')

# Serve trang đăng ký
@app.route('/Auth/RegisterForm.html')
def serve_register():
    return send_from_directory(os.path.join(app.static_folder, 'src/Auth'), 'RegisterForm.html')

# Serve các trang vocabulary
@app.route('/BoTuVung/<string:folder>/<string:filename>')
def serve_vocab_files(folder, filename):
    return send_from_directory(os.path.join(app.static_folder, 'src/pages/BoTuVung', folder), filename)

# Serve các trang games trong vocabulary folders
@app.route('/BoTuVung/<string:folder>/games/<string:filename>')
def serve_vocab_games(folder, filename):
    return send_from_directory(os.path.join(app.static_folder, 'src/pages/BoTuVung', folder, 'games'), filename)

# Fallback cho các file vocabulary cũ
@app.route('/BoTuVung/<string:filename>')
def serve_vocab_files_old(filename):
    return send_from_directory(os.path.join(app.static_folder, 'src/pages/BoTuVung'), filename)

PAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'pages'))


@app.route("/chatbox.html")
def serve_chatbox():
    return send_from_directory(PAGES_DIR, "chatbox.html")
    
@app.route('/frontend/src/pages/changepassword.html')
def serve_change_password():
    return send_from_directory(PAGES_DIR, 'changepassword.html')




if __name__ == '__main__':
    app.run(debug=True)
