import pyperclip
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import threading

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard History Manager")
        self.root.geometry("400x350")  # Set a default window size
        self.clipboard_history = []
        self.is_running = True

        # Create GUI elements
        self.create_widgets()

        # Start monitoring clipboard
        self.update_clipboard()

    def create_widgets(self):
        # Frame for history and buttons for better layout control
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Label for clipboard history
        self.history_label = tk.Label(frame, text="My Clipboard History", font=("Arial", 14, 'bold'))
        self.history_label.pack(pady=5)

        # Listbox to display clipboard history with scrollbar
        self.history_listbox = tk.Listbox(frame, width=50, height=10, selectmode=tk.SINGLE, font=("Arial", 10))
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)

        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons frame for better layout
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, fill=tk.X)

        # Button to paste selected text back to clipboard
        self.paste_button = tk.Button(button_frame, text="Copy text", command=self.paste_selected, width=20, bg="lightgreen")
        self.paste_button.pack(side=tk.LEFT, padx=5)

        # Button to clear clipboard history
        self.clear_button = tk.Button(button_frame, text="Clear History", command=self.clear_history, width=20, bg="lightcoral")
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Button to quit the app
        self.quit_button = tk.Button(button_frame, text="Quit", command=self.stop, width=20, bg="lightgray")
        self.quit_button.pack(side=tk.LEFT, padx=5)

        # Status label for feedback on actions
        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 10, 'italic'), fg="gray")
        self.status_label.pack(pady=5)

    def update_clipboard(self):
        """Monitor the clipboard and add new entries to the history."""
        def monitor():
            while self.is_running:
                current_clipboard = pyperclip.paste()

                # If the clipboard content is new, add it to the history
                if current_clipboard and (not self.clipboard_history or current_clipboard != self.clipboard_history[-1]):
                    self.clipboard_history.append(current_clipboard)
                    self.history_listbox.insert(tk.END, current_clipboard)

                time.sleep(1)  # Check every second (this can be made more efficient)

        # Start clipboard monitoring in a background thread
        threading.Thread(target=monitor, daemon=True).start()

    def paste_selected(self):
        """Copy selected history item back to clipboard."""
        try:
            selected_index = self.history_listbox.curselection()
            if selected_index:
                selected_text = self.history_listbox.get(selected_index)
                pyperclip.copy(selected_text)
                self.status_label.config(text="Copied to clipboard!", fg="green")
                messagebox.showinfo("Success", "Copied to clipboard!")
            else:
                self.status_label.config(text="No item selected!", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")

    def clear_history(self):
        """Clear the clipboard history."""
        self.clipboard_history.clear()
        self.history_listbox.delete(0, tk.END)
        self.status_label.config(text="History cleared.", fg="blue")

    def stop(self):
        """Stop the application."""
        self.is_running = False
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    clipboard_manager = ClipboardManager(root)
    root.mainloop()
