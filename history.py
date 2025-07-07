import sqlite3
from datetime import datetime, timedelta

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def is_stale(conn, stale_days):
    c = conn.cursor()
    c.execute("SELECT MAX(timestamp) FROM history")
    row = c.fetchone()
    if row and row[0]:
        last_ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_ts > timedelta(days=stale_days):
            return True
        return False
    return True  # if no history yet
