from gi.repository import Adw, Gtk


class GameplaySection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Gameplay Settings")
        rows = []
        
        # Game Mode
        gamemode = Adw.ComboRow(title="Default Game Mode")
        gamemodes = ["survival", "creative", "adventure", "spectator"]
        model = Gtk.StringList()
        for gm in gamemodes:
            model.append(gm)
        gamemode.set_model(model)
        current_gm = properties_data["gamemode"]
        if current_gm in gamemodes:
            gamemode.set_selected(gamemodes.index(current_gm))
        else:
            gamemode.set_selected(0)
        gamemode.connect("notify::selected", self.window.on_gamemode_changed)
        group.add(gamemode)
        self.window.add_row(rows, gamemode, "gamemode", "", "gamemode")
        
        # Force Game Mode
        force_gm = Adw.SwitchRow(title="Force Game Mode")
        force_gm.set_subtitle("Force players to default game mode on join")
        force_gm.set_active(properties_data["force-gamemode"] == "true")
        force_gm.connect("notify::active", self.window.on_switch_changed, "force-gamemode")
        group.add(force_gm)
        self.window.add_row(rows, force_gm, "force gamemode", "", "force-gamemode")
        
        # Difficulty
        difficulty = Adw.ComboRow(title="Difficulty")
        difficulties = ["peaceful", "easy", "normal", "hard"]
        model = Gtk.StringList()
        for d in difficulties:
            model.append(d)
        difficulty.set_model(model)
        current_diff = properties_data["difficulty"]
        if current_diff in difficulties:
            difficulty.set_selected(difficulties.index(current_diff))
        else:
            difficulty.set_selected(1)
        difficulty.connect("notify::selected", self.window.on_difficulty_changed)
        group.add(difficulty)
        self.window.add_row(rows, difficulty, "difficulty", "", "difficulty")
        
        # Allow Flight
        allow_flight = Adw.SwitchRow(title="Allow Flight")
        allow_flight.set_subtitle("Allow players to fly without anti-cheat kicking")
        allow_flight.set_active(properties_data["allow-flight"] == "true")
        allow_flight.connect("notify::active", self.window.on_switch_changed, "allow-flight")
        group.add(allow_flight)
        self.window.add_row(rows, allow_flight, "allow flight", "", "allow-flight")
        
        # Spawn Protection
        spawn_protection_adj = Gtk.Adjustment(
            value=int(properties_data.get("spawn-protection", "16")),
            lower=0, upper=100, step_increment=1, page_increment=10
        )
        spawn_protection = Adw.SpinRow()
        spawn_protection.set_title("Spawn Protection (blocks)")
        spawn_protection.set_subtitle("0 = disable spawn protection")
        spawn_protection.set_adjustment(spawn_protection_adj)
        spawn_protection_adj.connect("value-changed", self.window.on_adjustment_changed, "spawn-protection")
        group.add(spawn_protection)
        self.window.add_row(rows, spawn_protection, "spawn protection", "", "spawn-protection")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
