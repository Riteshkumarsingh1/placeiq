import psycopg2
conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()
cur.execute("SELECT id, name FROM colleges WHERE name ILIKE '%iit bombay%'")
rows = cur.fetchall()
for row in rows:
    print(row)
cur.close()
conn.close()
