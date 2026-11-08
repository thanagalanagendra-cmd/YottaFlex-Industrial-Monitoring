
from src.database import get_connection


def inspect_data():
    conn = get_connection()
    cursor = conn.cursor()

    queries = {
        "Facilities": "SELECT COUNT(*) FROM facility",
        "Pumps": "SELECT COUNT(*) FROM pump",
        "Tanks": "SELECT COUNT(*) FROM tank",
        "Valves": "SELECT COUNT(*) FROM valve",
        "Pipes": "SELECT COUNT(*) FROM pipe",
        "Sensors": "SELECT COUNT(*) FROM sensor",
        "Telemetry": "SELECT COUNT(*) FROM telemetry",
        "Alarms": "SELECT COUNT(*) FROM alarm"
    }

    print("\n========== DATABASE SUMMARY ==========")

    for name, query in queries.items():
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"{name}: {count}")

    print("\n========== SENSOR SUMMARY ==========")

    cursor.execute("""
        SELECT sensor_type, COUNT(*)
        FROM sensor
        GROUP BY sensor_type
    """)

    for sensor_type, count in cursor.fetchall():
        print(sensor_type, ":", count)

    print("\n========== TELEMETRY SUMMARY ==========")

    cursor.execute("""
        SELECT
            s.sensor_type,
            ROUND(MIN(t.reading_value), 2),
            ROUND(AVG(t.reading_value), 2),
            ROUND(MAX(t.reading_value), 2)
        FROM telemetry t
        JOIN sensor s ON t.sensor_id = s.sensor_id
        GROUP BY s.sensor_type
    """)

    for row in cursor.fetchall():
        print(row)

    conn.close()


if __name__ == "__main__":
    inspect_data()
