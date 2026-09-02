import psycopg2

conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
cur = conn.cursor()

# First, check suspicious values (> 5000)
cur.execute('SELECT id, name, highest_ctc, avg_ctc FROM colleges WHERE highest_ctc > 5000')
rows = cur.fetchall()
if rows:
    print(f'Found {len(rows)} colleges with extremely high highest_ctc (> 5000). Fixing...')
    for id, name, high, avg in rows:
        # Assume the value is in rupees crores? or something? Divide by 100 to get lakhs.
        new_high = high / 100
        cur.execute('UPDATE colleges SET highest_ctc = %s WHERE id = %s', (new_high, id))
        print(f'  Fixed {name}: {high} → {new_high} (lakhs)')
    conn.commit()
else:
    print('No extremely high values (>5000) found.')

# Next, check values between 1000 and 5000 – might be in lakhs but still too high for realistic highest offer?
cur.execute('SELECT id, name, highest_ctc, avg_ctc FROM colleges WHERE highest_ctc BETWEEN 1000 AND 5000')
rows = cur.fetchall()
if rows:
    print(f'\nFound {len(rows)} colleges with highest_ctc between 1000-5000 (i.e., {rows[0][2]/100}Cr to {rows[0][2]/100}Cr). These might be in crore?')
    for id, name, high, avg in rows:
        # If it's > 20 times avg, it's probably in crore.
        if avg and high > avg * 20:
            new_high = high / 100
            cur.execute('UPDATE colleges SET highest_ctc = %s WHERE id = %s', (new_high, id))
            print(f'  Fixed {name}: {high} → {new_high}')
    conn.commit()
else:
    print('No colleges with highest_ctc between 1000-5000.')

# Finally, check values between 100 and 1000 – these are likely already in lakhs.
cur.execute('SELECT COUNT(*) FROM colleges WHERE highest_ctc BETWEEN 100 AND 1000')
count = cur.fetchone()[0]
print(f'\nColleges with highest_ctc between 100-1000 (already in lakhs): {count}')

cur.close()
conn.close()
