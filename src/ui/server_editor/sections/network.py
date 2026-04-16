from gi.repository import Adw, Gtk


class NetworkSection:
    def __init__(self, window):
        self.window = window
    
    def create(self, preferences_page, groups, properties_data):
        group = Adw.PreferencesGroup(title="Network Settings")
        rows = []
        
        # Online Mode
        online = Adw.SwitchRow(title="Online Mode")
        online.set_subtitle("Enable authentication (false = cracked server)")
        online.set_active(properties_data["online-mode"] == "true")
        online.connect("notify::active", self.window.on_switch_changed, "online-mode")
        group.add(online)
        self.window.add_row(rows, online, "online mode", "", "online-mode")
        
        # Enforce Secure Profile
        secure_profile = Adw.SwitchRow(title="Enforce Secure Profile")
        secure_profile.set_subtitle("Require chat signing and secure profiles")
        secure_profile.set_active(properties_data["enforce-secure-profile"] == "true")
        secure_profile.connect("notify::active", self.window.on_switch_changed, "enforce-secure-profile")
        group.add(secure_profile)
        self.window.add_row(rows, secure_profile, "secure profile", "", "enforce-secure-profile")
        
        # Prevent Proxy Connections
        prevent_proxy = Adw.SwitchRow(title="Prevent Proxy Connections")
        prevent_proxy.set_subtitle("Prevent VPN and proxy connections")
        prevent_proxy.set_active(properties_data["prevent-proxy-connections"] == "true")
        prevent_proxy.connect("notify::active", self.window.on_switch_changed, "prevent-proxy-connections")
        group.add(prevent_proxy)
        self.window.add_row(rows, prevent_proxy, "prevent proxy", "", "prevent-proxy-connections")
        
        # Rate Limit
        rate_limit_adj = Gtk.Adjustment(
            value=int(properties_data.get("rate-limit", "0")),
            lower=0, upper=100, step_increment=1, page_increment=5
        )
        rate_limit = Adw.SpinRow()
        rate_limit.set_title("Rate Limit")
        rate_limit.set_subtitle("Max packets per second (0 = unlimited)")
        rate_limit.set_adjustment(rate_limit_adj)
        rate_limit_adj.connect("value-changed", self.window.on_adjustment_changed, "rate-limit")
        group.add(rate_limit)
        self.window.add_row(rows, rate_limit, "rate limit", "", "rate-limit")
        
        # Network Compression
        compression_adj = Gtk.Adjustment(
            value=int(properties_data.get("network-compression-threshold", "256")),
            lower=0, upper=1024, step_increment=32, page_increment=128
        )
        compression = Adw.SpinRow()
        compression.set_title("Network Compression Threshold (bytes)")
        compression.set_subtitle("0 = compress everything")
        compression.set_adjustment(compression_adj)
        compression_adj.connect("value-changed", self.window.on_adjustment_changed, "network-compression-threshold")
        group.add(compression)
        self.window.add_row(rows, compression, "network compression", "", "network-compression-threshold")
        
        # Enable Status
        enable_status = Adw.SwitchRow(title="Enable Server Status")
        enable_status.set_subtitle("Show server in server list")
        enable_status.set_active(properties_data["enable-status"] == "true")
        enable_status.connect("notify::active", self.window.on_switch_changed, "enable-status")
        group.add(enable_status)
        self.window.add_row(rows, enable_status, "enable status", "", "enable-status")
        
        # Accepts Transfers
        accepts_transfers = Adw.SwitchRow(title="Accepts Transfers")
        accepts_transfers.set_subtitle("Allow server transfers via command")
        accepts_transfers.set_active(properties_data["accepts-transfers"] == "true")
        accepts_transfers.connect("notify::active", self.window.on_switch_changed, "accepts-transfers")
        group.add(accepts_transfers)
        self.window.add_row(rows, accepts_transfers, "accepts transfers", "", "accepts-transfers")
        
        preferences_page.add(group)
        self.window.register_group(group, rows)
