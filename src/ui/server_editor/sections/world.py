from gi.repository import Adw, Gtk


class WorldSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="World Settings")
        rows = []
        
        # Level Name
        level_name = Adw.EntryRow(title="World Name")
        level_name.set_text(properties_data["level-name"])
        level_name.connect("changed", self.window.on_entry_changed, "level-name")
        group.add(level_name)
        self.window.add_row(rows, level_name, "world name level", "", "level-name")
        
        # Level Seed (using ActionRow with Entry for subtitle)
        level_seed_row = Adw.ActionRow(title="World Seed")
        level_seed_entry = Gtk.Entry()
        level_seed_entry.set_text(properties_data["level-seed"])
        level_seed_entry.connect("changed", self.window.on_entry_changed, "level-seed")
        level_seed_row.add_suffix(level_seed_entry)
        level_seed_row.set_subtitle("Leave empty for random seed")
        group.add(level_seed_row)
        self.window.add_row(rows, level_seed_row, "world seed", "", "level-seed")
        
        # Level Type
        level_type = Adw.ComboRow(title="World Type")
        level_types = ["minecraft:normal", "minecraft:flat", "minecraft:large_biomes", 
                       "minecraft:amplified", "minecraft:single_biome_surface"]
        model = Gtk.StringList()
        for lt in level_types:
            model.append(lt)
        level_type.set_model(model)
        current_type = properties_data["level-type"]
        if current_type in level_types:
            level_type.set_selected(level_types.index(current_type))
        else:
            level_type.set_selected(0)
        level_type.connect("notify::selected", self.window.on_combo_changed, "level-type", level_types)
        group.add(level_type)
        self.window.add_row(rows, level_type, "world type", "", "level-type")
        
        # Generator Settings
        gen_settings_row = Adw.ActionRow(title="Generator Settings")
        gen_settings_entry = Gtk.Entry()
        gen_settings_entry.set_text(properties_data["generator-settings"])
        gen_settings_entry.connect("changed", self.window.on_entry_changed, "generator-settings")
        gen_settings_row.add_suffix(gen_settings_entry)
        gen_settings_row.set_subtitle("JSON settings for custom world generation")
        group.add(gen_settings_row)
        self.window.add_row(rows, gen_settings_row, "generator settings", "", "generator-settings")
        
        # Generate Structures
        gen_structures = Adw.SwitchRow(title="Generate Structures")
        gen_structures.set_subtitle("Generate villages, temples, etc.")
        gen_structures.set_active(properties_data["generate-structures"] == "true")
        gen_structures.connect("notify::active", self.window.on_switch_changed, "generate-structures")
        group.add(gen_structures)
        self.window.add_row(rows, gen_structures, "generate structures", "", "generate-structures")
        
        # Hardcore Mode
        hardcore = Adw.SwitchRow(title="Hardcore Mode")
        hardcore.set_subtitle("Players are banned on death")
        hardcore.set_active(properties_data["hardcore"] == "true")
        hardcore.connect("notify::active", self.window.on_switch_changed, "hardcore")
        group.add(hardcore)
        self.window.add_row(rows, hardcore, "hardcore mode", "", "hardcore")
        
        # Max World Size
        max_world_adj = Gtk.Adjustment(
            value=int(properties_data.get("max-world-size", "29999984")),
            lower=1000, upper=29999984, step_increment=1000, page_increment=10000
        )
        max_world = Adw.SpinRow()
        max_world.set_title("Max World Size (blocks)")
        max_world.set_adjustment(max_world_adj)
        max_world_adj.connect("value-changed", self.window.on_adjustment_changed, "max-world-size")
        group.add(max_world)
        self.window.add_row(rows, max_world, "max world size", "", "max-world-size")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
