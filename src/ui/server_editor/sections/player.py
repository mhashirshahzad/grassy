from gi.repository import Adw, Gtk


class PlayerSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Player Settings")
        rows = []
        
        # Idle Timeout
        idle_adj = Gtk.Adjustment(
            value=int(properties_data.get("player-idle-timeout", "0")),
            lower=0, upper=60, step_increment=1, page_increment=5
        )
        idle = Adw.SpinRow()
        idle.set_title("Idle Timeout (minutes)")
        idle.set_subtitle("0 = no timeout")
        idle.set_adjustment(idle_adj)
        idle_adj.connect("value-changed", self.window.on_adjustment_changed, "player-idle-timeout")
        group.add(idle)
        self.window.add_row(rows, idle, "idle timeout", "", "player-idle-timeout")
        
        # Hide Online Players
        hide_players = Adw.SwitchRow(title="Hide Online Players")
        hide_players.set_subtitle("Hide player count in server list")
        hide_players.set_active(properties_data["hide-online-players"] == "true")
        hide_players.connect("notify::active", self.window.on_switch_changed, "hide-online-players")
        group.add(hide_players)
        self.window.add_row(rows, hide_players, "hide online players", "", "hide-online-players")
        
        # Log IPs
        log_ips = Adw.SwitchRow(title="Log Player IPs")
        log_ips.set_active(properties_data["log-ips"] == "true")
        log_ips.connect("notify::active", self.window.on_switch_changed, "log-ips")
        group.add(log_ips)
        self.window.add_row(rows, log_ips, "log ips", "", "log-ips")
        
        # Pause When Empty
        pause_adj = Gtk.Adjustment(
            value=int(properties_data.get("pause-when-empty-seconds", "60")),
            lower=0, upper=3600, step_increment=10, page_increment=60
        )
        pause = Adw.SpinRow()
        pause.set_title("Pause When Empty (seconds)")
        pause.set_subtitle("0 = never pause")
        pause.set_adjustment(pause_adj)
        pause_adj.connect("value-changed", self.window.on_adjustment_changed, "pause-when-empty-seconds")
        group.add(pause)
        self.window.add_row(rows, pause, "pause when empty", "", "pause-when-empty-seconds")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
