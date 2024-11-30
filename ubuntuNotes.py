import gi
import os
import pickle

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import Gtk, AyatanaAppIndicator3

NOTES_FILE = "sticky_notes.pkl"  # File to store notes content

class StickyNotesApp:
    def __init__(self):
        self.indicator = AyatanaAppIndicator3.Indicator.new(
            "Sticky Notes",
            "text-x-generic",  # Icon name
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)

        # Create menu
        menu = Gtk.Menu()

        new_note_item = Gtk.MenuItem(label="Open Ubuntu Notes")
        new_note_item.connect("activate", self.create_new_note)
        menu.append(new_note_item)

        menu.show_all()
        self.indicator.set_menu(menu)

        self.notes = self.load_notes()

    def load_notes(self):
        """Load saved notes from the file."""
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "rb") as f:
                return pickle.load(f)
        return []

    def save_notes(self):
        """Save current notes to the file."""
        with open(NOTES_FILE, "wb") as f:
            pickle.dump(self.notes, f)

    def create_new_note(self, _):
        """Create a new sticky note window."""
        note_window = Gtk.Window(title="Sticky Note")
        note_window.set_default_size(200, 200)

        # Make the window movable
        note_window.set_resizable(True)

        # Add a text view for note content
        text_view = Gtk.TextView()
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.set_border_width(10)

        # If there are saved notes, load the last note into the text view
        if self.notes:
            text_buffer = text_view.get_buffer()
            text_buffer.set_text(self.notes[-1])  # Load the last saved note

        note_window.add(text_view)

        # Save the note's content when it's closed
        def on_window_close(_, __):
            text_buffer = text_view.get_buffer()
            start, end = text_buffer.get_bounds()
            note_content = text_buffer.get_text(start, end, True).strip()
            if note_content:
                self.notes.append(note_content)
                self.save_notes()  # Save to file
            note_window.destroy()

        note_window.connect("delete-event", on_window_close)

        note_window.show_all()


def main():
    app = StickyNotesApp()
    Gtk.main()

if __name__ == "__main__":
    main()
