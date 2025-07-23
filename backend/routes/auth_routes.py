from flask import Blueprint, request, jsonify, session, current_app
from models.database import get_db_connection
from utils.mail_otp import send_otp_mail
from flask_bcrypt import Bcrypt
import jwt, datetime, random

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username, email, password, role = data['username'], data['email'], data['password'], data.get('role', 'student')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        return jsonify({'message': 'Email đã tồn tại'}), 400
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s,%s,%s,%s)",
                   (username, email, hashed_pw, role))
    conn.commit()
    return jsonify({'message': 'Đăng ký thành công'})

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.json['email']
    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['otp_email'] = email
    send_otp_mail(current_app, email, otp)
    return jsonify({'message': 'OTP đã được gửi'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password, otp = data['email'], data['password'], data['otp']
    if session.get('otp') != otp or session.get('otp_email') != email:
        return jsonify({'message': 'OTP không hợp lệ'}), 401
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'Đăng nhập thành công', 'token': token,'username': user['username']})
    return jsonify({'message': 'Sai mật khẩu'}), 401

@auth_bp.route('/reset-password', methods=['POST'])
def reset():
    email, new_pass = request.json['email'], request.json['new_password']
    hashed = bcrypt.generate_password_hash(new_pass).decode('utf-8')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash=%s WHERE email=%s", (hashed, email))
    conn.commit()
    return jsonify({'message': 'Đặt lại mật khẩu thành công'})
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data['email']
    password = data['password']
    otp = data['otp']

    if session.get('otp') != otp or session.get('otp_email') != email:
        return jsonify({'success': False, 'message': 'OTP không hợp lệ'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'username': user['username'],
            'redirect': '/src/pages/Home.html'
        })

    return jsonify({'success': False, 'message': 'Sai mật khẩu'}), 401

@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND role='admin'", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'success': False, 'message': 'Tài khoản admin không tồn tại'}), 404

    if bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({
            'success': True,
            'username': user['username'],
            'redirect': '/src/pages/Admin/admin.html'
        })
    else:
        return jsonify({'success': False, 'message': 'Sai mật khẩu'}), 401
