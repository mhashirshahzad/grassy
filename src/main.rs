mod app;

fn main() {
    // Don't call gtk::init manually - let adw handle it
    // Just set the environment variable before creating the app
    std::env::set_var("GTK_CSD", "0");

    app::run();
}
