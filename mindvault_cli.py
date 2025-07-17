# mindvault_cli.py (Phase 1: Enhanced CLI Note System)

import argparse
import sqlite3
import os
from datetime import datetime
from textblob import TextBlob

DB_PATH = os.path.expanduser("~/.mindvault/mindvault.db")

# --- DB Setup ---
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            sentiment TEXT,
            tags TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Helpers ---
def analyze_sentiment(note):
    analysis = TextBlob(note)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def save_note(note):
    sentiment = analyze_sentiment(note)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (content, sentiment, timestamp) VALUES (?, ?, ?)", (note, sentiment, timestamp))
    conn.commit()
    conn.close()
    print("✅ Note saved successfully.")

def list_recent_notes(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, sentiment, timestamp FROM notes ORDER BY timestamp DESC LIMIT ?", (limit,))
    notes = c.fetchall()
    conn.close()
    print("\n--- Recent Notes ---")
    for note in notes:
        print(f"[{note[0]}] {note[1]} | {note[2]} | {note[3]}")

def search_notes(keyword):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, timestamp FROM notes WHERE content LIKE ? ORDER BY timestamp DESC", (f"%{keyword}%",))
    results = c.fetchall()
    conn.close()
    print("\n--- Search Results ---")
    for r in results:
        print(f"[{r[0]}] {r[1]} | {r[2]}")

# --- CLI Setup ---
parser = argparse.ArgumentParser(description="MindVault+ — Second brain for the terminal-native Linux user")
parser.add_argument("-N", "--note", help="Add a new note directly")
parser.add_argument("--history", action="store_true", help="Show recent notes")
parser.add_argument("--search", help="Search notes by keyword")
args = parser.parse_args()

init_db()

if args.note:
    save_note(args.note)
elif args.history:
    list_recent_notes()
elif args.search:
    search_notes(args.search)
else:
    parser.print_help()
