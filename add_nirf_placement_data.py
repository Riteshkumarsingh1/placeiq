# add_nirf_placement_data.py
import psycopg2

# NIRF Top Colleges ka real placement data
NIRF_PLACEMENT_DATA = [
    {"name": "IIT Bombay", "avg_ctc": 28.5, "placement_pct": 95},
    {"name": "IIT Delhi", "avg_ctc": 27.0, "placement_pct": 94},
    {"name": "IIT Madras", "avg_ctc": 26.8, "placement_pct": 92},
    {"name": "IIT Kanpur", "avg_ctc": 25.0, "placement_pct": 90},
    {"name": "IIT Kharagpur", "avg_ctc": 24.0, "placement_pct": 91},
    {"name": "IIT Roorkee", "avg_ctc": 22.0, "placement_pct": 89},
    {"name": "IIT Guwahati", "avg_ctc": 21.5, "placement_pct": 88},
    {"name": "IIT Hyderabad", "avg_ctc": 20.8, "placement_pct": 87},
    {"name": "NIT Trichy", "avg_ctc": 14.0, "placement_pct": 89},
    {"name": "NIT Warangal", "avg_ctc": 13.0, "placement_pct": 87},
    {"name": "IIIT Hyderabad", "avg_ctc": 22.0, "placement_pct": 93},
    {"name": "BITS Pilani", "avg_ctc": 20.5, "placement_pct": 92},
    {"name": "VIT Vellore", "avg_ctc": 9.5, "placement_pct": 83},
    {"name": "IIM Ahmedabad", "avg_ctc": 36.0, "placement_pct": 100},
    {"name": "IIM Bangalore", "avg_ctc": 34.0, "placement_pct": 100},
    {"name": "IIM Calcutta", "avg_ctc": 34.5, "placement_pct": 100},
]

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

for data in NIRF_PLACEMENT_DATA:
    cur.execute("""
        UPDATE colleges 
        SET avg_ctc = %s, placement_pct = %s 
        WHERE name ILIKE %s
    """, (data['avg_ctc'], data['placement_pct'], f"%{data['name']}%"))

conn.commit()
print("✅ Placement data added for top colleges!")