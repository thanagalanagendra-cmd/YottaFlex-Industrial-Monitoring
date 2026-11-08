
import sqlite3
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DB_PATH = BASE_DIR / "database" / "yottaflex.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS facility (
        facility_id TEXT PRIMARY KEY,
        facility_name TEXT NOT NULL,
        location TEXT,
        status TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pump (
        pump_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        pump_name TEXT NOT NULL,
        nominal_flow REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS tank (
        tank_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        tank_name TEXT NOT NULL,
        capacity REAL NOT NULL,
        current_level REAL NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS valve (
        valve_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        valve_name TEXT NOT NULL,
        valve_state TEXT NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS pipe (
        pipe_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        source_node_id TEXT NOT NULL,
        target_node_id TEXT NOT NULL,
        diameter REAL NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS sensor (
        sensor_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        equipment_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        unit TEXT NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS operating_mode (
        mode_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        mode_name TEXT NOT NULL,
        effective_from TEXT NOT NULL,
        effective_to TEXT,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS telemetry (
        telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        reading_value REAL NOT NULL,
        reading_time TEXT NOT NULL,
        FOREIGN KEY (sensor_id) REFERENCES sensor(sensor_id)
    );

    CREATE TABLE IF NOT EXISTS alarm (
        alarm_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        issue_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        ground_truth INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
    );

    CREATE TABLE IF NOT EXISTS simulation_run (
        simulation_id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        mode_id TEXT,
        configuration TEXT NOT NULL,
        run_status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (facility_id) REFERENCES facility(facility_id),
        FOREIGN KEY (mode_id) REFERENCES operating_mode(mode_id)
    );
    """)

    conn.commit()
    conn.close()

    print("Database and 10 tables created successfully!")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    create_tables()
