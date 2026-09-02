import psycopg2
import re

def normalize(name):
    name = name.lower()
    name = re.sub(r'^indian institute of technology\s+', 'iit ', name)
    name = re.sub(r'^national institute of technology\s+', 'nit ', name)
    name = re.sub(r'^indian institute of management\s+', 'iim ', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# Get all colleges
cur.execute("SELECT id, name FROM colleges")
rows = cur.fetchall()

# Group by normalized name
groups = {}
for id, name in rows:
    norm = normalize(name)
    groups.setdefault(norm, []).append((id, name))

to_delete = []
to_keep = {}

for norm, colleges in groups.items():
    if len(colleges) <= 1:
        continue
    # Choose the one with the most complete data (prefer one with nirf_rank or avg_ctc)
    best_id = None
    best_name = None
    for id, name in colleges:
        cur.execute("SELECT nirf_rank, avg_ctc FROM colleges WHERE id = %s", (id,))
        rank, ctc = cur.fetchone()
        if (rank is not None and rank > 0) or (ctc is not None and ctc > 0):
            best_id = id
            best_name = name
            break
    if best_id is None:
        best_id = colleges[0][0]
        best_name = colleges[0][1]
    # Mark others for deletion
    for id, name in colleges:
        if id != best_id:
            to_delete.append(id)
            print(f"Will delete duplicate: {name} (keeping {best_name})")

if to_delete:
    cur.execute("DELETE FROM colleges WHERE id = ANY(%s)", (to_delete,))
    print(f"\n✅ Deleted {len(to_delete)} duplicate entries")
else:
    print("No duplicates found")

conn.commit()
cur.close()
conn.close()
