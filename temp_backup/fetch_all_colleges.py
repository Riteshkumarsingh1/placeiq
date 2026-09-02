# fetch_all_colleges.py
import requests
import time
from app import create_app
from extensions import db
from models import College

app = create_app()

def fetch_all_colleges():
    """Fetch all colleges using pagination"""
    all_colleges = []
    page = 1
    limit = 500  # Per page limit
    
    print("\n" + "="*60)
    print("🚀 FETCHING ALL COLLEGES FROM API")
    print("="*60)
    
    while True:
        url = f"http://localhost:3000/api/institutions?page={page}&limit={limit}"
        print(f"\n📡 Fetching page {page}...")
        
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            # API response mein 'data' key mein colleges array hai
            colleges = data.get('data', [])
            
            if not colleges:
                print(f"   📭 No more colleges found. Stopping.")
                break
                
            all_colleges.extend(colleges)
            print(f"   ✅ Got {len(colleges)} colleges (Total so far: {len(all_colleges)})")
            
            # Check if we have reached the end
            if len(colleges) < limit:
                print(f"   📭 Last page reached.")
                break
                
            page += 1
            time.sleep(0.5)  # Be polite to API
            
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
            break
    
    return all_colleges

def save_to_database(colleges_data):
    """Save colleges to database"""
    print("\n" + "="*60)
    print("💾 SAVING COLLEGES TO DATABASE")
    print("="*60)
    
    with app.app_context():
        added = 0
        skipped = 0
        total = len(colleges_data)
        
        for idx, item in enumerate(colleges_data):
            name = item.get('institute_name', '')
            city = item.get('district', '')
            
            if not name:
                skipped += 1
                continue
            
            # Check if already exists
            existing = College.query.filter_by(name=name).first()
            if existing:
                skipped += 1
                continue
            
            college = College(
                name=name[:200],
                city=city[:80] if city else None,
                state=None,
                stream='Engineering',  # Default, API mein stream info nahi hai
                tier=2,
                avg_ctc=None,
                placement_pct=None,
                fees_per_year=None,
                nirf_rank=None
            )
            db.session.add(college)
            added += 1
            
            # Progress show karo
            if added % 1000 == 0:
                db.session.commit()
                print(f"   💾 Saved {added} colleges so far... ({added}/{total})")
        
        db.session.commit()
        return added, skipped

if __name__ == "__main__":
    # Step 1: Fetch all colleges
    all_colleges = fetch_all_colleges()
    
    if not all_colleges:
        print("\n❌ No colleges fetched! Make sure API is running.")
        print("   API should be at: http://localhost:3000")
        exit()
    
    print(f"\n📊 Total colleges fetched: {len(all_colleges)}")
    
    # Step 2: Save to database
    added, skipped = save_to_database(all_colleges)
    
    # Step 3: Final summary
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"   📥 Fetched: {len(all_colleges)} colleges")
    print(f"   ✨ Added: {added} new colleges")
    print(f"   ⏭️ Skipped: {skipped} (duplicates or invalid)")
    
    with app.app_context():
        total = College.query.count()
        print(f"   📊 Total in DB: {total}")
    print("="*60)
    