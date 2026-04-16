from datetime import datetime


class EventHandlers:
    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()
        
        for group, rows in self.groups:
            visible_any = False
            for row, blob in rows:
                match = (query == "") or (query in blob.lower())
                row.set_visible(match)
                visible_any = visible_any or match
            group.set_visible(visible_any or query == "")
    
    def on_entry_changed(self, entry, key):
        self.properties_data[key] = entry.get_text()
    
    def on_adjustment_changed(self, adjustment, key):
        self.properties_data[key] = str(int(adjustment.get_value()))
    
    def on_switch_changed(self, switch, _pspec, key):
        self.properties_data[key] = "true" if switch.get_active() else "false"
    
    def on_combo_changed(self, combo, _pspec, key, values):
        self.properties_data[key] = values[combo.get_selected()]
    
    def on_difficulty_changed(self, combo, _pspec):
        difficulties = ["peaceful", "easy", "normal", "hard"]
        self.properties_data["difficulty"] = difficulties[combo.get_selected()]
    
    def on_gamemode_changed(self, combo, _pspec):
        gamemodes = ["survival", "creative", "adventure", "spectator"]
        self.properties_data["gamemode"] = gamemodes[combo.get_selected()]
    
    def on_op_level_changed(self, combo, _pspec):
        self.properties_data["op-permission-level"] = str(combo.get_selected() + 1)
    
    def save_properties(self, button):
        content = "# Minecraft server properties\n"
        content += f"# {datetime.now()}\n\n"
        
        for k, v in sorted(self.properties_data.items()):
            content += f"{k}={v}\n"
        
        with open(self.properties_file, "w") as f:
            f.write(content)
        
        self.close()
