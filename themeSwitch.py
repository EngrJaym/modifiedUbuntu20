import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
import os

THEME_FILE = os.path.expanduser("~/.theme_switcher_config")  # File to store the selected theme

class ThemeSwitcher(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Theme Switcher")
        self.set_border_width(10)

        # Dropdown for theme selection
        self.theme_label = Gtk.Label(label="Select Theme:")
        self.theme_dropdown = Gtk.ComboBoxText()
        self.theme_dropdown.append_text("Adwaita")  # Default light theme
        self.theme_dropdown.append_text("Adwaita-dark")  # Default dark theme
        self.theme_dropdown.append_text("Yaru")  # Example custom theme
        self.theme_dropdown.append_text("Yaru-dark")  # Example custom theme (dark)
        self.theme_dropdown.connect("changed", self.on_theme_changed)

        # Create a box to arrange widgets
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box.pack_start(self.theme_label, False, False, 0)
        self.box.pack_start(self.theme_dropdown, False, False, 0)

        self.add(self.box)

        # Set the initial dropdown selection
        self.set_initial_theme()

    def set_initial_theme(self):
        """Set the dropdown to the previously saved or currently active theme."""
        # Check if a saved theme exists
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, "r") as file:
                saved_theme = file.read().strip()
        else:
            # Fall back to the current system theme
            saved_theme = subprocess.check_output(
                "gsettings get org.gnome.desktop.interface gtk-theme", shell=True
            ).decode("utf-8").strip().strip("'")

        # Set the dropdown selection
        if saved_theme in ["Adwaita", "Adwaita-dark", "Yaru", "Yaru-dark"]:
            self.theme_dropdown.set_active(["Adwaita", "Adwaita-dark", "Yaru", "Yaru-dark"].index(saved_theme))
        else:
            self.theme_dropdown.set_active(-1)  # Unknown theme

        # Apply the saved theme
        self.apply_theme(saved_theme)

    def on_theme_changed(self, dropdown):
        """Change the system theme based on the selection."""
        selected_theme = dropdown.get_active_text()
        if selected_theme:
            self.apply_theme(selected_theme)
            # Save the selected theme to a file
            with open(THEME_FILE, "w") as file:
                file.write(selected_theme)

    def apply_theme(self, theme):
        """Apply the selected theme to the system."""
        subprocess.run([
            "gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme
        ])

def main():
    window = ThemeSwitcher()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
