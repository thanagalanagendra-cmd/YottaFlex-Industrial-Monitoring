
import sqlite3

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT
        gt.truth_id,
        gt.equipment_id,
        gt.anomaly_type,
        gt.telemetry_reference,
        s.sensor_type,
        t.reading_value
    FROM ground_truth gt
    LEFT JOIN telemetry t
        ON t.telemetry_id = CAST(gt.telemetry_reference AS INTEGER)
    LEFT JOIN sensor s
        ON s.sensor_id = t.sensor_id
    ORDER BY gt.truth_id
""")

records = cursor.fetchall()

expected = {
    "GT-001": ("PUMP-001", "FLOW", 20.0),
    "GT-002": ("PUMP-002", "PRESSURE", 8.5),
    "GT-003": ("TANK-001", "LEVEL", 120.0),
    "GT-004": ("TANK-002", "LEVEL", 5.0)
}

passed = 0

for truth_id, equipment, anomaly, telemetry_id, sensor_type, value in records:
    expected_equipment, expected_sensor, expected_value = expected[truth_id]

    valid = (
        equipment == expected_equipment
        and sensor_type == expected_sensor
        and value == expected_value
        and telemetry_id is not None
    )

    print(f"{truth_id}: {'PASS' if valid else 'FAIL'}")

    if valid:
        passed += 1

print(f"\nGround-truth validation: {passed}/{len(expected)} PASS")

conn.close()

