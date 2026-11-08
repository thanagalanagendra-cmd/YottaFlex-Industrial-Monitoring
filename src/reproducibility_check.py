import hashlib
import json
from pathlib import Path

folder = Path("exports/csv")
manifest_path = Path("exports/checksum_manifest.json")

current_checksums = {}

for file in sorted(folder.glob("*.csv")):
    file_hash = hashlib.sha256(file.read_bytes()).hexdigest()
    current_checksums[file.name] = file_hash

if manifest_path.exists():
    previous_checksums = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    if previous_checksums == current_checksums:
        print("REPRODUCIBILITY CHECK: PASS")
        print("All CSV checksums match the previous run.")
    else:
        print("REPRODUCIBILITY CHECK: FAIL")
        print("Some CSV files have changed.")
        for name in current_checksums:
            if previous_checksums.get(name) != current_checksums[name]:
                print(f"Changed: {name}")
else:
    print("Baseline checksum manifest created.")
    print("Run this command again to compare checksums.")

manifest_path.write_text(
    json.dumps(current_checksums, indent=4),
    encoding="utf-8"
)

print(f"Files checked: {len(current_checksums)}")