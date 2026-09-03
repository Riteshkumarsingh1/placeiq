# app.py - Complete working version with auto-fetch from online sources
from flask import Flask, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging
import os
from datetime import datetime, timedelta

from config import Config
from extensions import db, migrate, jwt
from routes.auth import auth_bp
from routes.colleges import colleges_bp
from routes.predictor import predictor_bp
from routes.chat import chat_bp
from routes.ml import ml_bp
from routes.sentiment import sentiment_bp
from routes.auto_update import update_colleges_from_nirf, auto_update_database
from routes.digest import digest_bp 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Debug: Print config status
    print("\n" + "="*60)
    print("🔧 PLACEIQ CONFIGURATION STATUS")
    print("="*60)
    print(f"✅ Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    print(f"✅ GROQ API Key: {'✓ Loaded' if app.config.get('GROQ_API_KEY') else '✗ Missing'}")
    print(f"✅ JWT Secret: {'✓ Set' if app.config.get('JWT_SECRET_KEY') else '✗ Missing'}")
    print("="*60 + "\n")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(colleges_bp, url_prefix="/api/colleges")
    app.register_blueprint(predictor_bp, url_prefix="/api/predictor")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(ml_bp, url_prefix="/api/ml")
    app.register_blueprint(sentiment_bp, url_prefix="/api/sentiment")
    app.register_blueprint(digest_bp, url_prefix='/api/digest')

    # ========== TRAIN ML MODEL ==========
    with app.app_context():
        try:
            from routes.ml import train_college_ctc_model
            train_college_ctc_model(app)  # pass the current app
            print("✅ College CTC model trained on real data.")
        except Exception as e:
            print(f"⚠️ Could not train college CTC model: {e}")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "PlaceIQ API"}

    @app.route("/api/debug/config")
    def debug_config():
        return {
            "groq_api_key": "✓ Loaded" if app.config.get("GROQ_API_KEY") else "✗ Missing",
            "database_url": app.config.get("SQLALCHEMY_DATABASE_URI", "Not set"),
            "jwt_secret": "✓ Set" if app.config.get("JWT_SECRET_KEY") else "✗ Missing"
        }

    @app.route('/')
    @app.route('/placeiq-v4.html')
    def serve_frontend():
        return send_file('placeiq-v4.html')

    # ========== AUTO UPDATE SCHEDULER ==========
    
    # 1. Weekly full update from all sources (Sunday at 2 AM)
    scheduler.add_job(
        func=auto_update_database,
        trigger="cron",
        day_of_week="sun",
        hour=2,
        minute=0,
        id="weekly_full_update",
        replace_existing=True
    )
    logger.info("📅 Scheduled: Weekly full database update (Every Sunday at 2 AM)")
    
    # 2. Daily quick update for rankings (Every day at 3 AM)
    scheduler.add_job(
        func=update_colleges_from_nirf,
        trigger="cron",
        hour=3,
        minute=0,
        id="daily_ranking_update",
        replace_existing=True
    )
    logger.info("📅 Scheduled: Daily NIRF ranking update (Every day at 3 AM)")
    
    # 3. Run on startup (30 seconds after server starts)
    scheduler.add_job(
        func=auto_update_database,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=30),
        id="startup_update",
        replace_existing=True
    )
    logger.info("🚀 Scheduled: Initial database update (30 seconds after startup)")
    
    # Start the scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ Auto-update scheduler started successfully!")
    
    # Shutdown scheduler when app exits
    atexit.register(lambda: scheduler.shutdown())
    # ==========================================

    return app

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
        
        # Check if database is empty
        from models import College
        college_count = College.query.count()
        if college_count == 0:
            logger.warning("⚠️ Database is empty! Auto-update will run in 30 seconds to fetch colleges.")
            logger.info("💡 You can also manually seed with: python seed_colleges.py")
        else:
            logger.info(f"✅ Database already has {college_count} colleges")
    
    app.run(debug=True, port=5000)