import sqlite3

conn = sqlite3.connect("database/yottaflex.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = cursor.fetchall()

print("\nDATABASE TABLES AND RECORD COUNTS\n")

for (table,) in tables:
    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cursor.fetchone()[0]
    print(f"{table}: {count} records")

conn.close()