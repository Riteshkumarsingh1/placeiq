import psycopg2
conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()
# Convert all highest_ctc that are > 5000 (likely in crore) to lakhs by dividing by 100
cur.execute("UPDATE colleges SET highest_ctc = highest_ctc / 100 WHERE highest_ctc > 5000")
conn.commit()
print(f"Updated {cur.rowcount} colleges")
cur.execute("SELECT name, highest_ctc FROM colleges WHERE name LIKE '%IIT Delhi%' OR name LIKE '%IIT Bombay%'")
for name, val in cur.fetchall():
    print(f"{name}: {val}")
cur.close()
conn.close()
