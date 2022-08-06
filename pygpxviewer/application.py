from pathlib import Path


from gi.repository import Gtk, Gio, GLib


from pygpxviewer.app_window import AppWindow
from config import Config


class Application(Gtk.Application):
    def __init__(self, application_id):
        super().__init__(application_id=application_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

        GLib.set_prgname(application_id)
        self.settings = Gio.Settings.new(application_id)

        self.app_window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("refresh", None)
        action.connect("activate", self.on_refresh)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):        
        if not self.app_window:
            self.app_window = AppWindow(application=self)
        self.app_window.present()

    def on_refresh(self, action, param):
        self.app_window.start_refresh()

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.app_window, modal=True)
        about_dialog.set_logo_icon_name(self.get_application_id())
        about_dialog.set_program_name(Config.PROGRAM_NAME)
        about_dialog.set_authors(["Vincent Cottineau <perso@vcottineau.fr>"])
        about_dialog.set_version(Config.VERSION)
        about_dialog.set_comments("A simple Gtk3 application to plot gpx files.")
        about_dialog.set_website("https://github.com/vcottineau/pyGpxViewer")
        about_dialog.set_license(Path('LICENSE').read_text())
        about_dialog.present()

    def on_quit(self, action, param):
        self.quit()
