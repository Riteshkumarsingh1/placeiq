# fetch_unique_colleges.py
import requests
import time
from app import create_app
from extensions import db
from models import College

app = create_app()

def fetch_unique_colleges():
    """Fetch only unique colleges from API"""
    all_colleges = []
    seen_names = set()
    page = 1
    limit = 500
    
    print("\n" + "="*60)
    print("🚀 FETCHING UNIQUE COLLEGES FROM API")
    print("="*60)
    
    while page <= 10:  # Sirf first 10 pages fetch karo (pehle test ke liye)
        url = f"http://localhost:3000/api/institutions?page={page}&limit={limit}"
        print(f"\n📡 Fetching page {page}...")
        
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            colleges = data.get('data', [])
            
            if not colleges:
                print(f"   📭 No more colleges found.")
                break
            
            new_count = 0
            for item in colleges:
                name = item.get('institute_name', '')
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_colleges.append(item)
                    new_count += 1
            
            print(f"   ✅ Got {len(colleges)} colleges, {new_count} new (Total unique: {len(all_colleges)})")
            
            if new_count == 0:
                print(f"   📭 No new colleges found. Stopping.")
                break
                
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            break
    
    return all_colleges

def save_to_database(colleges_data):
    """Save unique colleges to database"""
    print("\n" + "="*60)
    print("💾 SAVING TO DATABASE")
    print("="*60)
    
    with app.app_context():
        added = 0
        skipped = 0
        
        for idx, item in enumerate(colleges_data):
            name = item.get('institute_name', '')
            city = item.get('district', '')
            
            if not name:
                skipped += 1
                continue
            
            existing = College.query.filter_by(name=name).first()
            if existing:
                skipped += 1
                continue
            
            college = College(
                name=name[:200],
                city=city[:80] if city else None,
                state=None,
                stream='Engineering',
                tier=2,
                avg_ctc=None,
                placement_pct=None,
                fees_per_year=None,
                nirf_rank=None
            )
            db.session.add(college)
            added += 1
            
            if added % 500 == 0:
                db.session.commit()
                print(f"   💾 Saved {added} colleges so far...")
        
        db.session.commit()
        return added, skipped

if __name__ == "__main__":
    # Stop the current infinite loop script (Ctrl+C)
    print("⚠️ Make sure you stopped the previous script with Ctrl+C")
    input("Press Enter to continue...")
    
    # Fetch unique colleges
    colleges = fetch_unique_colleges()
    
    print(f"\n📊 Total unique colleges fetched: {len(colleges)}")
    
    # Save to database
    added, skipped = save_to_database(colleges)
    
    # Final summary
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"   ✨ Added: {added} new colleges")
    print(f"   ⏭️ Skipped: {skipped} (duplicates)")
    
    with app.app_context():
        total = College.query.count()
        print(f"   📊 Total in DB: {total}")
    print("="*60)