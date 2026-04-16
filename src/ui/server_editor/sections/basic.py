from gi.repository import Adw, Gtk


class BasicSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Basic Settings")
        rows = []
        
        # MOTD
        motd = Adw.EntryRow(title="Server Name (MOTD)")
        motd.set_text(properties_data["motd"])
        motd.connect("changed", self.window.on_entry_changed, "motd")
        group.add(motd)
        self.window.add_row(rows, motd, "motd server name", "", "motd")
        
        # Server Port
        port = Adw.EntryRow(title="Server Port")
        port.set_text(properties_data["server-port"])
        port.connect("changed", self.window.on_entry_changed, "server-port")
        group.add(port)
        self.window.add_row(rows, port, "server port", "", "server-port")
        
        # Server IP
        server_ip_row = Adw.ActionRow(title="Server IP (Bind Address)")
        server_ip_entry = Gtk.Entry()
        server_ip_entry.set_text(properties_data["server-ip"])
        server_ip_entry.connect("changed", self.window.on_entry_changed, "server-ip")
        server_ip_row.add_suffix(server_ip_entry)
        server_ip_row.set_subtitle("Leave empty to bind to all interfaces")
        group.add(server_ip_row)
        self.window.add_row(rows, server_ip_row, "server ip bind", "", "server-ip")
        
        # Max Players
        max_players_adj = Gtk.Adjustment(
            value=int(properties_data.get("max-players", "20")),
            lower=1, upper=100, step_increment=1, page_increment=10
        )
        max_players = Adw.SpinRow()
        max_players.set_title("Max Players")
        max_players.set_adjustment(max_players_adj)
        max_players_adj.connect("value-changed", self.window.on_adjustment_changed, "max-players")
        group.add(max_players)
        self.window.add_row(rows, max_players, "max players", "", "max-players")
        
        # Bug Report Link
        bug_report_row = Adw.ActionRow(title="Bug Report Link")
        bug_report_entry = Gtk.Entry()
        bug_report_entry.set_text(properties_data["bug-report-link"])
        bug_report_entry.connect("changed", self.window.on_entry_changed, "bug-report-link")
        bug_report_row.add_suffix(bug_report_entry)
        bug_report_row.set_subtitle("Custom URL for bug reports")
        group.add(bug_report_row)
        self.window.add_row(rows, bug_report_row, "bug report link", "", "bug-report-link")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
