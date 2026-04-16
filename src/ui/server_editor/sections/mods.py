from gi.repository import Adw, Gtk
import subprocess
import os


class ModsSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        self.mods_folder = self.window.server_folder / "mods"
        
        # Only show if mods folder exists
        if not self.mods_folder.exists() or not self.mods_folder.is_dir():
            return
        
        group = Adw.PreferencesGroup(title="Mods Management")
        rows = []
        
        row = Adw.ActionRow(title="Open Mods Folder")
        row.set_subtitle("Manage your installed mods")
        
        # Count mods if any
        mod_count = len(list(self.mods_folder.glob("*.jar")))
        if mod_count > 0:
            row.set_subtitle(f"{mod_count} mod(s) installed - Click to open folder")
        else:
            row.set_subtitle("No mods installed - Click to open folder")
        
        btn = Gtk.Button(label="Open Folder")
        btn.add_css_class("suggested-action")
        btn.connect("clicked", self.on_open_mods_clicked)
        
        row.add_suffix(btn)
        group.add(row)
        
        preferences_page.add(group)
        self.window.add_row(rows, row, "open mods folder", "mods management", "mods")
        self.window.register_group(group, rows)
    
    def on_open_mods_clicked(self, button):
        """Open the mods folder in the system file manager"""
        try:
            mods_path = str(self.mods_folder)
            
            # Cross-platform folder opening
            if os.name == 'nt':  # Windows
                os.startfile(mods_path)
            elif hasattr(os, 'uname') and os.uname().sysname == 'Darwin':  # macOS
                subprocess.run(['open', mods_path])
            else:  # Linux
                subprocess.run(['xdg-open', mods_path])
                
        except Exception as e:
            # Show error dialog if cannot open
            error_dialog = Adw.MessageDialog.new(
                self.window,
                "Error",
                f"Failed to open mods folder: {str(e)}"
            )
            error_dialog.add_response("ok", "OK")
            error_dialog.set_default_response("ok")
            error_dialog.present()
