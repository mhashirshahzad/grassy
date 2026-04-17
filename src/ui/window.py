from gi.repository import Adw, Gtk, Gio
from pathlib import Path
import os
import appdirs

#
from ui.settings import SettingsWindow
from ui.card import ServerCard

from ui.downloader.minecraft import MinecraftDownloaderWindow
from ui.downloader.forge import ForgeDownloaderWindow
from ui.downloader.fabric import FabricDownloaderWindow
from ui.server_runner import ServerRunnerWindow

from utils import get_servers_dir, save_servers_dir, is_java_installed


class GrassyWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Grassy")
        self.set_default_size(800, 600)

        # store cards for filtering
        self.server_cards = []

        # -------------------------
        # MAIN LIST
        # -------------------------
        self.server_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        self.server_list.set_margin_top(12)
        self.server_list.set_margin_bottom(12)
        self.server_list.set_margin_start(12)
        self.server_list.set_margin_end(12)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self.server_list)

        # -------------------------
        # HEADER
        # -------------------------
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Grassy - Minecraft Server Manager"))

        settings_button = Gtk.Button.new_from_icon_name("emblem-system-symbolic")
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self.on_settings_clicked)
        header.pack_start(settings_button)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search servers...")
        self.search_entry.set_width_chars(18)
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self.on_search_changed)
        header.pack_start(self.search_entry)

        # -------------------------
        # DOWNLOAD MENU
        # -------------------------
        self.download_button = Gtk.MenuButton()
        self.download_button.set_icon_name("list-add-symbolic")
        self.download_button.set_tooltip_text("Download Minecraft server")
        self.download_button.add_css_class("suggested-action")

        self.create_actions()

        menu_model = Gio.Menu()
        menu_model.append("Official Minecraft Server", "win.download_official")
        menu_model.append("Forge (Modded)", "win.download_forge")
        menu_model.append("Fabric (Modded)", "win.download_fabric")

        popover = Gtk.PopoverMenu()
        popover.set_menu_model(menu_model)
        self.download_button.set_popover(popover)

        header.pack_end(self.download_button)

        scan_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        scan_button.set_tooltip_text("Scan for servers")
        scan_button.connect("clicked", self.on_scan_clicked)
        header.pack_end(scan_button)

        # -------------------------
        # FOOTER (JAVA STATUS)
        # -------------------------
        self.java_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.java_status.set_margin_top(6)
        self.java_status.set_margin_bottom(6)
        self.java_status.set_margin_start(12)
        self.java_status.set_margin_end(12)
        self.java_status.set_halign(Gtk.Align.CENTER)

        # Dot indicator
        self.java_dot = Gtk.Label()
        self.java_dot.set_use_markup(True)

        # Text
        self.java_label = Gtk.Label(label="Checking Java...")
        self.java_label.add_css_class("heading")  # clean, header-like typography

        self.java_status.append(self.java_dot)
        self.java_status.append(self.java_label)
        # -------------------------
        # LAYOUT
        # -------------------------
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(scrolled)
        main_box.append(self.java_status)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(main_box)

        self.set_content(toolbar)

        # -------------------------
        # INIT
        # -------------------------
        self.refresh_server_list()
        self.update_java_status()

    # -------------------------
    # JAVA STATUS
    # -------------------------
    def update_java_status(self):
        if is_java_installed():
            self.java_dot.set_markup("<span foreground='green'>●</span>")
            self.java_label.set_text("Java detected")
        else:
            self.java_dot.set_markup("<span foreground='red'>●</span>")
            self.java_label.set_text("Java not found")
    # -------------------------
    # ACTIONS
    # -------------------------

    def create_actions(self):
        action_official = Gio.SimpleAction.new("download_official", None)
        action_official.connect("activate", self.on_download_official)
        self.add_action(action_official)

        action_forge = Gio.SimpleAction.new("download_forge", None)
        action_forge.connect("activate", self.on_download_forge)
        self.add_action(action_forge)

        action_fabric = Gio.SimpleAction.new("download_fabric", None)
        action_fabric.connect("activate", self.on_download_fabric)
        self.add_action(action_fabric)

    def on_download_official(self, action, param):
        window = MinecraftDownloaderWindow(parent=self)
        window.connect("destroy", lambda d: self.refresh_server_list())
        window.present()

    def on_download_forge(self, action, param):
        window = ForgeDownloaderWindow(parent=self)
        window.connect("destroy", lambda d: self.refresh_server_list())
        window.present()

    def on_download_fabric(self, action, param):
        window = FabricDownloaderWindow(parent=self)
        window.connect("destroy", lambda d: self.refresh_server_list())
        window.present()

    # -------------------------
    # SERVER LOADING
    # -------------------------

    def refresh_server_list(self):
        for child in list(self.server_list):
            self.server_list.remove(child)

        self.server_cards = []

        servers_dir = get_servers_dir()

        if not os.path.exists(servers_dir):
            os.makedirs(servers_dir, exist_ok=True)
            self.show_empty_state(servers_dir)
            return

        server_folders = []

        for item in Path(servers_dir).iterdir():
            if item.is_dir() and (item / "server.jar").exists():
                server_folders.append(item)

        if not server_folders:
            self.show_empty_state(servers_dir)
            return

        for folder in sorted(server_folders):
            card = ServerCard(
                folder,
                on_server_changed=self.refresh_server_list
            )

            self.server_cards.append((folder.name.lower(), card))
            self.server_list.append(card)

    # -------------------------
    # SEARCH
    # -------------------------

    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()

        for name, card in self.server_cards:
            card.set_visible(query in name)

    # -------------------------
    # EMPTY STATE
    # -------------------------

    def show_empty_state(self, servers_dir):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_vexpand(True)

        icon = Gtk.Image.new_from_icon_name("folder-symbolic")
        icon.set_pixel_size(64)
        box.append(icon)

        label = Gtk.Label(label="No servers found")
        label.add_css_class("title-4")
        box.append(label)

        sub = Gtk.Label(
            label=f"Create folders in:\n{servers_dir}\nwith server.jar inside"
        )
        sub.set_halign(Gtk.Align.CENTER)
        sub.add_css_class("dim-label")
        box.append(sub)

        btn = Gtk.Button(label="Download Server")
        btn.add_css_class("suggested-action")
        btn.connect("clicked", self.on_download_clicked)
        box.append(btn)

        self.server_list.append(box)

    def on_download_clicked(self, button):
        self.download_button.set_active(True)

    # -------------------------
    # HANDLERS
    # -------------------------

    def on_settings_clicked(self, button):
        dialog = SettingsWindow(parent=self)
        dialog.connect("destroy", lambda d: self.refresh_server_list())
        dialog.present()

    def on_scan_clicked(self, button):
        self.refresh_server_list()
        self.update_java_status()
