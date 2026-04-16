from gi.repository import Adw, Gtk, GLib
import requests
import os
import threading
import subprocess
from pathlib import Path
import appdirs


class ForgeDownloaderWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        
        self.parent = parent
        self.set_title("Download Forge Server")
        self.set_default_size(600, 400)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        # Main layout
        self.content = Adw.ToolbarView()
        
        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Download Forge Server"))
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda x: self.destroy())
        header.pack_end(cancel_button)
        
        self.content.add_top_bar(header)
        
        # Main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Minecraft version selection
        mc_label = Gtk.Label(label="Minecraft Version")
        mc_label.set_halign(Gtk.Align.START)
        mc_label.add_css_class("heading")
        main_box.append(mc_label)
        
        self.mc_version_entry = Adw.EntryRow()
        self.mc_version_entry.set_text("1.20.1")
        main_box.append(self.mc_version_entry)
        
        # Forge version selection
        forge_label = Gtk.Label(label="Forge Version")
        forge_label.set_halign(Gtk.Align.START)
        forge_label.add_css_class("heading")
        forge_label.set_margin_top(12)
        main_box.append(forge_label)
        
        # Forge version combo
        self.forge_version_combo = Adw.ComboRow()
        self.forge_version_combo.set_title("Select Forge Version")
        self.forge_version_combo.set_subtitle("Click to load versions first")
        self.forge_version_combo.set_sensitive(False)
        main_box.append(self.forge_version_combo)
        
        # Load versions button
        self.load_versions_btn = Gtk.Button(label="Load Available Versions")
        self.load_versions_btn.add_css_class("suggested-action")
        self.load_versions_btn.connect("clicked", self.on_load_versions_clicked)
        main_box.append(self.load_versions_btn)
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        separator.set_margin_bottom(12)
        main_box.append(separator)
        
        # Download button
        self.download_button = Gtk.Button(label="Download Forge Server")
        self.download_button.add_css_class("suggested-action")
        self.download_button.connect("clicked", self.on_download_clicked)
        self.download_button.set_sensitive(False)
        main_box.append(self.download_button)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_visible(False)
        main_box.append(self.progress_bar)
        
        # Status label
        self.status_label = Gtk.Label(label="")
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_visible(False)
        main_box.append(self.status_label)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(main_box)
        self.content.set_content(scrolled)
        
        self.set_content(self.content)
        
        self.forge_versions = []
        self.selected_forge_version = None
    
    def get_servers_dir(self):
        """Get the servers directory from settings (cross-platform)"""
        config_dir = appdirs.user_config_dir("grassy")
        settings_file = os.path.join(config_dir, "settings.txt")
        data_dir = appdirs.user_data_dir("grassy")
        default_dir = os.path.join(data_dir, "servers")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    saved_dir = f.read().strip()
                    if saved_dir and os.path.exists(saved_dir):
                        return saved_dir
            except:
                pass
        
        # Create default directory if it doesn't exist
        os.makedirs(default_dir, exist_ok=True)
        return default_dir
    
    def on_load_versions_clicked(self, button):
        """Load Forge versions for the specified Minecraft version"""
        mc_version = self.mc_version_entry.get_text().strip()
        
        if not mc_version:
            self.show_error("Please enter a Minecraft version")
            return
        
        self.load_versions_btn.set_sensitive(False)
        self.load_versions_btn.set_label("Loading...")
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Loading Forge versions for {mc_version}...")
        
        thread = threading.Thread(target=self.load_forge_versions, args=(mc_version,))
        thread.daemon = True
        thread.start()
    
    def load_forge_versions(self, mc_version):
        """Load Forge versions in background thread"""
        try:
            # Forge API endpoint
            url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{mc_version}.json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 404:
                GLib.idle_add(self.show_error, f"No Forge versions found for Minecraft {mc_version}")
                return
            
            response.raise_for_status()
            data = response.json()
            
            # Extract versions
            versions = []
            if "number" in data:
                versions.append(data["number"])
            elif "versions" in data:
                versions = list(data["versions"].keys())
            
            if not versions:
                GLib.idle_add(self.show_error, f"No Forge versions available for {mc_version}")
                return
            
            versions.sort(reverse=True)
            self.forge_versions = versions
            
            GLib.idle_add(self.update_forge_versions, versions)
            
        except requests.RequestException as e:
            GLib.idle_add(self.show_error, f"Failed to load versions: {str(e)}")
    
    def update_forge_versions(self, versions):
        """Update the combo box with available versions"""
        model = Gtk.StringList()
        for version in versions:
            model.append(version)
        
        self.forge_version_combo.set_model(model)
        self.forge_version_combo.set_sensitive(True)
        self.forge_version_combo.connect("notify::selected", self.on_forge_version_selected)
        
        self.load_versions_btn.set_sensitive(True)
        self.load_versions_btn.set_label("Load Available Versions")
        self.status_label.set_visible(False)
        self.download_button.set_sensitive(True)
    
    def on_forge_version_selected(self, combo, _pspec):
        """Handle Forge version selection"""
        selected = combo.get_selected()
        if selected >= 0:
            self.selected_forge_version = self.forge_versions[selected]
    
    def on_download_clicked(self, button):
        """Start Forge download"""
        mc_version = self.mc_version_entry.get_text().strip()
        
        if not mc_version:
            self.show_error("Please enter a Minecraft version")
            return
        
        if not self.selected_forge_version:
            self.show_error("Please select a Forge version")
            return
        
        # Disable download button
        self.download_button.set_sensitive(False)
        self.download_button.set_label("Downloading...")
        
        # Show progress
        self.progress_bar.set_visible(True)
        self.progress_bar.set_fraction(0.0)
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Downloading Forge {self.selected_forge_version}...")
        
        # Start download thread
        thread = threading.Thread(
            target=self.download_forge,
            args=(mc_version, self.selected_forge_version)
        )
        thread.daemon = True
        thread.start()
    
    def download_forge(self, mc_version, forge_version):
        """Download and install Forge server"""
        try:
            # Download Forge installer
            download_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar"
            
            self.update_status("Downloading Forge installer...")
            
            servers_dir = self.get_servers_dir()
            server_folder = Path(servers_dir) / f"forge_{mc_version}_{forge_version}"
            server_folder.mkdir(parents=True, exist_ok=True)
            
            installer_path = server_folder / "forge_installer.jar"
            
            # Download with progress
            response = requests.get(download_url, stream=True, timeout=120)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = downloaded / total_size
                            GLib.idle_add(self.update_progress, progress * 0.6)
            
            self.update_status("Installing Forge (this may take a moment)...")
            GLib.idle_add(self.update_progress, 0.7)
            
            # Run Forge installer
            process = subprocess.run([
                "java", "-jar", str(installer_path), "--installServer",
                str(server_folder)
            ], cwd=str(server_folder), capture_output=True, text=True)
            
            if process.returncode != 0:
                raise Exception(f"Forge installer failed: {process.stderr}")
            
            GLib.idle_add(self.update_progress, 0.95)
            
            # Clean up installer
            installer_path.unlink()
            
            # Find and rename forge jar to server.jar
            forge_jars = list(server_folder.glob("forge-*.jar"))
            for jar in forge_jars:
                if "server" in jar.name or "universal" in jar.name:
                    jar.rename(server_folder / "server.jar")
                    break
            else:
                # If no server/universal jar found, use the largest jar
                if forge_jars:
                    forge_jars[0].rename(server_folder / "server.jar")
            
            # Accept EULA
            eula_path = server_folder / "eula.txt"
            with open(eula_path, 'w') as f:
                f.write("eula=true\n")
            
            GLib.idle_add(self.download_complete, f"Forge {forge_version}", server_folder)
            
        except subprocess.CalledProcessError as e:
            GLib.idle_add(self.show_error, f"Failed to run Forge installer: {str(e)}")
        except Exception as e:
            GLib.idle_add(self.show_error, f"Failed to install Forge: {str(e)}")
    
    def update_status(self, message):
        """Update status label"""
        GLib.idle_add(lambda: self.status_label.set_label(message))
    
    def update_progress(self, fraction):
        """Update progress bar"""
        self.progress_bar.set_fraction(fraction)
    
    def download_complete(self, version, server_folder):
        """Handle successful download"""
        self.status_label.set_label(f"✓ Successfully installed {version}!")
        self.progress_bar.set_fraction(1.0)
        
        GLib.timeout_add(1500, self.close_and_refresh)
    
    def close_and_refresh(self):
        """Close dialog and refresh server list"""
        if self.parent and hasattr(self.parent, 'refresh_server_list'):
            self.parent.refresh_server_list()
        self.destroy()
        return False
    
    def show_error(self, error_message):
        """Show error message"""
        self.status_label.set_label(f"Error: {error_message}")
        self.status_label.add_css_class("error")
        self.download_button.set_sensitive(True)
        self.download_button.set_label("Download Forge Server")
        self.progress_bar.set_visible(False)
        self.load_versions_btn.set_sensitive(True)
