
import sqlite3
import json
from pathlib import Path
import pandas as pd

DB_PATH = Path("database/yottaflex.db")
CSV_DIR = Path("exports/csv")
JSON_DIR = Path("exports/json")

CSV_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# Get all database tables
cursor = conn.cursor()
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type = 'table'
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""")

tables = [row[0] for row in cursor.fetchall()]

manifest = []

for table in tables:
    df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)

    # Export CSV
    csv_path = CSV_DIR / f"{table}.csv"
    df.to_csv(csv_path, index=False)

    # Export JSON
    json_path = JSON_DIR / f"{table}.json"
    df.to_json(
        json_path,
        orient="records",
        indent=4,
        force_ascii=False
    )

    manifest.append({
        "table": table,
        "row_count": len(df),
        "csv_file": str(csv_path),
        "json_file": str(json_path)
    })

    print(f"{table}: {len(df)} records exported")

conn.close()

# Save export manifest
manifest_path = Path("exports/source_manifest.json")
manifest_path.write_text(
    json.dumps(manifest, indent=4),
    encoding="utf-8"
)

print("\nAll database tables exported successfully!")
print("CSV folder:", CSV_DIR)
print("JSON folder:", JSON_DIR)
print("Manifest:", manifest_path)
