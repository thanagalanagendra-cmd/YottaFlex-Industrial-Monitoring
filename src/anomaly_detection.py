

from src.database import get_connection


def detect_anomalies():
    conn = get_connection()
    cursor = conn.cursor()

    # Clear previous generated alarm results
    cursor.execute("DELETE FROM alarm")

    detected = 0

    # ==========================================
    # RULES 1, 2 AND 3: CHECK TELEMETRY READINGS
    # ==========================================

    cursor.execute("""
        SELECT
            s.sensor_id,
            s.facility_id,
            s.equipment_id,
            s.sensor_type,
            t.reading_value,
            t.reading_time
        FROM telemetry t
        JOIN sensor s ON t.sensor_id = s.sensor_id
        ORDER BY t.reading_time
    """)

    readings = cursor.fetchall()

    for sensor_id, facility_id, equipment_id, sensor_type, value, timestamp in readings:

        issue_type = None
        severity = "MEDIUM"

        # Rule 1: Physically invalid sensor values
        if sensor_type == "LEVEL" and not 0 <= value <= 100:
            issue_type = "SENSOR_FAULT"
            severity = "HIGH"

        elif sensor_type == "VALVE_POSITION" and not 0 <= value <= 100:
            issue_type = "SENSOR_FAULT"
            severity = "HIGH"

        elif sensor_type == "PRESSURE" and not 0 <= value <= 15:
            issue_type = "SENSOR_FAULT"
            severity = "HIGH"

        # Rule 2: Pump degradation
        elif sensor_type == "FLOW":
            cursor.execute("""
                SELECT nominal_flow
                FROM pump
                WHERE pump_id = ?
            """, (equipment_id,))

            result = cursor.fetchone()

            if result and value < result[0] * 0.75:
                issue_type = "PUMP_DEGRADATION"
                severity = "HIGH"

        # Rule 3: High pressure anomaly
        elif sensor_type == "PRESSURE" and value > 5.5:
            issue_type = "PRESSURE_ANOMALY"
            severity = "HIGH"

        # Store detected alarm
        if issue_type:
            alarm_id = f"ALARM-{detected + 1:06d}"

            cursor.execute("""
                INSERT INTO alarm (
                    alarm_id,
                    facility_id,
                    issue_type,
                    severity,
                    ground_truth,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alarm_id,
                facility_id,
                issue_type,
                severity,
                0,
                timestamp
            ))

            detected += 1

    # ==========================================
    # RULE 4: POSSIBLE LEAK DETECTION
    # ==========================================

    cursor.execute("""
        SELECT *
        FROM (
            SELECT
                s.facility_id,
                s.equipment_id,
                t.reading_value,
                t.reading_time,
                LAG(t.reading_value) OVER (
                    PARTITION BY s.sensor_id
                    ORDER BY t.reading_time
                ) AS previous_value
            FROM telemetry t
            JOIN sensor s ON t.sensor_id = s.sensor_id
            WHERE s.sensor_type = 'LEVEL'
        )
        WHERE previous_value BETWEEN 0 AND 100
          AND reading_value BETWEEN 0 AND 100
          AND previous_value - reading_value >= 20
    """)

    leak_events = cursor.fetchall()

    for facility_id, tank_id, value, timestamp, previous_value in leak_events:

        alarm_id = f"ALARM-{detected + 1:06d}"

        cursor.execute("""
            INSERT INTO alarm (
                alarm_id,
                facility_id,
                issue_type,
                severity,
                ground_truth,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alarm_id,
            facility_id,
            "LEAK_INDICATION",
            "HIGH",
            0,
            timestamp
        ))

        detected += 1

    # ==========================================
    # DISPLAY RESULTS
    # ==========================================

    conn.commit()

    print("Telemetry readings checked:", len(readings))
    print("Detected alarms:", detected)

    cursor.execute("""
        SELECT issue_type, COUNT(*)
        FROM alarm
        GROUP BY issue_type
    """)

    print("\nAlarm summary:")

    for issue_type, count in cursor.fetchall():
        print(issue_type, ":", count)

    conn.close()


if __name__ == "__main__":
    detect_anomalies()

  