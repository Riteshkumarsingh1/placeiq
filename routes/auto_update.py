# routes/auto_update.py
import requests
import json
from datetime import datetime
import logging
import time
from bs4 import BeautifulSoup
import re
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollegeDataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def _normalize_name(self, name):
        name = name.lower()
        name = re.sub(r'^indian institute of technology\s+', 'iit ', name)
        name = re.sub(r'^national institute of technology\s+', 'nit ', name)
        name = re.sub(r'^indian institute of management\s+', 'iim ', name)
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name

    def fetch_from_nirf(self):
        """Fetch colleges from NIRF official HTML page"""
        colleges = []
        try:
            nirf_url = "https://www.nirfindia.org/2024/EngineeringRanking"
            response = requests.get(nirf_url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table')

                if table:
                    rows = table.find_all('tr')
                    for i, row in enumerate(rows[1:101], 1):
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            name_col = cols[1] if len(cols) > 1 else None
                            if name_col:
                                name = name_col.text.strip()
                                name = re.sub(r'^\d+\s*', '', name)
                                name = re.sub(r'\s+', ' ', name)
                                if name and len(name) > 5:
                                    college = {
                                        'name': name,
                                        'nirf_rank': i,
                                        'tier': self._calculate_tier(i),
                                        'stream': 'Engineering',
                                        'avg_ctc': self._estimate_ctc_from_rank(i),
                                        'placement_pct': self._estimate_placement_from_rank(i),
                                        'city': '',
                                        'state': ''
                                    }
                                    colleges.append(college)

            if not colleges:
                colleges = self._get_fallback_nirf_data()
        except Exception as e:
            print(f"NIRF fetch error: {e}")
            colleges = self._get_fallback_nirf_data()
        return colleges

    def _estimate_ctc_from_rank(self, rank):
        if rank <= 10:
            return 28.0
        elif rank <= 20:
            return 22.0
        elif rank <= 50:
            return 16.0
        elif rank <= 100:
            return 10.0
        elif rank <= 200:
            return 7.0
        else:
            return 5.0

    def _estimate_placement_from_rank(self, rank):
        if rank <= 10:
            return 95
        elif rank <= 20:
            return 92
        elif rank <= 50:
            return 88
        elif rank <= 100:
            return 82
        elif rank <= 200:
            return 75
        else:
            return 65

    def _get_fallback_nirf_data(self):
        return [
            {"name": "IIT Madras", "nirf_rank": 1, "tier": 1, "stream": "Engineering", "avg_ctc": 26.8, "placement_pct": 92, "city": "Chennai", "state": "Tamil Nadu"},
            {"name": "IIT Delhi", "nirf_rank": 2, "tier": 1, "stream": "Engineering", "avg_ctc": 27.0, "placement_pct": 94, "city": "New Delhi", "state": "Delhi"},
            {"name": "IIT Bombay", "nirf_rank": 3, "tier": 1, "stream": "Engineering", "avg_ctc": 28.5, "placement_pct": 95, "city": "Mumbai", "state": "Maharashtra"},
        ]

    def fetch_from_college_api(self):
        return self._get_sample_colleges()

    def _get_sample_colleges(self):
        return [
            {"name": "VIT Vellore", "city": "Vellore", "state": "Tamil Nadu", "stream": "Engineering", "avg_ctc": 9.5, "placement_pct": 83, "tier": 2},
            {"name": "SRM University", "city": "Chennai", "state": "Tamil Nadu", "stream": "Engineering", "avg_ctc": 7.5, "placement_pct": 80, "tier": 2},
            {"name": "IIM Ahmedabad", "city": "Ahmedabad", "state": "Gujarat", "stream": "MBA", "avg_ctc": 36.0, "placement_pct": 100, "tier": 1},
        ]

    def fetch_from_aishe(self):
        return []

    def _calculate_tier(self, rank):
        if rank <= 50:
            return 1
        elif rank <= 150:
            return 2
        else:
            return 3

    def _calculate_tier_by_ctc(self, ctc):
        if ctc >= 15:
            return 1
        elif ctc >= 8:
            return 2
        else:
            return 3

    def _detect_stream(self, text):
        text_lower = text.lower()
        if 'engineering' in text_lower or 'b.tech' in text_lower:
            return 'Engineering'
        elif 'mba' in text_lower or 'management' in text_lower:
            return 'MBA'
        elif 'mca' in text_lower:
            return 'MCA'
        else:
            return 'Other'

    def fetch_all_sources(self):
        """Fetch data from all sources and combine"""
        all_colleges = []
        print("\n📚 Fetching from NIRF...")
        nirf_colleges = self.fetch_from_nirf()
        all_colleges.extend(nirf_colleges)
        time.sleep(1)
        print("\n📚 Fetching from College data sources...")
        api_colleges = self.fetch_from_college_api()
        all_colleges.extend(api_colleges)

        # Remove duplicates by name (simple)
        unique_colleges = {}
        for college in all_colleges:
            name = college.get('name', '').lower().strip()
            if name and name not in unique_colleges:
                unique_colleges[name] = college
        result = list(unique_colleges.values())
        print(f"\n✅ Total unique colleges fetched: {len(result)}")
        return result


def auto_update_database():
    """Main function to auto-update database from all sources"""
    from extensions import db
    from models import College
    from app import create_app

    print("\n" + "=" * 70)
    print("🔄 PLACEIQ AUTO DATABASE UPDATE STARTED")
    print(f"📅 Time: {datetime.now()}")
    print("=" * 70)

    app = create_app()
    with app.app_context():
        try:
            fetcher = CollegeDataFetcher()
            colleges_data = fetcher.fetch_all_sources()

            added = 0
            updated = 0
            skipped = 0

            # Pre‑fetch all existing colleges to avoid repeated queries
            existing_colleges = College.query.all()
            # Build a set of normalized names of existing colleges
            existing_norm_names = {fetcher._normalize_name(c.name) for c in existing_colleges}

            for college_data in colleges_data:
                if not college_data.get('name'):
                    continue

                name = college_data['name']
                norm_name = fetcher._normalize_name(name)

                if norm_name in existing_norm_names:
                    skipped += 1
                else:
                    new_college = College(
                        name=name,
                        city=college_data.get('city', ''),
                        state=college_data.get('state', ''),
                        stream=college_data.get('stream', 'Engineering'),
                        tier=college_data.get('tier', 2),
                        nirf_rank=college_data.get('nirf_rank'),
                        avg_ctc=college_data.get('avg_ctc'),
                        placement_pct=college_data.get('placement_pct')
                    )
                    db.session.add(new_college)
                    added += 1

            db.session.commit()
            print("\n" + "=" * 70)
            print("✅ AUTO UPDATE COMPLETE!")
            print(f"   ✨ Added: {added} new colleges")
            print(f"   📝 Updated: {updated} existing colleges")
            print(f"   ⏭️ Skipped: {skipped} (no changes or duplicates)")
            print(f"   📊 Total in DB: {College.query.count()}")
            print("=" * 70)
            return True
        except Exception as e:
            print(f"\n❌ Auto update failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def update_colleges_from_nirf():
    """Scheduler wrapper function"""
    auto_update_database()


def update_all_colleges_with_estimates():
    """Update all colleges with estimated data"""
    from extensions import db
    from models import College
    from app import create_app

    print("\n" + "=" * 70)
    print("🔄 UPDATING ALL COLLEGES WITH ESTIMATED DATA")
    print("=" * 70)

    app = create_app()
    with app.app_context():
        colleges = College.query.all()
        if not colleges:
            print("No colleges found.")
            return

        updated = 0
        for college in colleges:
            if college.avg_ctc is None:
                if college.tier == 1:
                    college.avg_ctc = 20.0
                elif college.tier == 2:
                    college.avg_ctc = 9.0
                else:
                    college.avg_ctc = 5.0
                updated += 1

        db.session.commit()
        print(f"\n✅ Updated {updated} colleges with estimated data.")