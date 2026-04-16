from gi.repository import Adw, Gtk


class PerformanceSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Performance Settings")
        rows = []
        
        # View Distance
        view_adj = Gtk.Adjustment(
            value=int(properties_data.get("view-distance", "10")),
            lower=3, upper=32, step_increment=1, page_increment=5
        )
        view = Adw.SpinRow()
        view.set_title("View Distance (chunks)")
        view.set_adjustment(view_adj)
        view_adj.connect("value-changed", self.window.on_adjustment_changed, "view-distance")
        group.add(view)
        self.window.add_row(rows, view, "view distance", "", "view-distance")
        
        # Simulation Distance
        sim_adj = Gtk.Adjustment(
            value=int(properties_data.get("simulation-distance", "10")),
            lower=3, upper=32, step_increment=1, page_increment=5
        )
        simulation = Adw.SpinRow()
        simulation.set_title("Simulation Distance (chunks)")
        simulation.set_adjustment(sim_adj)
        sim_adj.connect("value-changed", self.window.on_adjustment_changed, "simulation-distance")
        group.add(simulation)
        self.window.add_row(rows, simulation, "simulation distance", "", "simulation-distance")
        
        # Entity Broadcast Range
        entity_range_adj = Gtk.Adjustment(
            value=int(properties_data.get("entity-broadcast-range-percentage", "100")),
            lower=10, upper=1000, step_increment=10, page_increment=50
        )
        entity_range = Adw.SpinRow()
        entity_range.set_title("Entity Broadcast Range (%)")
        entity_range.set_adjustment(entity_range_adj)
        entity_range_adj.connect("value-changed", self.window.on_adjustment_changed, "entity-broadcast-range-percentage")
        group.add(entity_range)
        self.window.add_row(rows, entity_range, "entity broadcast range", "", "entity-broadcast-range-percentage")
        
        # Max Tick Time
        tick_time_adj = Gtk.Adjustment(
            value=int(properties_data.get("max-tick-time", "60000")),
            lower=0, upper=300000, step_increment=5000, page_increment=10000
        )
        tick_time = Adw.SpinRow()
        tick_time.set_title("Max Tick Time (ms)")
        tick_time.set_adjustment(tick_time_adj)
        tick_time_adj.connect("value-changed", self.window.on_adjustment_changed, "max-tick-time")
        group.add(tick_time)
        self.window.add_row(rows, tick_time, "max tick time", "", "max-tick-time")
        
        # Max Chained Neighbor Updates
        chain_adj = Gtk.Adjustment(
            value=int(properties_data.get("max-chained-neighbor-updates", "1000000")),
            lower=1000, upper=10000000, step_increment=10000, page_increment=100000
        )
        chain = Adw.SpinRow()
        chain.set_title("Max Chained Neighbor Updates")
        chain.set_adjustment(chain_adj)
        chain_adj.connect("value-changed", self.window.on_adjustment_changed, "max-chained-neighbor-updates")
        group.add(chain)
        self.window.add_row(rows, chain, "max chained neighbor updates", "", "max-chained-neighbor-updates")
        
        # Use Native Transport
        native_transport = Adw.SwitchRow(title="Use Native Transport")
        native_transport.set_subtitle("Use native OS networking for better performance")
        native_transport.set_active(properties_data["use-native-transport"] == "true")
        native_transport.connect("notify::active", self.window.on_switch_changed, "use-native-transport")
        group.add(native_transport)
        self.window.add_row(rows, native_transport, "use native transport", "", "use-native-transport")
        
        # Sync Chunk Writes
        sync_chunk = Adw.SwitchRow(title="Sync Chunk Writes")
        sync_chunk.set_subtitle("Force chunk data to disk immediately")
        sync_chunk.set_active(properties_data["sync-chunk-writes"] == "true")
        sync_chunk.connect("notify::active", self.window.on_switch_changed, "sync-chunk-writes")
        group.add(sync_chunk)
        self.window.add_row(rows, sync_chunk, "sync chunk writes", "", "sync-chunk-writes")
        
        # Region File Compression
        region_compression = Adw.ComboRow(title="Region File Compression")
        compressions = ["deflate", "lz4", "none"]
        model = Gtk.StringList()
        for c in compressions:
            model.append(c)
        region_compression.set_model(model)
        current_comp = properties_data["region-file-compression"]
        if current_comp in compressions:
            region_compression.set_selected(compressions.index(current_comp))
        else:
            region_compression.set_selected(0)
        region_compression.connect("notify::selected", self.window.on_combo_changed, "region-file-compression", compressions)
        group.add(region_compression)
        self.window.add_row(rows, region_compression, "region file compression", "", "region-file-compression")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
