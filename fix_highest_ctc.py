import psycopg2

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# Find colleges where highest_ctc is > 1000 (i.e., > 10 crore)
cur.execute("SELECT id, name, highest_ctc, avg_ctc FROM colleges WHERE highest_ctc > 1000")
rows = cur.fetchall()

if rows:
    print(f"Found {len(rows)} suspicious entries. Fixing...")
    for id, name, high, avg in rows:
        if avg and high > avg * 20:
            new_high = round(high / 100, 1)
            cur.execute("UPDATE colleges SET highest_ctc = %s WHERE id = %s", (new_high, id))
            print(f"  Fixed {name}: {high}L → {new_high}L")
    conn.commit()
else:
    print("No extremely high highest_ctc values found.")

cur.close()
conn.close()
