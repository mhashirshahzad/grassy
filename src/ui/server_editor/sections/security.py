from gi.repository import Adw, Gtk


class SecuritySection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Security Settings")
        rows = []
        
        # White List
        wl = Adw.SwitchRow(title="White List")
        wl.set_subtitle("Only whitelisted players can join")
        wl.set_active(properties_data["white-list"] == "true")
        wl.connect("notify::active", self.window.on_switch_changed, "white-list")
        group.add(wl)
        self.window.add_row(rows, wl, "whitelist", "", "white-list")
        
        # Enforce Whitelist
        enforce_wl = Adw.SwitchRow(title="Enforce Whitelist")
        enforce_wl.set_subtitle("Kick non-whitelisted players in game")
        enforce_wl.set_active(properties_data["enforce-whitelist"] == "true")
        enforce_wl.connect("notify::active", self.window.on_switch_changed, "enforce-whitelist")
        group.add(enforce_wl)
        self.window.add_row(rows, enforce_wl, "enforce whitelist", "", "enforce-whitelist")
        
        # OP Permission Level
        op_level = Adw.ComboRow(title="OP Permission Level")
        levels = ["1 - Bypass spawn protection", "2 - Use command blocks", 
                  "3 - Use /ban, /op", "4 - Use /stop"]
        model = Gtk.StringList()
        for lvl in levels:
            model.append(lvl)
        op_level.set_model(model)
        current_op = int(properties_data.get("op-permission-level", "4"))
        op_level.set_selected(min(current_op - 1, 3))
        op_level.connect("notify::selected", self.window.on_op_level_changed)
        group.add(op_level)
        self.window.add_row(rows, op_level, "op permission level", "", "op-permission-level")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
