from gi.repository import Adw, Gtk
from pathlib import Path

from .handlers import EventHandlers
from .sections import (
    JavaSection, ModsSection, BasicSection, WorldSection,
    GameplaySection, PlayerSection, NetworkSection,
    PerformanceSection, SecuritySection
)


class ServerEditorWindow(Adw.Window, EventHandlers):
    def __init__(self, parent, server_folder, **kwargs):
        super().__init__(**kwargs)
        
        self.server_folder = server_folder
        self.properties_file = server_folder / "server.properties"
        self.properties_data = {}
        self.groups = []
        
        self.set_title(f"Server Properties - {server_folder.name}")
        self.set_default_size(900, 700)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        self.setup_ui()
        self.load_properties()
        self.create_all_sections()
    
    def setup_ui(self):
        self.content = Adw.ToolbarView()
        
        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Edit Server Properties"))
        
        # Search
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search settings...")
        self.search_entry.set_width_chars(20)
        self.search_entry.connect("search-changed", self.on_search_changed)
        header.pack_start(self.search_entry)
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.save_properties)
        header.pack_end(save_button)
        
        self.content.add_top_bar(header)
        
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.preferences_page = Adw.PreferencesPage()
        scrolled.set_child(self.preferences_page)
        self.content.set_content(scrolled)
        self.set_content(self.content)
    
    def load_properties(self):
        self.properties_data = {}
        
        if self.properties_file.exists():
            with open(self.properties_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        self.properties_data[k] = v
        
        # Defaults
        defaults = {
            "accepts-transfers": "false", "allow-flight": "false",
            "broadcast-console-to-ops": "true", "broadcast-rcon-to-ops": "true",
            "bug-report-link": "", "difficulty": "easy",
            "enable-code-of-conduct": "false", "enable-jmx-monitoring": "false",
            "enable-query": "false", "enable-rcon": "false",
            "enable-status": "true", "enforce-secure-profile": "true",
            "enforce-whitelist": "false", "entity-broadcast-range-percentage": "100",
            "force-gamemode": "false", "function-permission-level": "2",
            "gamemode": "survival", "generate-structures": "true",
            "generator-settings": "{}", "hardcore": "false",
            "hide-online-players": "false", "initial-disabled-packs": "",
            "initial-enabled-packs": "vanilla", "level-name": "world",
            "level-seed": "", "level-type": "minecraft:normal",
            "log-ips": "true", "management-server-enabled": "false",
            "management-server-host": "localhost", "management-server-port": "25565",
            "management-server-secret": "", "management-server-tls-enabled": "true",
            "management-server-tls-keystore": "", "management-server-tls-keystore-password": "",
            "max-chained-neighbor-updates": "1000000", "max-players": "20",
            "max-tick-time": "60000", "max-world-size": "29999984",
            "motd": "A Minecraft Server", "network-compression-threshold": "256",
            "online-mode": "true", "op-permission-level": "4",
            "pause-when-empty-seconds": "60", "player-idle-timeout": "0",
            "prevent-proxy-connections": "false", "query.port": "25565",
            "rate-limit": "0", "rcon.password": "", "rcon.port": "25575",
            "region-file-compression": "deflate", "require-resource-pack": "false",
            "resource-pack": "", "resource-pack-id": "", "resource-pack-prompt": "",
            "resource-pack-sha1": "", "server-ip": "", "server-port": "25565",
            "simulation-distance": "10", "spawn-protection": "16",
            "status-heartbeat-interval": "0", "sync-chunk-writes": "true",
            "text-filtering-config": "", "text-filtering-version": "0",
            "use-native-transport": "true", "view-distance": "10", "white-list": "false",
        }
        
        for k, v in defaults.items():
            if k not in self.properties_data:
                self.properties_data[k] = v
    
    def create_all_sections(self):
        sections = [
            JavaSection, ModsSection, BasicSection, WorldSection,
            GameplaySection, PlayerSection, NetworkSection,
            PerformanceSection, SecuritySection
        ]
        
        for section_class in sections:
            section = section_class(self)
            section.create(self.preferences_page, self.groups, self.properties_data)
    
    def register_group(self, group, rows):
        self.groups.append((group, rows))
    
    def add_row(self, rows, widget, title, subtitle="", key=""):
        blob = f"{title} {subtitle} {key}"
        rows.append((widget, blob))
