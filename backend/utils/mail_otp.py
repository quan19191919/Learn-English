import smtplib
from email.mime.text import MIMEText

def send_otp(receiver_email, otp_code):
    sender_email = "dangthaiphuong6789@gmail.com"
    app_password = "iayr sssw ctsj fkdn"

    msg = MIMEText(f"Mã OTP của bạn là: {otp_code}")
    msg["Subject"] = "Mã xác nhận OTP"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
