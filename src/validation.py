
from src.database import get_connection


def validate_database():
    conn = get_connection()
    cursor = conn.cursor()

    errors = []

    print("\n========== DATABASE VALIDATION ==========")

    # 1. Check expected record counts
    expected_counts = {
        "facility": 3,
        "pump": 20,
        "tank": 30,
        "valve": 60,
        "pipe": 40,
        "sensor": 130,
        "telemetry": 100000
    }

    for table, expected in expected_counts.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cursor.fetchone()[0]

        status = "PASS" if actual == expected else "FAIL"
        print(f"{table}: {actual}/{expected} - {status}")

        if actual != expected:
            errors.append(f"Incorrect count in {table}")

    # 2. Check foreign key constraints
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()

    if fk_errors:
        errors.append("Foreign key violations found")
        print("Foreign key check: FAIL")
    else:
        print("Foreign key check: PASS")

    # 3. Check pipe endpoints exist
    cursor.execute("""
        SELECT COUNT(*)
        FROM pipe p
        WHERE NOT EXISTS (
            SELECT 1 FROM pump
            WHERE pump_id = p.source_node_id
              AND facility_id = p.facility_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM valve
            WHERE valve_id = p.source_node_id
              AND facility_id = p.facility_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM tank
            WHERE tank_id = p.source_node_id
              AND facility_id = p.facility_id
        )
    """)

    invalid_sources = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pipe p
        WHERE NOT EXISTS (
            SELECT 1 FROM pump
            WHERE pump_id = p.target_node_id
              AND facility_id = p.facility_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM valve
            WHERE valve_id = p.target_node_id
              AND facility_id = p.facility_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM tank
            WHERE tank_id = p.target_node_id
              AND facility_id = p.facility_id
        )
    """)

    invalid_targets = cursor.fetchone()[0]

    if invalid_sources == 0 and invalid_targets == 0:
        print("Pipe endpoint validation: PASS")
    else:
        errors.append("Invalid pipe endpoints found")
        print("Pipe endpoint validation: FAIL")

    # 4. Check sensor equipment relationships
    cursor.execute("""
        SELECT COUNT(*)
        FROM sensor s
        WHERE NOT EXISTS (
            SELECT 1 FROM pump p
            WHERE p.pump_id = s.equipment_id
              AND p.facility_id = s.facility_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM tank t
            WHERE t.tank_id = s.equipment_id
              AND t.facility_id = s.facility_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM valve v
            WHERE v.valve_id = s.equipment_id
              AND v.facility_id = s.facility_id
        )
    """)

    invalid_sensors = cursor.fetchone()[0]

    if invalid_sensors == 0:
        print("Sensor equipment validation: PASS")
    else:
        errors.append("Invalid sensor equipment relationships")
        print("Sensor equipment validation: FAIL")

    # 5. Check tank capacity
    cursor.execute("""
        SELECT COUNT(*)
        FROM tank
        WHERE capacity <= 0
           OR current_level < 0
           OR current_level > capacity
    """)

    invalid_tanks = cursor.fetchone()[0]

    if invalid_tanks == 0:
        print("Tank capacity validation: PASS")
    else:
        errors.append("Invalid tank capacity or level")
        print("Tank capacity validation: FAIL")

    # 6. Check telemetry readings are linked to sensors
    cursor.execute("""
        SELECT COUNT(*)
        FROM telemetry t
        LEFT JOIN sensor s ON t.sensor_id = s.sensor_id
        WHERE s.sensor_id IS NULL
    """)

    invalid_telemetry = cursor.fetchone()[0]

    if invalid_telemetry == 0:
        print("Telemetry relationship validation: PASS")
    else:
        errors.append("Telemetry contains invalid sensor IDs")
        print("Telemetry relationship validation: FAIL")

    # Final result
    print("\n========== FINAL RESULT ==========")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
    else:
        print("ALL VALIDATION CHECKS PASSED!")

    conn.close()


if __name__ == "__main__":
    validate_database()
