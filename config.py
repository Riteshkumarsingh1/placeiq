import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///placeiq.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500,http://127.0.0.1:5000").split(",")
    BCRYPT_LOG_ROUNDS = 12
