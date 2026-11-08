
import random
from src.database import get_connection

# Fixed seed ensures repeatable data
random.seed(20261022)


def generate_master_data():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Create 3 facilities
    facilities = [
        ("FAC-001", "Central Water Plant", "Hyderabad", "ACTIVE"),
        ("FAC-002", "North Water Plant", "Vijayawada", "ACTIVE"),
        ("FAC-003", "South Water Plant", "Rajahmundry", "ACTIVE")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO facility
        (facility_id, facility_name, location, status)
        VALUES (?, ?, ?, ?)
    """, facilities)

    # 2. Create 20 pumps
    for i in range(1, 21):
        facility_id = f"FAC-{((i - 1) % 3) + 1:03d}"

        cursor.execute("""
            INSERT OR IGNORE INTO pump
            (pump_id, facility_id, pump_name, nominal_flow, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            f"PUMP-{i:03d}",
            facility_id,
            f"Pump {i}",
            round(random.uniform(50, 150), 2),
            "ACTIVE"
        ))

    # 3. Create 30 tanks
    for i in range(1, 31):
        facility_id = f"FAC-{((i - 1) % 3) + 1:03d}"
        capacity = round(random.uniform(500, 2000), 2)
        current_level = round(random.uniform(0.3, 0.8) * capacity, 2)

        cursor.execute("""
            INSERT OR IGNORE INTO tank
            (tank_id, facility_id, tank_name, capacity, current_level)
            VALUES (?, ?, ?, ?, ?)
        """, (
            f"TANK-{i:03d}",
            facility_id,
            f"Tank {i}",
            capacity,
            current_level
        ))

    # 4. Create 60 valves
    for i in range(1, 61):
        facility_id = f"FAC-{((i - 1) % 3) + 1:03d}"

        cursor.execute("""
            INSERT OR IGNORE INTO valve
            (valve_id, facility_id, valve_name, valve_state)
            VALUES (?, ?, ?, ?)
        """, (
            f"VALVE-{i:03d}",
            facility_id,
            f"Valve {i}",
            random.choice(["OPEN", "CLOSED"])
        ))

    conn.commit()

    # Verify inserted records
    for table in ["facility", "pump", "tank", "valve"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table.capitalize()} records: {cursor.fetchone()[0]}")

    conn.close()
    print("\nMaster data generated successfully!")


if __name__ == "__main__":
    generate_master_data()
