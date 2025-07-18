import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DB_PATH = os.path.abspath("C:/Users/navak/Desktop/Hex 2025/Ticket Analyzer/regex/keyword_store.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL,
            category TEXT NOT NULL,
            keyword TEXT NOT NULL,
            UNIQUE(tool_name, category, keyword)
        );
    """)
    return conn

def save_keywords(tool_name, category, keywords):
    conn = get_db_connection()
    with conn:
        for word in keywords:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO keywords (tool_name, category, keyword)
                    VALUES (?, ?, ?)
                """, (tool_name, category, word))
                # print(f"[DB] Inserted {len(keywords)} keywords into '{category}' for tool '{tool_name}'")

            except Exception as e:
                print(f"[DB] Insert failed for word: {word} - {e}")
 
    conn.close()
def load_keywords(tool_name):
    conn = get_db_connection()
    buckets = {
        "actions": [],
        "applications": [],
        "objects": [],
        "non_ito_objects": [],
        "non-ito_words": []
    }
    for category in buckets.keys():
        rows = conn.execute("""
            SELECT keyword FROM keywords
            WHERE tool_name = ? AND category = ?
        """, (tool_name, category)).fetchall()
        buckets[category] = [row[0] for row in rows]
    conn.close()
    return buckets
    '''
    print(f"[DB] Loaded buckets for {tool_name}:")
    for k, v in buckets.items():
        print(f"  {k}: {len(v)}")
    return buckets
    '''