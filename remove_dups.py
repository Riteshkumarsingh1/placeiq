import psycopg2
import re

def normalize(name):
    name = name.lower()
    name = re.sub(r'^indian institute of technology ', 'iit ', name)
    name = re.sub(r'^national institute of technology ', 'nit ', name)
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

cur.execute("SELECT id, name FROM colleges ORDER BY id")
rows = cur.fetchall()

seen = {}
delete_ids = []

for id, name in rows:
    norm = normalize(name)
    if norm in seen:
        delete_ids.append(id)
    else:
        seen[norm] = id

if delete_ids:
    cur.execute("DELETE FROM colleges WHERE id = ANY(%s)", (delete_ids,))
    print(f"✅ Deleted {len(delete_ids)} duplicate colleges")
else:
    print("No duplicates found")

conn.commit()
cur.close()
conn.close()