# add_progressive.py
import requests
import psycopg2
import time

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

for page in range(1, 20):  # Pages 1 to 20
    print(f"\n📡 Fetching page {page}...")
    response = requests.get(f"http://localhost:3000/api/institutions?page={page}&limit=500")
    data = response.json()
    colleges = data.get('data', [])
    
    if not colleges:
        break
    
    inserted = 0
    for item in colleges:
        name = item.get('institute_name', '')[:200]
        city = item.get('district', '')[:80]
        
        if not name:
            continue
        
        cur.execute("SELECT 1 FROM colleges WHERE name = %s LIMIT 1", (name,))
        if cur.fetchone():
            continue
        
        cur.execute(
            "INSERT INTO colleges (name, city, stream, tier) VALUES (%s, %s, %s, %s)",
            (name, city, 'Engineering', 2)
        )
        inserted += 1
    
    conn.commit()
    print(f"   ✅ Page {page}: Added {inserted} new colleges")
    time.sleep(0.5)

cur.execute("SELECT COUNT(*) FROM colleges")
total = cur.fetchone()[0]
print(f"\n📊 Total colleges in DB: {total}")

cur.close()
conn.close()