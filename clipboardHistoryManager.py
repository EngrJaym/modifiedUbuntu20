import pyperclip
import tkinter as tk
from tkinter import messagebox
import time
import threading

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard History Manager")
        self.clipboard_history = []
        self.is_running = True

        # Create GUI elements
        self.create_widgets()
        
        # Start monitoring clipboard
        self.update_clipboard()

    def create_widgets(self):
        # Label for clipboard history
        self.history_label = tk.Label(self.root, text="My Clipboard History", font=("Arial", 14))
        self.history_label.pack(pady=10)

         # Listbox to display clipboard history
        self.history_listbox = tk.Listbox(self.root, width=50, height=10)
        self.history_listbox.pack(pady=10)

        # Button to paste selected text back to clipboard
        self.paste_button = tk.Button(self.root, text="Copy Text", command=self.paste_selected)
        self.paste_button.pack(pady=5)

        # Button to clear clipboard history
        self.clear_button = tk.Button(self.root, text="Clear History", command=self.clear_history)
        self.clear_button.pack(pady=5)

        # Button to quit the app
        self.quit_button = tk.Button(self.root, text="Quit", command=self.stop)
        self.quit_button.pack(pady=5)

    def update_clipboard(self):
        """Monitor the clipboard and add new entries to the history."""
        def monitor():
            while self.is_running:
                current_clipboard = pyperclip.paste()

                # If the clipboard content is new, add it to the history
                if current_clipboard and (not self.clipboard_history or current_clipboard != self.clipboard_history[-1]):
                    self.clipboard_history.append(current_clipboard)
                    self.history_listbox.insert(tk.END, current_clipboard)

                time.sleep(1)  # Check every second

        # Start clipboard monitoring in a background thread
        threading.Thread(target=monitor, daemon=True).start()
    def paste_selected(self):
            """Copy selected history item back to clipboard."""
            try:
                selected_index = self.history_listbox.curselection()
                if selected_index:
                    selected_text = self.history_listbox.get(selected_index)
                    pyperclip.copy(selected_text)
                    messagebox.showinfo("Success", "Copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {e}")

    def clear_history(self):
        """Clear the clipboard history."""
        self.clipboard_history.clear()
        self.history_listbox.delete(0, tk.END)

    def stop(self):
        """Stop the application."""
        self.is_running = False
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    clipboard_manager = ClipboardManager(root)
    root.mainloop()
