# check_db.py
from app import create_app
from models import College

app = create_app()
with app.app_context():
    total = College.query.count()
    print(f"Total colleges: {total}")