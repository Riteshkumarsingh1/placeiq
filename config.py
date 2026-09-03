import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Database ──────────────────────────────────────────────
    # Render 'postgres://' format deta hai, SQLAlchemy ko 'postgresql://' chahiye
    raw_url = os.environ.get('DATABASE_URL')
    if raw_url and raw_url.startswith('postgres://'):
        raw_url = raw_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = raw_url or "sqlite:///placeiq.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ── GROQ API ──────────────────────────────────────────────
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500,http://127.0.0.1:5000").split(",")

    # ── Security ──────────────────────────────────────────────
    BCRYPT_LOG_ROUNDS = 12
