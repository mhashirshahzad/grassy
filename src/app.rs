use adw::gtk;
use adw::prelude::*;
pub fn run() {
    let app = GameApp::new();
    app.run();
}

struct GameApp {
    app: adw::Application,
}

impl GameApp {
    pub fn new() -> Self {
        let app = adw::Application::new(
            Some("org.bongo.grassy"),
            adw::gio::ApplicationFlags::empty(),
        );

        app.connect_activate(|app| {
            let window = MainWindow::new(app);
            window.present();
        });

        GameApp { app }
    }

    pub fn run(self) {
        self.app.run();
    }
}

struct MainWindow {
    window: adw::ApplicationWindow,
}

impl MainWindow {
    pub fn new(app: &adw::Application) -> Self {
        let window = adw::ApplicationWindow::new(app);
        window.set_title(Some("Grassy"));
        window.set_default_size(800, 600);
        // Create header bar (libadwaita provides one by default)
        let header = adw::HeaderBar::new();

        // Add buttons to header
        let add_button = adw::gtk::Button::new();
        add_button.set_icon_name("list-add-symbolic");
        header.pack_start(&add_button);

        let menu_button = gtk::MenuButton::new();
        menu_button.set_icon_name("open-menu-symbolic");
        header.pack_end(&menu_button);

        // Create main content
        let content = gtk::Box::new(gtk::Orientation::Vertical, 12);
        content.set_margin_top(12);
        content.set_margin_bottom(12);
        content.set_margin_start(12);
        content.set_margin_end(12);

        let label = gtk::Label::new(Some("Minecraft Server Manager"));
        label.add_css_class("title-1");
        content.append(&label);

        let button = gtk::Button::with_label("Start Server");
        button.add_css_class("suggested-action");
        content.append(&button);

        window.set_titlebar(Some(&header));
        window.set_child(Some(&content));

        MainWindow { window }
    }

    pub fn present(&self) {
        self.window.show();
    }
}
