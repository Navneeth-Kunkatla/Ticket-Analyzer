from utils.db import get_db_connection, DB_PATH

print(f"[DEBUG] Using DB_PATH: {DB_PATH}")

conn = get_db_connection()

TOOL_NAME = "Asset Panda"

rows = conn.execute("""
    SELECT tool_name, category, keyword FROM keywords
    WHERE tool_name = ?
""", (TOOL_NAME,)).fetchall()

print(f"[DEBUG] Found {len(rows)} rows for '{TOOL_NAME}':")
for row in rows:
    print(row)

conn.close()
