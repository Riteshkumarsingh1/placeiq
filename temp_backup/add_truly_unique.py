# add_truly_unique.py
import requests
import psycopg2
from psycopg2.extras import execute_values

print("📡 Fetching all colleges from API...")
response = requests.get("http://localhost:3000/api/institutions?limit=40000", timeout=60)
data = response.json()
colleges = data.get('data', [])

print(f"✅ Fetched {len(colleges)} raw colleges")

# Unique colleges based on name
unique_map = {}
for item in colleges:
    name = item.get('institute_name', '')[:200]
    if not name:
        continue
    # Agar same name pehle se hai, toh skip (pehle wala hi rakho)
    if name not in unique_map:
        unique_map[name] = {
            'name': name,
            'city': item.get('district', '')[:80]
        }

unique_colleges = list(unique_map.values())
print(f"📊 Unique colleges after deduplication: {len(unique_colleges)}")

# Database connection
conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# Existing colleges
cur.execute("SELECT name FROM colleges")
existing_names = set(row[0] for row in cur.fetchall())
print(f"📚 Existing colleges: {len(existing_names)}")

# Naye colleges filter karo
new_colleges = []
for college in unique_colleges:
    if college['name'] not in existing_names:
        new_colleges.append((college['name'], college['city'], 'Engineering', 2))

print(f"✨ Truly new colleges to add: {len(new_colleges)}")

# Add new colleges
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
