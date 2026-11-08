
from src.database import get_connection


def generate_pipes():
    conn = get_connection()
    cursor = conn.cursor()

    # Rebuild the generated baseline topology
    cursor.execute("DELETE FROM pipe")

    pipe_number = 1

    for facility_number in range(1, 4):
        facility_id = f"FAC-{facility_number:03d}"

        cursor.execute(
            "SELECT pump_id FROM pump WHERE facility_id = ? ORDER BY pump_id",
            (facility_id,)
        )
        pumps = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT tank_id FROM tank WHERE facility_id = ? ORDER BY tank_id",
            (facility_id,)
        )
        tanks = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT valve_id FROM valve WHERE facility_id = ? ORDER BY valve_id",
            (facility_id,)
        )
        valves = [row[0] for row in cursor.fetchall()]

        for i, pump_id in enumerate(pumps):
            tank_id = tanks[i % len(tanks)]
            valve_id = valves[i % len(valves)]

            # Connection 1: Pump to Valve
            cursor.execute("""
                INSERT INTO pipe VALUES (?, ?, ?, ?, ?)
            """, (
                f"PIPE-{pipe_number:03d}",
                facility_id,
                pump_id,
                valve_id,
                100.0
            ))
            pipe_number += 1

            # Connection 2: Valve to Tank
            cursor.execute("""
                INSERT INTO pipe VALUES (?, ?, ?, ?, ?)
            """, (
                f"PIPE-{pipe_number:03d}",
                facility_id,
                valve_id,
                tank_id,
                100.0
            ))
            pipe_number += 1

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM pipe")
    print("Total pipe segments:", cursor.fetchone()[0])

    conn.close()
    print("Pump -> Valve -> Tank topology created successfully!")


if __name__ == "__main__":
    generate_pipes()
