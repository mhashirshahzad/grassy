from gi.repository import Adw, Gtk, GLib
import requests
import threading
from pathlib import Path
import appdirs
import subprocess
import re


class ForgeDownloaderWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_title("Download Forge Server")
        self.set_default_size(550, 500)
        self.set_transient_for(parent)
        self.set_modal(True)

        # Data stores
        self.all_mc_versions = []
        self.forge_versions = []      # Forge versions for selected MC version
        self.selected_mc = None
        self.selected_forge = None

        # UI setup
        self.content = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Download Forge Server"))

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda x: self.destroy())
        header.pack_end(cancel_button)

        self.content.add_top_bar(header)

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)

        # --- Minecraft Version ---
        mc_label = Gtk.Label(label="Minecraft Version")
        mc_label.set_halign(Gtk.Align.START)
        mc_label.add_css_class("heading")
        main_box.append(mc_label)

        self.mc_entry = Gtk.Entry()
        self.mc_entry.set_placeholder_text("Loading Minecraft versions...")
        self.mc_entry.set_sensitive(False)
        main_box.append(self.mc_entry)

        self.mc_spinner = Gtk.Spinner()
        self.mc_spinner.set_visible(False)
        main_box.append(self.mc_spinner)

        # --- Separator ---
        sep1 = Gtk.Separator()
        sep1.set_margin_top(12)
        sep1.set_margin_bottom(12)
        main_box.append(sep1)

        # --- Forge Version ---
        forge_label = Gtk.Label(label="Forge Version")
        forge_label.set_halign(Gtk.Align.START)
        forge_label.add_css_class("heading")
        main_box.append(forge_label)

        self.forge_entry = Gtk.Entry()
        self.forge_entry.set_placeholder_text("Select Minecraft version first")
        self.forge_entry.set_sensitive(False)
        main_box.append(self.forge_entry)

        self.forge_spinner = Gtk.Spinner()
        self.forge_spinner.set_visible(False)
        main_box.append(self.forge_spinner)

        # --- Separator ---
        sep2 = Gtk.Separator()
        sep2.set_margin_top(12)
        sep2.set_margin_bottom(12)
        main_box.append(sep2)

        # --- Download Button ---
        self.download_button = Gtk.Button(label="Download Forge Server")
        self.download_button.add_css_class("suggested-action")
        self.download_button.set_sensitive(False)
        self.download_button.connect("clicked", self.on_download_clicked)
        main_box.append(self.download_button)

        # --- Progress & Status ---
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        main_box.append(self.progress_bar)

        self.status_label = Gtk.Label(label="")
        self.status_label.set_visible(False)
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.add_css_class("dim-label")
        main_box.append(self.status_label)

        # Finalize UI
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(main_box)
        self.content.set_content(scrolled)
        self.set_content(self.content)

        # Start loading Minecraft versions
        self.load_minecraft_versions()

    # ----------------------------------------------------------------------
    # 1. LOAD MINECRAFT VERSIONS (from Mojang API)
    # ----------------------------------------------------------------------
    def load_minecraft_versions(self):
        self.mc_spinner.set_visible(True)
        self.mc_spinner.start()
        self.mc_entry.set_placeholder_text("Loading Minecraft versions...")
        threading.Thread(target=self._fetch_mc_versions, daemon=True).start()

    def _fetch_mc_versions(self):
        try:
            url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
            # Get only release versions
            versions = [v["id"] for v in data["versions"] if v["type"] == "release"]
            versions.sort(reverse=True)
            self.all_mc_versions = versions
            GLib.idle_add(self._update_mc_list, versions)
        except Exception as e:
            GLib.idle_add(self.show_error, f"Failed to load Minecraft versions: {str(e)}")

    def _update_mc_list(self, versions):
        self.mc_spinner.stop()
        self.mc_spinner.set_visible(False)

        if not versions:
            self.mc_entry.set_placeholder_text("No versions found")
            return

        # Set up autocomplete
        model = Gtk.ListStore(str)
        for v in versions:
            model.append([v])

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)

        self.mc_entry.set_completion(completion)
        self.mc_entry.set_text(versions[0])
        self.mc_entry.set_sensitive(True)

        # Trigger forge loading
        self.on_mc_changed()
        self.mc_entry.connect("changed", self.on_mc_changed)

    def on_mc_changed(self, *args):
        text = self.mc_entry.get_text().strip()
        if text in self.all_mc_versions:
            self.selected_mc = text
            # Load Forge versions for this Minecraft version
            self._load_forge_versions(text)
        else:
            self.selected_mc = None
            self.download_button.set_sensitive(False)

    # ----------------------------------------------------------------------
    # 2. LOAD FORGE VERSIONS (using Forge API)
    # ----------------------------------------------------------------------
    def _load_forge_versions(self, mc_version):
        self.forge_entry.set_sensitive(False)
        self.forge_entry.set_placeholder_text("Loading Forge versions...")
        self.forge_spinner.set_visible(True)
        self.forge_spinner.start()
        self.download_button.set_sensitive(False)
        threading.Thread(target=self._fetch_forge_versions, args=(mc_version,), daemon=True).start()

    def _fetch_forge_versions(self, mc_version):
        try:
            # Forge API endpoint for specific Minecraft version
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
            
            # Sort versions (newest first)
            versions.sort(reverse=True)
            
            self.forge_versions = versions
            GLib.idle_add(self._update_forge_list, versions)
            
        except Exception as e:
            GLib.idle_add(self.show_error, f"Failed to load Forge versions: {str(e)}")

    def _update_forge_list(self, versions):
        self.forge_spinner.stop()
        self.forge_spinner.set_visible(False)

        if not versions:
            self.forge_entry.set_placeholder_text("No Forge versions found for this MC version")
            self.forge_entry.set_sensitive(False)
            return

        model = Gtk.ListStore(str)
        for v in versions:
            model.append([v])

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)

        self.forge_entry.set_completion(completion)
        self.forge_entry.set_text(versions[0])
        self.forge_entry.set_sensitive(True)

        self.selected_forge = versions[0]
        self._update_download_button()

        self.forge_entry.connect("changed", self.on_forge_changed)

    def on_forge_changed(self, *args):
        text = self.forge_entry.get_text().strip()
        if text in self.forge_versions:
            self.selected_forge = text
        else:
            self.selected_forge = None
        self._update_download_button()

    def _update_download_button(self):
        if self.selected_mc and self.selected_forge:
            self.download_button.set_sensitive(True)
        else:
            self.download_button.set_sensitive(False)

    # ----------------------------------------------------------------------
    # 3. DOWNLOAD PROCESS
    # ----------------------------------------------------------------------
    def on_download_clicked(self, btn):
        if not (self.selected_mc and self.selected_forge):
            self.show_error("Please select Minecraft version and Forge version")
            return

        self.download_button.set_sensitive(False)
        self.mc_entry.set_sensitive(False)
        self.forge_entry.set_sensitive(False)

        self.progress_bar.set_visible(True)
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Downloading Forge {self.selected_forge}...")

        threading.Thread(
            target=self._download_forge_server,
            args=(self.selected_mc, self.selected_forge),
            daemon=True
        ).start()

    def _download_forge_server(self, mc_version, forge_version):
        try:
            # Forge installer URL
            installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar"
            
            servers_dir = self._get_servers_dir()
            folder_name = f"forge_server-{mc_version}-{forge_version}"
            folder = Path(servers_dir) / folder_name
            folder.mkdir(parents=True, exist_ok=True)

            installer_path = folder / "forge_installer.jar"
            server_jar_path = folder / "server.jar"

            # Download installer with progress
            response = requests.get(installer_url, stream=True, timeout=120)
            response.raise_for_status()

            total = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(installer_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            GLib.idle_add(self._update_progress, (downloaded / total) * 0.6)

            # Run installer
            GLib.idle_add(self._update_status, "Installing Forge (this may take a moment)...")
            GLib.idle_add(self._update_progress, 0.7)

            process = subprocess.run(
                ["java", "-jar", str(installer_path), "--installServer", str(folder)],
                cwd=str(folder),
                capture_output=True,
                text=True
            )

            if process.returncode != 0:
                raise Exception(f"Forge installer failed: {process.stderr}")

            GLib.idle_add(self._update_progress, 0.9)

            # Clean up installer
            installer_path.unlink()

            # Find and rename forge jar to server.jar
            forge_jars = list(folder.glob("forge-*.jar"))
            for jar in forge_jars:
                if "server" in jar.name or "universal" in jar.name:
                    jar.rename(server_jar_path)
                    break
            else:
                # If no server/universal jar found, use the first one
                if forge_jars:
                    forge_jars[0].rename(server_jar_path)

            # Accept EULA
            eula_path = folder / "eula.txt"
            with open(eula_path, 'w') as f:
                f.write("eula=true\n")

            GLib.idle_add(self._download_complete, f"Forge {forge_version}", folder_name)

        except subprocess.CalledProcessError as e:
            GLib.idle_add(self.show_error, f"Failed to run Forge installer: {str(e)}")
        except Exception as e:
            GLib.idle_add(self.show_error, f"Download failed: {str(e)}")

    def _update_status(self, message):
        self.status_label.set_label(message)

    def _update_progress(self, fraction):
        self.progress_bar.set_fraction(fraction)

    def _download_complete(self, version, folder_name):
        self.status_label.set_label(f"✓ Successfully installed {version}!")
        self.progress_bar.set_fraction(1.0)
        GLib.timeout_add(1500, self._close_and_refresh)

    def _close_and_refresh(self):
        if self.parent and hasattr(self.parent, "refresh_server_list"):
            self.parent.refresh_server_list()
        self.destroy()
        return False

    # ----------------------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------------------
    def _get_servers_dir(self):
        base = appdirs.user_data_dir("grassy")
        path = Path(base) / "servers"
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    def show_error(self, msg):
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Error: {msg}")
        self.status_label.add_css_class("error")
        self.download_button.set_sensitive(True)
        self.mc_entry.set_sensitive(True)
        self.forge_entry.set_sensitive(True)
        self.progress_bar.set_visible(False)
        # Stop any visible spinners
        for spinner in [self.mc_spinner, self.forge_spinner]:
            spinner.stop()
            spinner.set_visible(False)
