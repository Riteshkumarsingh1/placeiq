# add_all_colleges_at_once.py
import requests
import psycopg2
from psycopg2.extras import execute_values

print("📡 Fetching all colleges from API...")
response = requests.get("http://localhost:3000/api/institutions?limit=40000", timeout=60)
data = response.json()
colleges = data.get('data', [])

print(f"✅ Fetched {len(colleges)} colleges")

# Database connection
conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# Pehle existing colleges ke names ka set banao
cur.execute("SELECT name FROM colleges")
existing_names = set(row[0] for row in cur.fetchall())
print(f"📚 Existing colleges: {len(existing_names)}")

# Naye colleges filter karo
new_colleges = []
for item in colleges:
    name = item.get('institute_name', '')[:200]
    city = item.get('district', '')[:80]
    
    if not name or name in existing_names:
        continue
    
    new_colleges.append((name, city, 'Engineering', 2))

print(f"✨ New colleges to add: {len(new_colleges)}")

# Batch insert karo
if new_colleges:
    execute_values(
        cur,
        "INSERT INTO colleges (name, city, stream, tier) VALUES %s",
        new_colleges
    )
    conn.commit()
    print(f"✅ Added {len(new_colleges)} new colleges!")
else:
    print("✅ No new colleges to add!")

# Final count
cur.execute("SELECT COUNT(*) FROM colleges")
total = cur.fetchone()[0]
print(f"\n📊 Total colleges in DB: {total}")

cur.close()
conn.close()
