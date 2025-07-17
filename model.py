import sqlite3
import datetime

DB_NAME = "vault.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                tags TEXT,
                sentiment TEXT,
                timestamp TEXT
            );
        """)

def insert_note(content, tags, sentiment):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO notes (content, tags, sentiment, timestamp) VALUES (?, ?, ?, ?);",
            (content, tags, sentiment, datetime.datetime.now().isoformat())
        )

def get_recent_notes(limit=10):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT * FROM notes ORDER BY id DESC LIMIT ?;",
            (limit,)
        )
        return cursor.fetchall()

