# mindvault_tui.py — Final Working Version

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Vertical
from textual.reactive import reactive
from rich.text import Text
import sqlite3
from datetime import datetime
from textblob import TextBlob
import os

DB_PATH = os.path.expanduser("~/.mindvault/mindvault.db")

# --- DB Functions ---
def get_recent_notes(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, sentiment, timestamp FROM notes ORDER BY timestamp DESC LIMIT ?", (limit,))
    notes = c.fetchall()
    conn.close()
    return notes

def search_notes(keyword):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, sentiment, timestamp FROM notes WHERE content LIKE ? ORDER BY timestamp DESC", (f"%{keyword}%",))
    notes = c.fetchall()
    conn.close()
    return notes

def insert_note(content):
    sentiment = analyze_sentiment(content)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (content, sentiment, timestamp) VALUES (?, ?, ?)", (content, sentiment, timestamp))
    conn.commit()
    conn.close()

def analyze_sentiment(note):
    polarity = TextBlob(note).sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

ASCII_BANNER = """
╔════════════════════════════════════╗
║     🧠  M I N D V A U L T   +      ║
║   "Second Brain, Terminal-Powered" ║
╚════════════════════════════════════╝
"""

# --- TUI App ---
class Banner(Static):
    def on_mount(self):
        self.update(ASCII_BANNER)

class MindVaultApp(App):
    CSS_PATH = "mindvault.css"
    BINDINGS = [
        ("n", "new_note", "New Note"),
        ("/", "search_note", "Search"),
        ("r", "reload_notes", "Reload"),
        ("q", "quit", "Quit"),
    ]

    mode = reactive("browse")  # 'browse', 'add', 'search'
    search_query = reactive("")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Banner()
        with Vertical():
            self.note_display = Static(id="note-list")
            yield self.note_display
            self.note_input = Input(placeholder="Enter your note or search...", id="note-input")
            self.note_input.visible = False
            yield self.note_input
        yield Footer()

    def on_mount(self):
        self.refresh_notes()

    def refresh_notes(self, notes=None):
        notes = notes or get_recent_notes()
        output = Text()
        for content, sentiment, timestamp in notes:
            sentiment_color = {
                "positive": "green",
                "neutral": "yellow",
                "negative": "red"
            }.get(sentiment, "white")
            output.append(f"[{timestamp[:16]}] ", style="bold blue")
            output.append(content + "\n", style="white")
            output.append(f" → Mood: {sentiment}\n\n", style=sentiment_color)
        self.note_display.update(output)

    def action_new_note(self):
        self.mode = "add"
        self.note_input.placeholder = "Type your new note and press Enter..."
        self.note_input.visible = True
        self.set_focus(self.note_input)

    def action_search_note(self):
        self.mode = "search"
        self.note_input.placeholder = "Search notes by keyword..."
        self.note_input.visible = True
        self.set_focus(self.note_input)

    def action_reload_notes(self):
        self.refresh_notes()

    async def on_input_submitted(self, message: Input.Submitted):
        text = message.value.strip()
        self.note_input.visible = False
        self.note_input.value = ""

        if self.mode == "add" and text:
            insert_note(text)
            self.refresh_notes()
        elif self.mode == "search" and text:
            results = search_notes(text)
            self.refresh_notes(results)
        else:
            self.refresh_notes()

        self.set_focus(None)
        self.mode = "browse"

if __name__ == "__main__":
    MindVaultApp().run()
