
import sqlite3
import json
import csv
from pathlib import Path

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

# Exact injected values for each test scenario
scenarios = [
    ("GT-001", "PUMP-001", "FLOW", 20.0),
    ("GT-002", "PUMP-002", "PRESSURE", 8.5),
    ("GT-003", "TANK-001", "LEVEL", 120.0),
    ("GT-004", "TANK-002", "LEVEL", 5.0)
]

for truth_id, equipment_id, sensor_type, value in scenarios:

    cursor.execute("""
        SELECT t.telemetry_id, t.reading_time, t.reading_value
        FROM telemetry t
        JOIN sensor s ON t.sensor_id = s.sensor_id
        WHERE s.equipment_id = ?
          AND s.sensor_type = ?
          AND t.reading_value = ?
        ORDER BY t.telemetry_id
        LIMIT 1
    """, (equipment_id, sensor_type, value))

    reading = cursor.fetchone()

    if reading is None:
        print(f"WARNING: No matching telemetry for {truth_id}")
        continue

    telemetry_id, reading_time, reading_value = reading

    cursor.execute("""
        UPDATE ground_truth
        SET telemetry_reference = ?,
            created_at = ?
        WHERE truth_id = ?
    """, (str(telemetry_id), reading_time, truth_id))

    print(
        f"{truth_id}: telemetry ID={telemetry_id}, "
        f"value={reading_value}, time={reading_time}"
    )

conn.commit()

# Export updated ground truth to CSV and JSON
cursor.execute("""
    SELECT * FROM ground_truth ORDER BY truth_id
""")

columns = [item[0] for item in cursor.description]
rows = cursor.fetchall()

records = [dict(zip(columns, row)) for row in rows]

Path("exports").mkdir(exist_ok=True)

with open("exports/ground_truth.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)

with open("exports/ground_truth.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=4)

print("\nGround-truth links updated!")
print("CSV and JSON exported successfully.")

conn.close()
