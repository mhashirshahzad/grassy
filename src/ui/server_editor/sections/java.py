from gi.repository import Adw, Gtk


class JavaSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Java Settings")
        rows = []
        
        row = Adw.ActionRow(title="Configure Java")
        row.set_subtitle("Memory allocation and Java path")
        
        btn = Gtk.Button(label="Configure...")
        btn.add_css_class("suggested-action")
        btn.connect("clicked", self.on_java_settings_clicked)
        
        row.add_suffix(btn)
        group.add(row)
        
        preferences_page.add(group)
        self.window.add_row(rows, row, "java configure", "memory path", "java")
        self.window.register_group(group, rows)
    
    def on_java_settings_clicked(self, button):
        from ui.java_editor import JavaEditorWindow
        JavaEditorWindow(parent=self.window, server_folder=self.window.server_folder).present()
