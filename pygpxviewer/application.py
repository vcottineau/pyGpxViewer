from gi.repository import Gio, GLib, Gtk

from config import Config
from pygpxviewer.app_window import AppWindow


class Application(Gtk.Application):
    __gtype_name__ = "app"

    def __init__(self, application_id):
        super().__init__(application_id=application_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.props.resource_base_path = "/com/github/vcottineau/pygpxviewer/"
        GLib.set_application_name(Config.PROGRAM_NAME)
        GLib.set_prgname(application_id)

        self.app_window = None

    def do_activate(self):
        self.app_window = self.props.active_window
        if not self.app_window:
            self.app_window = AppWindow(application=self)
            self.app_window.set_default_icon_name(self.props.application_id)
        self.app_window.present()
