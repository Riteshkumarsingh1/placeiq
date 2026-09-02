# check_db_status.py
import psycopg2

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# 1. Total colleges
cur.execute("SELECT COUNT(*) FROM colleges")
total = cur.fetchone()[0]
print(f"📊 Total Colleges: {total}")

# 2. Real NIRF data wale
cur.execute("SELECT COUNT(*) FROM colleges WHERE nirf_rank IS NOT NULL")
real = cur.fetchone()[0]
print(f"✅ Real NIRF Data: {real} colleges")

# 3. Estimated data wale
cur.execute("SELECT COUNT(*) FROM colleges WHERE nirf_rank IS NULL AND avg_ctc IS NOT NULL")
estimated = cur.fetchone()[0]
print(f"⚠️ Estimated Data: {estimated} colleges")

# 4. Top 10 colleges by NIRF rank
cur.execute("""
    SELECT name, avg_ctc, placement_pct, nirf_rank 
    FROM colleges 
    WHERE nirf_rank IS NOT NULL 
    ORDER BY nirf_rank 
    LIMIT 10
""")
print("\n🏆 Top 10 Colleges (Real NIRF Data):")
for row in cur.fetchall():
    print(f"   {row[0]:25} | ₹{row[1]}L | {row[2]}% | Rank: {row[3]}")

cur.close()
conn.close()