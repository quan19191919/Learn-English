import os

MAIL_CONFIG = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USERNAME": os.getenv("MAIL_USER"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASS"),
    "MAIL_USE_TLS": True
}

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "2510200425102004",
    "database": "yagi_english"
}

SECRET_KEY = os.getenv("SECRET_KEY", "devkey123")
