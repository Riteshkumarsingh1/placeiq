# fetch_and_seed.py
import requests
import time
from app import create_app
from extensions import db
from models import College

app = create_app()

def fetch_colleges_from_api(state=None, limit=500):
    """Fetch colleges from the Indian Colleges Data API"""
    base_url = "http://localhost:3000/api/institutions"
    
    if state:
        url = f"{base_url}/search?state={state}&limit={limit}"
    else:
        url = f"{base_url}?limit={limit}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # API response structure ke hisaab se adjust karo
            colleges = data.get('institutions', data.get('data', data.get('colleges', [])))
            return colleges
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Request failed: {e}")
        return []

def fetch_courses_for_college(college_id):
    """Fetch courses for a specific college (for future use)"""
    url = f"http://localhost:3000/api/institution/{college_id}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('programmes', data.get('courses', []))
    except:
        pass
    return []

def save_to_database(colleges_data):
    """Save fetched colleges to database"""
    with app.app_context():
        added = 0
        skipped = 0
        total_fetched = len(colleges_data)
        
        print(f"\n📚 Total colleges fetched: {total_fetched}")
        print("💾 Saving to database...\n")
        
        for idx, item in enumerate(colleges_data):
            # Extract college name
            name = item.get('name', '') or item.get('college_name', '') or item.get('institution_name', '')
            if not name:
                continue
            
            # Extract city/district
            city = item.get('district', '') or item.get('city', '') or item.get('location', '')
            
            # Extract state
            state = item.get('state', '')
            
            # Extract stream/course type (if available)
            stream = 'Engineering'  # Default, baad mein update karna
            programmes = item.get('programmes', item.get('courses', []))
            if programmes:
                # Agar koi specific course type hai to use stream mein daal sakte ho
                first_course = programmes[0] if programmes else {}
                course_name = first_course.get('name', '').lower()
                if 'mba' in course_name or 'management' in course_name:
                    stream = 'MBA'
                elif 'mca' in course_name or 'computer' in course_name:
                    stream = 'MCA'
                # else default 'Engineering'
            
            # Check if college already exists
            existing = College.query.filter_by(name=name).first()
            if existing:
                skipped += 1
                if skipped % 100 == 0:
                    print(f"⏭️ Skipped {skipped} duplicates...")
                continue
            
            # Create new college
            college = College(
                name=name[:200],  # Max length 200
                city=city[:80] if city else None,
                state=state[:80] if state else None,
                stream=stream,
                tier=2,  # Default tier, baad mein NIRF se update hoga
                avg_ctc=None,
                placement_pct=None,
                fees_per_year=None,
                nirf_rank=None
            )
            db.session.add(college)
            added += 1
            
            if added % 50 == 0:
                print(f"✨ Added {added} colleges so far...")
                db.session.commit()  # Intermediate commit to save progress
        
        db.session.commit()
        print(f"\n{'='*50}")
        print(f"✅ SAVING COMPLETE!")
        print(f"   ✨ Added: {added} new colleges")
        print(f"   ⏭️ Skipped: {skipped} (duplicates)")
        print(f"   📊 Total in DB: {College.query.count()}")
        print(f"{'='*50}")

def update_streams_from_courses():
    """Optional: Baad mein is function se stream update kar sakte ho"""
    with app.app_context():
        colleges = College.query.filter_by(stream='Engineering').limit(100).all()
        updated = 0
        
        for college in colleges:
            # Search for college in API to get courses
            # Iske liye college name se search karna padega
            pass
        
        print(f"Updated streams for {updated} colleges")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 INDIAN COLLEGES DATA FETCHER")
    print("="*50)
    
    # Step 1: Fetch colleges
    print("\n📡 Fetching colleges from API...")
    colleges = fetch_colleges_from_api(limit=1000)
    print(f"✅ Fetched {len(colleges)} colleges")
    
    if not colleges:
        print("\n❌ No colleges fetched! Check if API is running.")
        print("   Make sure API is started with: npm run dev")
        exit()
    
    # Step 2: Save to database
    save_to_database(colleges)
    
    # Step 3: Show sample
    with app.app_context():
        sample = College.query.limit(5).all()
        print("\n📋 Sample colleges added:")
        for c in sample:
            print(f"   • {c.name} ({c.stream}) - {c.city}, {c.state}")