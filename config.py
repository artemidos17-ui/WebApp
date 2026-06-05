import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")
SQLALCHEMY_TRACK_MODIFICATIONS = False
W_KEY = os.getenv("W_KEY")