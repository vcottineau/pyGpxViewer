import pathlib
import threading

from gi.repository import Gio, GObject, Gtk

from config import Config
from pygpxviewer.app_column_view import AppColumnView
from pygpxviewer.helpers import gpx_helper, sqlite_helper


class AppWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "app_window"

    folder_path = GObject.Property(type=str)

    def __init__(self, application):
        super().__init__(application=application)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_resource("/com/github/pygpxviewer/style.css")
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.settings = Gio.Settings.new("com.github.pygpxviewer.app.window")

        self.set_size_request(300, 600)

        self.app_column_view = AppColumnView()
        self.connect("notify::folder-path", self.app_column_view.on_folder_path_changed)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.app_column_view)

        self.settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-fullscreen", self, "fullscreened", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("folder-path", self, "folder-path", Gio.SettingsBindFlags.DEFAULT)

        self.set_header_bar()
        self.set_child(self.scrolled_window)

    def set_header_bar(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)

        title_widget = Gtk.Label()
        title_widget.set_markup(f"<b>{Config.PROGRAM_NAME}</b>")
        title_widget.set_hexpand_set(False)
        title_widget.set_hexpand(False)
        header_bar.set_title_widget(title_widget)

        button_open = Gtk.Button.new_from_icon_name("document-open-symbolic")
        button_open.connect("clicked", self.on_button_open_clicked)
        header_bar.pack_start(button_open)

        search_entry = Gtk.SearchEntry()
        search_entry.set_hexpand_set(True)
        search_entry.set_hexpand(True)
        search_entry.set_halign(Gtk.Align.FILL)
        search_entry.connect("changed", self.app_column_view.on_search_entry_changed)
        header_bar.pack_start(search_entry)

        popover = Gtk.Popover()
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("view-more-symbolic")
        menu_button.set_popover(popover)
        header_bar.pack_end(menu_button)

        button_refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        button_refresh.connect("clicked", self.on_button_refresh_clicked)
        header_bar.pack_end(button_refresh)

        self.spinner = Gtk.Spinner()
        header_bar.pack_end(self.spinner)

        self.set_titlebar(header_bar)

    def on_button_open_clicked(self, button):
        self.file_chooser = Gtk.FileChooserNative.new(
            title="Select folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER)
        self.file_chooser.connect("response", self.on_file_chooser_response)
        self.file_chooser.show()

    def on_button_refresh_clicked(self, button):
        self.update_records()

    def on_file_chooser_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.folder_path = dialog.get_file().get_path()
            self.update_records()

    def update_records(self):
        self.spinner.start()
        self.set_sensitive(False)
        thread = WorkerUpdateThread(self.folder_path, self.on_update_records_ended)
        thread.start()

    def on_update_records_ended(self):
        self.app_column_view.reset_liststore()
        self.set_sensitive(True)
        self.spinner.stop()


class WorkerUpdateThread(threading.Thread):
    def __init__(self, folder_path, callback):
        threading.Thread.__init__(self)
        self.folder_path = folder_path
        self.callback = callback

    def run(self):
        sqlite_helper.clear_records()
        for file in pathlib.Path(self.folder_path).glob("**/*.gpx"):
            gpx_helper.set_gpx(file)
            record = (
                str(file),
                gpx_helper.get_gpx_points_nb(),
                gpx_helper.get_gpx_length(),
                gpx_helper.get_gpx_up_hill(),
                gpx_helper.get_gpx_down_hill()
            )
            sqlite_helper.add_record(record)
        GObject.idle_add(self.callback)
