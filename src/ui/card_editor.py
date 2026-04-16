from gi.repository import Adw, Gtk

class ServerRenameWindow:
    """Dialog for renaming a server folder"""
    
    def __init__(self, parent, server_card):
        self.parent = parent
        self.server_card = server_card
        self.dialog = None
        self.entry = None
    
    def present(self):
        """Show the rename dialog"""
        # Create a dialog for renaming
        self.dialog = Adw.MessageDialog.new(self.parent, 
                                           "Rename Server", 
                                           "Enter the new name for your server:")
        
        # Create a box to hold the entry
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Create entry widget
        self.entry = Gtk.Entry()
        self.entry.set_text(self.server_card.server_name)
        self.entry.set_placeholder_text("Server name")
        self.entry.set_activates_default(True)  # Press Enter to confirm
        
        content_box.append(self.entry)
        
        # Add custom content to dialog
        self.dialog.set_extra_child(content_box)
        
        # Add responses
        self.dialog.add_response("cancel", "Cancel")
        self.dialog.add_response("rename", "Rename")
        self.dialog.set_response_appearance("rename", Adw.ResponseAppearance.SUGGESTED)
        self.dialog.set_default_response("rename")
        self.dialog.set_close_response("cancel")
        
        self.dialog.connect("response", self.on_response)
        self.dialog.present()
    
    def on_response(self, dialog, response):
        """Handle rename confirmation"""
        new_name = self.entry.get_text().strip()
        dialog.destroy()
        
        if response == "rename" and new_name and new_name != self.server_card.server_name:
            self.rename_server(new_name)
    
    def rename_server(self, new_name):
        """Perform the actual rename operation"""
        try:
            # Check if a folder with the new name already exists in the parent directory
            parent_dir = self.server_card.server_folder.parent
            new_folder_path = parent_dir / new_name
            
            if new_folder_path.exists():
                # Show error dialog if name already exists
                error_dialog = Adw.MessageDialog.new(self.parent,
                                                     "Rename Failed",
                                                     f"A server named '{new_name}' already exists.")
                error_dialog.add_response("ok", "OK")
                error_dialog.set_default_response("ok")
                error_dialog.present()
                return
            
            # Rename the folder
            self.server_card.server_folder.rename(new_folder_path)
            
            # Update the server_card's folder path
            self.server_card.server_folder = new_folder_path
            
            # Update server_name
            self.server_card.server_name = new_name
            
            # Update the label
            self.server_card.name_label.set_label(self.server_card.server_name)
            
            # Reload properties (in case any paths inside need updating)
            self.server_card.load_properties()
            self.server_card.motd_label.set_label(self.server_card.motd)
            
            # Notify parent to refresh server list if needed
            if self.server_card.on_server_changed:
                self.server_card.on_server_changed()
                
        except Exception as e:
            # Show error dialog if rename fails
            error_dialog = Adw.MessageDialog.new(self.parent,
                                                 "Rename Failed",
                                                 f"Failed to rename server: {str(e)}")
            error_dialog.add_response("ok", "OK")
            error_dialog.set_default_response("ok")
            error_dialog.present()
