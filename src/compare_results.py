
import sqlite3
from collections import Counter

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

# Expected anomaly counts
cursor.execute("""
    SELECT anomaly_type, COUNT(*)
    FROM ground_truth
    GROUP BY anomaly_type
""")

expected = Counter(dict(cursor.fetchall()))

# Actual detected alarm counts
cursor.execute("""
    SELECT issue_type, COUNT(*)
    FROM alarm
    GROUP BY issue_type
""")

detected = Counter(dict(cursor.fetchall()))

print("\nEXPECTED vs DETECTED ANOMALIES\n")

all_types = sorted(set(expected) | set(detected))

for anomaly in all_types:
    expected_count = expected[anomaly]
    detected_count = detected[anomaly]

    status = "PASS" if expected_count == detected_count else "CHECK"

    print(
        f"{anomaly}: Expected={expected_count}, "
        f"Detected={detected_count} - {status}"
    )

conn.close()
