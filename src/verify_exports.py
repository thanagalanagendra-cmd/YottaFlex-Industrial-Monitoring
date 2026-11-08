import csv
from pathlib import Path

folder = Path("exports/csv")

for file in sorted(folder.glob("*.csv")):
    with open(file, "r", encoding="utf-8", newline="") as f:
        count = sum(1 for row in csv.DictReader(f))

    print(f"{file.name}: {count} records")