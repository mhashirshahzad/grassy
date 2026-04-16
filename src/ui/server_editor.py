from gi.repository import Adw, Gtk
from pathlib import Path
from ui.java_editor import JavaEditorWindow
from datetime import datetime


class ServerEditorWindow(Adw.Window):
    def __init__(self, parent, server_folder, **kwargs):
        super().__init__(**kwargs)

        self.server_folder = server_folder
        self.properties_file = server_folder / "server.properties"
        self.properties_data = {}

        self.set_title(f"Server Properties - {server_folder.name}")
        self.set_default_size(800, 600)
        self.set_transient_for(parent)
        self.set_modal(True)

        self.groups = []

        self.content = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Edit Server Properties"))

        # Search (top left)
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search settings...")
        self.search_entry.set_width_chars(20)
        self.search_entry.connect("search-changed", self.on_search_changed)
        header.pack_start(self.search_entry)

        # Save (top right)
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.save_properties)
        header.pack_end(save_button)

        self.content.add_top_bar(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self.preferences_page = Adw.PreferencesPage()

        self.load_properties()

        self.create_java_button()
        self.create_basic_settings()
        self.create_gameplay_settings()
        self.create_network_settings()
        self.create_performance_settings()
        self.create_security_settings()
        self.create_advanced_settings()

        scrolled.set_child(self.preferences_page)
        self.content.set_content(scrolled)
        self.set_content(self.content)

    # ----------------------------
    # SEARCH
    # ----------------------------
    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()

        for group, rows in self.groups:
            visible_any = False

            for row, blob in rows:
                match = (query == "") or (query in blob.lower())
                row.set_visible(match)
                visible_any = visible_any or match

            group.set_visible(visible_any or query == "")

    def register_group(self, group, rows):
        self.groups.append((group, rows))

    def add_row(self, rows, widget, title, subtitle="", key=""):
        blob = f"{title} {subtitle} {key}"
        rows.append((widget, blob))

    # ----------------------------
    # LOAD
    # ----------------------------
    def load_properties(self):
        self.properties_data = {}

        if self.properties_file.exists():
            with open(self.properties_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        self.properties_data[k] = v

        defaults = {
            "difficulty": "hard",
            "gamemode": "survival",
            "max-players": "20",
            "motd": "A Minecraft Server",
            "server-port": "25565",
            "online-mode": "false",
            "white-list": "false",
            "view-distance": "10",
            "player-idle-timeout": "0",
        }

        for k, v in defaults.items():
            self.properties_data.setdefault(k, v)

    # ----------------------------
    # JAVA
    # ----------------------------
    def create_java_button(self):
        group = Adw.PreferencesGroup(title="Java Settings")
        rows = []

        row = Adw.ActionRow(title="Configure Java")
        row.set_subtitle("Memory allocation and Java path")

        btn = Gtk.Button(label="Configure...")
        btn.add_css_class("suggested-action")
        btn.connect("clicked", self.on_java_settings_clicked)

        row.add_suffix(btn)
        group.add(row)

        self.preferences_page.add(group)

        self.add_row(rows, row, "java configure", "memory path", "java")
        self.register_group(group, rows)

    def on_java_settings_clicked(self, button):
        JavaEditorWindow(parent=self, server_folder=self.server_folder).present()

    # ----------------------------
    # BASIC
    # ----------------------------
    def create_basic_settings(self):
        group = Adw.PreferencesGroup(title="Basic Settings")
        rows = []

        motd = Adw.EntryRow(title="Server Name (MOTD)")
        motd.set_text(self.properties_data["motd"])
        motd.connect("changed", self.on_entry_changed, "motd")
        group.add(motd)
        self.add_row(rows, motd, "motd server name", "", "motd")

        port = Adw.EntryRow(title="Server Port")
        port.set_text(self.properties_data["server-port"])
        port.connect("changed", self.on_entry_changed, "server-port")
        group.add(port)
        self.add_row(rows, port, "server port", "", "server-port")

        self.preferences_page.add(group)
        self.register_group(group, rows)

    # ----------------------------
    # GAMEPLAY
    # ----------------------------
    def create_gameplay_settings(self):
        group = Adw.PreferencesGroup(title="Gameplay Settings")
        rows = []

        difficulty = Adw.ComboRow(title="Difficulty")
        model = Gtk.StringList()
        for d in ["peaceful", "easy", "normal", "hard"]:
            model.append(d)

        difficulty.set_model(model)
        difficulty.set_selected(
            ["peaceful", "easy", "normal", "hard"].index(
                self.properties_data["difficulty"]
            )
        )
        difficulty.connect("notify::selected", self.on_difficulty_changed)
        group.add(difficulty)

        self.add_row(rows, difficulty, "difficulty gameplay", "", "difficulty")

        self.preferences_page.add(group)
        self.register_group(group, rows)

    # ----------------------------
    # NETWORK
    # ----------------------------
    def create_network_settings(self):
        group = Adw.PreferencesGroup(title="Network Settings")
        rows = []

        online = Adw.SwitchRow(title="Online Mode (Cracked)")
        online.set_active(self.properties_data["online-mode"] == "true")
        online.connect("notify::active", self.on_switch_changed, "online-mode")
        group.add(online)

        self.add_row(rows, online, "online mode cracked", "", "online-mode")

        self.preferences_page.add(group)
        self.register_group(group, rows)

    # ----------------------------
    # PERFORMANCE
    # ----------------------------
    def create_performance_settings(self):
        group = Adw.PreferencesGroup(title="Performance")
        rows = []

        # Create adjustment for view distance
        view_adj = Gtk.Adjustment(
            value=int(self.properties_data.get("view-distance", "10")),
            lower=3,
            upper=32,
            step_increment=1,
            page_increment=10
        )
        
        view = Adw.SpinRow()
        view.set_title("View Distance")
        view.set_adjustment(view_adj)
        view.set_range(3, 32)
        
        # Connect to adjustment's value-changed signal
        view_adj.connect("value-changed", self.on_adjustment_changed, "view-distance")
        
        group.add(view)
        self.add_row(rows, view, "view distance performance", "", "view-distance")
        self.preferences_page.add(group)
        self.register_group(group, rows)

    # ----------------------------
    # SECURITY
    # ----------------------------
    def create_security_settings(self):
        group = Adw.PreferencesGroup(title="Security")
        rows = []

        wl = Adw.SwitchRow(title="White List")
        wl.set_active(self.properties_data["white-list"] == "true")
        wl.connect("notify::active", self.on_switch_changed, "white-list")
        group.add(wl)

        self.add_row(rows, wl, "whitelist security", "", "white-list")

        self.preferences_page.add(group)
        self.register_group(group, rows)

    # ----------------------------
    # ADVANCED
    # ----------------------------
    def create_advanced_settings(self):
        group = Adw.PreferencesGroup(title="Advanced")
        rows = []

        # Create adjustment for idle timeout
        idle_adj = Gtk.Adjustment(
            value=int(self.properties_data.get("player-idle-timeout", "0")),
            lower=0,
            upper=60,
            step_increment=1,
            page_increment=5
        )
        
        idle = Adw.SpinRow()
        idle.set_title("Idle Timeout (minutes)")
        idle.set_adjustment(idle_adj)
        idle.set_range(0, 60)
        
        # Connect to adjustment's value-changed signal
        idle_adj.connect("value-changed", self.on_adjustment_changed, "player-idle-timeout")
        
        group.add(idle)
        self.add_row(rows, idle, "idle timeout advanced", "", "player-idle-timeout")
        self.preferences_page.add(group)
        self.register_group(group, rows)

    # ----------------------------
    # EVENTS
    # ----------------------------
    def on_entry_changed(self, entry, key):
        self.properties_data[key] = entry.get_text()

    def on_adjustment_changed(self, adjustment, key):
        """Handle SpinRow value changes via Gtk.Adjustment"""
        self.properties_data[key] = str(int(adjustment.get_value()))

    def on_switch_changed(self, switch, _pspec, key):
        self.properties_data[key] = "true" if switch.get_active() else "false"

    def on_difficulty_changed(self, combo, _pspec):
        self.properties_data["difficulty"] = [
            "peaceful",
            "easy",
            "normal",
            "hard",
        ][combo.get_selected()]

    # ----------------------------
    # SAVE
    # ----------------------------
    def save_properties(self, button):
        content = "# Minecraft server properties\n"
        content += f"# {datetime.now()}\n\n"

        for k, v in sorted(self.properties_data.items()):
            content += f"{k}={v}\n"

        with open(self.properties_file, "w") as f:
            f.write(content)

        self.close()
