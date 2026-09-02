# estimate_placement.py
import psycopg2

# Database connection
conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# Baaki colleges ke liye tier-based estimates
cur.execute("""
    UPDATE colleges 
    SET avg_ctc = CASE 
        WHEN tier = 1 THEN 15.0
        WHEN tier = 2 THEN 8.0
        ELSE 4.5
    END,
    placement_pct = CASE
        WHEN tier = 1 THEN 85
        WHEN tier = 2 THEN 70
        ELSE 55
    END
    WHERE avg_ctc IS NULL
""")

conn.commit()

# Check kitne update hue
print(f"✅ Updated {cur.rowcount} colleges with estimated placement data")

# Close connection
cur.close()
conn.close()