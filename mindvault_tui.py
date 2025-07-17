# mindvault_tui.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Log
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from analyzer import auto_tag, analyze_sentiment
from model import insert_note, get_recent_notes

ASCII_BANNER = """
╔════════════════════════════════════╗
║     🧠  M I N D V A U L T   +      ║
║   "Second Brain, Terminal-Powered" ║
╚════════════════════════════════════╝
"""

class Banner(Static):
    def on_mount(self):
        self.update(ASCII_BANNER)

class MindVaultApp(App):
    CSS_PATH = "mindvault.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Banner()
        with Vertical():
            self.note_log = Log(highlight=True)
            yield self.note_log
            self.note_input = Input(placeholder="Type your note and press Enter...", id="note-input")
            yield self.note_input
        yield Footer()

    def on_mount(self):
        self.load_notes()
        self.note_input.focus()

    def load_notes(self):
        self.note_log.clear()
        notes = get_recent_notes(limit=10)
        for note in notes:
            ts = note[4][:16]
            self.note_log.write(f"[{ts}] {note[1]}")
            self.note_log.write(f"Tags: {note[2]} | Mood: {note[3]}")
            self.note_log.write("")

    async def on_input_submitted(self, event: Input.Submitted):
        content = event.value.strip()
        if not content:
            return
        try:
            tags = auto_tag(content)
            sentiment = analyze_sentiment(content)
            insert_note(content, tags, sentiment)
            self.note_log.write(f"✅ Added: {content}")
            self.note_log.write(f"Tags: {tags} | Sentiment: {sentiment}\n")
            self.note_input.value = ""
            self.load_notes()
        except Exception as e:
            self.note_log.write(f"❌ Error: {e}")

if __name__ == "__main__":
    MindVaultApp().run()
