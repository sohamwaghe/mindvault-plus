#!/usr/bin/env python3

import argparse
import sqlite3
import os
from datetime import datetime
from textblob import TextBlob

DB_DIR = os.path.expanduser("~/.mindvault")
DB_PATH = os.path.join(DB_DIR, "mindvault.db")

# Ensure DB exists
def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            sentiment TEXT,
            tags TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Save a new note
def save_note(content, tags=None):
    polarity = TextBlob(content).sentiment.polarity
    sentiment = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag_str = tags if tags else ""
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (content, sentiment, tags, timestamp) VALUES (?, ?, ?, ?)",
              (content, sentiment, tag_str, timestamp))
    conn.commit()
    conn.close()
    print(f"✅ Note saved! Sentiment: {sentiment} | Tags: {tag_str}")

# Search notes by keyword
def search_notes(keyword):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, sentiment, tags, timestamp FROM notes WHERE content LIKE ? ORDER BY timestamp DESC", (f"%{keyword}%",))
    rows = c.fetchall()
    conn.close()
    return rows

# Search by tag
def search_by_tag(tag):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, sentiment, tags, timestamp FROM notes WHERE tags LIKE ? ORDER BY timestamp DESC", (f"%{tag}%",))
    rows = c.fetchall()
    conn.close()
    return rows

# View all notes
def get_all_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, sentiment, tags, timestamp FROM notes ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# Print formatted notes
def print_notes(notes):
    if not notes:
        print("No notes found.")
        return
    for content, sentiment, tags, timestamp in notes:
        tag_display = f" [tags: {tags}]" if tags else ""
        print(f"[{timestamp}] ({sentiment}){tag_display}\n{content}\n")

# Main CLI handler
def main():
    parser = argparse.ArgumentParser(description="MindVault+ CLI")
    parser.add_argument("-N", "--note", help="Add a new note")
    parser.add_argument("-S", "--search", help="Search notes by keyword")
    parser.add_argument("-T", "--tags", help="Comma-separated tags for the new note")
    parser.add_argument("-H", "--history", action="store_true", help="Show all saved notes")
    parser.add_argument("--tag", help="View notes by tag")

    args = parser.parse_args()
    init_db()

    if args.note:
        save_note(args.note, tags=args.tags)
    elif args.search:
        results = search_notes(args.search)
        print_notes(results)
    elif args.history:
        print_notes(get_all_notes())
    elif args.tag:
        print_notes(search_by_tag(args.tag))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
