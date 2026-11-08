
import random
from datetime import datetime, timedelta

from src.database import get_connection

random.seed(20261022)


def generate_sensors_and_telemetry():
    conn = get_connection()
    cursor = conn.cursor()

    # Clear previous generated readings before rebuilding
    cursor.execute("DELETE FROM telemetry")
    cursor.execute("DELETE FROM sensor")

    sensors = []

    # 1. Pump sensors: flow and pressure
    cursor.execute("""
        SELECT pump_id, facility_id, nominal_flow
        FROM pump ORDER BY pump_id
    """)

    for pump_id, facility_id, nominal_flow in cursor.fetchall():
        sensors.append((
            facility_id, pump_id, "FLOW", "m3/hour",
            nominal_flow * 0.95
        ))
        sensors.append((
            facility_id, pump_id, "PRESSURE", "bar", 4.5
        ))

    # 2. Tank level sensors
    cursor.execute("""
        SELECT tank_id, facility_id, capacity, current_level
        FROM tank ORDER BY tank_id
    """)

    for tank_id, facility_id, capacity, current_level in cursor.fetchall():
        level_percent = (current_level / capacity) * 100

        sensors.append((
            facility_id, tank_id, "LEVEL", "%",
            level_percent
        ))

    # 3. Valve position sensors
    cursor.execute("""
        SELECT valve_id, facility_id, valve_state
        FROM valve ORDER BY valve_id
    """)

    for valve_id, facility_id, valve_state in cursor.fetchall():
        position = 100.0 if valve_state == "OPEN" else 0.0

        sensors.append((
            facility_id, valve_id, "VALVE_POSITION", "%",
            position
        ))

    # Insert sensor master records
    sensor_records = []

    for i, sensor in enumerate(sensors, start=1):
        facility_id, equipment_id, sensor_type, unit, base_value = sensor

        sensor_id = f"SNS-{i:03d}"

        sensor_records.append((
            sensor_id,
            facility_id,
            equipment_id,
            sensor_type,
            unit
        ))

    cursor.executemany("""
        INSERT INTO sensor
        (sensor_id, facility_id, equipment_id, sensor_type, unit)
        VALUES (?, ?, ?, ?, ?)
    """, sensor_records)

    # Generate exactly 100,000 telemetry readings
    total_readings = 100000
    readings_per_sensor = total_readings // len(sensors)
    extra_readings = total_readings % len(sensors)

    start_time = datetime(2026, 10, 22, 0, 0, 0)

    telemetry_records = []

    for index, sensor in enumerate(sensors):
        facility_id, equipment_id, sensor_type, unit, base_value = sensor
        sensor_id = f"SNS-{index + 1:03d}"

        count = readings_per_sensor
        if index < extra_readings:
            count += 1

        for reading_number in range(count):
            if sensor_type == "FLOW":
                value = random.gauss(base_value, base_value * 0.025)

            elif sensor_type == "PRESSURE":
                value = random.gauss(base_value, 0.15)

            elif sensor_type == "LEVEL":
                value = random.gauss(base_value, 1.5)
                value = max(0, min(100, value))

            elif sensor_type == "VALVE_POSITION":
                value = max(0, min(100, random.gauss(base_value, 0.5)))

            timestamp = start_time + timedelta(
                minutes=10 * reading_number
            )

            telemetry_records.append((
                sensor_id,
                round(value, 3),
                timestamp.isoformat()
            ))

    # Insert readings in batches to reduce memory usage
    batch_size = 10000

    for start in range(0, len(telemetry_records), batch_size):
        batch = telemetry_records[start:start + batch_size]

        cursor.executemany("""
            INSERT INTO telemetry
            (sensor_id, reading_value, reading_time)
            VALUES (?, ?, ?)
        """, batch)

    conn.commit()

    # Verify results
    cursor.execute("SELECT COUNT(*) FROM sensor")
    print("Total sensors:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM telemetry")
    print("Total telemetry readings:", cursor.fetchone()[0])

    conn.close()

    print("Sensor and telemetry generation completed!")


if __name__ == "__main__":
    generate_sensors_and_telemetry()
