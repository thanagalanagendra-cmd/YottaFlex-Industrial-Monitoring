import sqlite3

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

cursor.execute("""
    UPDATE simulation_run
    SET mode_id = 'MODE-001'
    WHERE simulation_id = 'SIM-2026-000001'
      AND facility_id = 'FAC-001'
""")

conn.commit()

print("Updated records:", cursor.rowcount)

cursor.execute("""
    SELECT s.simulation_id, s.facility_id,
           m.mode_name, s.run_status
    FROM simulation_run s
    JOIN operating_mode m
      ON s.mode_id = m.mode_id
""")

for row in cursor.fetchall():
    print(row)

conn.close()