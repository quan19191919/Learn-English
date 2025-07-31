1. Đề tài
# Learn English
Web học tập Tiếng Anh 
---
## Tính năng chính 
- Đăng ký/Đăng nhập(với OTP Email cho học sinh)
- Flashcard học từ vựng thông minh
- Thông qua bộ từ vựng có thể chơi game để ôn lại từ vựng
- Quên mật khẩu và đổi mật khẩu
- Chatbot tạo đề thi theo chủ đề và hỏi ngẫu nhiên chatbot sẽ trả lời
- Dashboard quản trị (Admin)
- Quản lý người dùng (tài khoản trẻ)
- Giao diện tối/sáng và đa ngôn ngữ
---
## Công nghệ sử dụng
- Backend: Python(Flask)
- FrontendL HTML, CSS, JS, Bootstrap
- AI: API key Gemini Google
- Database: MySQL
- Khác: JWT (xác thực), sandbox code runner, logging, 2FA (OTP)

---
## Cài đặt

<pre>
bash
git clone https://github.com/quan19191919/Learn-English.git
</pre>

2. Cài đặt thư viện
   <pre>pip install -r requirements.txt</pre>
3. DATABASE
<pre>
   def get_db_connection():
   return mysql.connector.connect(
        host="localhost",
        user="root",
        password="25102004",
        database="yagi_english"
    )</pre>
4. Khởi động hệ thống
   <pre>python app.py</pre>
5. Mở trình duyệt
   <pre> http://127.0.0.1:5000 </pre>
6. Tài khoản mẫu
   
| Vai trò | Email           | Mật khẩu|
|---------|-----------------|---------|
| Admin   | admin@gmail.com | 123456  |
| Student | phuong@gmai.com | p1234   |

7. Cấu trúc thư mục
<pre>
    project/
├── README.md
├── LICENSE
├── requirements.txt
├── app.py
├── config/
│   └── config.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png
├── templates/
│   ├── index.html
│   └── base.html
├── modules/
│   ├── __init__.py
│   ├── module1/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── views.py
│   └── module2/
│       ├── __init__.py
│       ├── models.py
│       └── views.py
└── tests/
    └── test_app.py
</pre>
## RUN SERVER
<pre>
python app.py
Mở trình duyệt: http://127.0.0.1:5000 
</pre>
