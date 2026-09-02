import psycopg2
conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()
cur.execute("SELECT name, highest_ctc FROM colleges WHERE name LIKE '%IIT Bombay%' OR name LIKE '%IIM Calcutta%'")
rows = cur.fetchall()
for row in rows:
    print(f"{row[0]}: {row[1]}")
cur.close()
conn.close()
