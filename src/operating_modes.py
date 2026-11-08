
import sqlite3

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

modes = [
    ("MODE-001", "FAC-001", "NORMAL", "2026-10-22 00:00:00", None),
    ("MODE-002", "FAC-001", "MAINTENANCE", "2026-10-25 00:00:00", None),
    ("MODE-003", "FAC-002", "NORMAL", "2026-10-22 00:00:00", None),
    ("MODE-004", "FAC-002", "HIGH_DEMAND", "2026-10-27 00:00:00", None),
    ("MODE-005", "FAC-003", "NORMAL", "2026-10-22 00:00:00", None),
    ("MODE-006", "FAC-003", "LOW_DEMAND", "2026-10-29 00:00:00", None)
]

cursor.executemany("""
    INSERT OR IGNORE INTO operating_mode
    (mode_id, facility_id, mode_name, effective_from, effective_to)
    VALUES (?, ?, ?, ?, ?)
""", modes)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM operating_mode")
print("Operating modes created:", cursor.fetchone()[0])

conn.close()
