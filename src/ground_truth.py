
import sqlite3
import csv
from pathlib import Path

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

# Create separate ground-truth table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ground_truth (
    truth_id TEXT PRIMARY KEY,
    equipment_id TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    expected_condition TEXT NOT NULL,
    telemetry_reference TEXT,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

# Known test scenarios injected into telemetry
records = [
    (
        "GT-001", "PUMP-001", "PUMP_DEGRADATION",
        "ANOMALY", "FLOW",
        "Pump flow was deliberately reduced to 20.",
        "2026-10-22 00:00:00"
    ),
    (
        "GT-002", "PUMP-002", "PRESSURE_ANOMALY",
        "ANOMALY", "PRESSURE",
        "Pump pressure was deliberately increased to 8.5 bar.",
        "2026-10-22 00:00:00"
    ),
    (
        "GT-003", "TANK-001", "SENSOR_FAULT",
        "ANOMALY", "LEVEL",
        "Tank level reading was deliberately increased to 120 percent.",
        "2026-10-22 00:00:00"
    ),
    (
        "GT-004", "TANK-002", "LEAK_INDICATION",
        "ANOMALY", "LEVEL",
        "Tank level was deliberately reduced to 5 percent.",
        "2026-11-01 00:00:00"
    )
]

cursor.executemany("""
    INSERT OR IGNORE INTO ground_truth
    (truth_id, equipment_id, anomaly_type, expected_condition,
     telemetry_reference, description, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", records)

conn.commit()

# Export ground truth separately
cursor.execute("""
    SELECT * FROM ground_truth ORDER BY truth_id
""")

rows = cursor.fetchall()
columns = [description[0] for description in cursor.description]

Path("exports").mkdir(exist_ok=True)

with open("exports/ground_truth.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(columns)
    writer.writerows(rows)

print("Ground-truth records:", len(rows))
print("Ground-truth CSV exported successfully!")

conn.close()
