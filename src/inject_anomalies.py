
from src.database import get_connection


def inject_anomalies():
    conn = get_connection()
    cursor = conn.cursor()

    # Scenario 1: Pump degradation
    cursor.execute("""
        UPDATE telemetry
        SET reading_value = 20
        WHERE telemetry_id = (
            SELECT t.telemetry_id
            FROM telemetry t
            JOIN sensor s ON t.sensor_id = s.sensor_id
            WHERE s.equipment_id = 'PUMP-001'
              AND s.sensor_type = 'FLOW'
            ORDER BY t.reading_time
            LIMIT 1
        )
    """)

    # Scenario 2: High pressure anomaly
    cursor.execute("""
        UPDATE telemetry
        SET reading_value = 8.5
        WHERE telemetry_id = (
            SELECT t.telemetry_id
            FROM telemetry t
            JOIN sensor s ON t.sensor_id = s.sensor_id
            WHERE s.equipment_id = 'PUMP-002'
              AND s.sensor_type = 'PRESSURE'
            ORDER BY t.reading_time
            LIMIT 1
        )
    """)

    # Scenario 3: Invalid tank-level sensor reading
    cursor.execute("""
        UPDATE telemetry
        SET reading_value = 120
        WHERE telemetry_id = (
            SELECT t.telemetry_id
            FROM telemetry t
            JOIN sensor s ON t.sensor_id = s.sensor_id
            WHERE s.equipment_id = 'TANK-001'
              AND s.sensor_type = 'LEVEL'
            ORDER BY t.reading_time
            LIMIT 1
        )
    """)

    # Scenario 4: Sudden tank-level drop
    cursor.execute("""
        UPDATE telemetry
        SET reading_value = 5
        WHERE telemetry_id = (
            SELECT t.telemetry_id
            FROM telemetry t
            JOIN sensor s ON t.sensor_id = s.sensor_id
            WHERE s.equipment_id = 'TANK-002'
              AND s.sensor_type = 'LEVEL'
            ORDER BY t.reading_time DESC
            LIMIT 1
        )
    """)

    conn.commit()
    conn.close()

    print("Four test scenarios injected successfully!")


if __name__ == "__main__":
    inject_anomalies()
