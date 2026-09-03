import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Database ──────────────────────────────────────────────
    # Render 'postgres://' format deta hai, SQLAlchemy ko 'postgresql://' chahiye
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "postgresql://postgres:12345@localhost:5432/placeiq"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ── GROQ API (chatbot) ───────────────────────────────────
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500,http://127.0.0.1:5000").split(",")

    # ── Security ──────────────────────────────────────────────
    BCRYPT_LOG_ROUNDS = 12
