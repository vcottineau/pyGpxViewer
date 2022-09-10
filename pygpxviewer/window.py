#  MIT License
#
#  Copyright (c) 2022 Vincent Cottineau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from gettext import gettext as _
from typing import Optional

from gi.repository import Adw, Gio, GLib, GObject, Gtk

from pygpxviewer.threads.workers import WorkerUpdateRecords
from pygpxviewer.widgets.appmenu import AppMenu
from pygpxviewer.widgets.gpxcolumnview import GpxColumnView
from pygpxviewer.widgets.windowsettings import WindowSettings


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/Window.ui")
class Window(Adw.ApplicationWindow):
    """Main application window manager."""

    __gtype_name__ = "Window"

    folder_path = GObject.Property(type=str)

    _headerbar = Gtk.Template.Child()
    _menu_button = Gtk.Template.Child()
    _scrolled_window = Gtk.Template.Child()
    _spinner = Gtk.Template.Child()

    def __init__(self, application: Adw.ApplicationWindow):
        super().__init__(application=application)

        self._app = application

        self._set_css()
        self._settings = Gio.Settings.new("com.github.pygpxviewer.window")

        self._app_menu = AppMenu()
        self._gpx_column_view = GpxColumnView(self)

        self._set_actions()
        self._setup_view()

        self._gpx_column_view.refresh()

    @GObject.Property(type=Gtk.Spinner, flags=GObject.ParamFlags.READABLE)
    def spinner(self) -> Gtk.Spinner:
        """Get spinner object property.

        :returns: Spinner object for threading tasks
        :rtype: Gtk.Spinner
        """
        return self._spinner

    @GObject.Property(type=Gio.Settings, flags=GObject.ParamFlags.READABLE)
    def settings(self) -> Gio.Settings:
        """Get Window settings property.

        :returns: Window settings
        :rtype: Gio.Settings
        """
        return self._settings

    def _set_actions(self):
        action_entries = [
            ('refresh', self._refresh, ("win.refresh", ["<Ctrl>R"])),
            ('window_settings', self._window_settings, None),
            ("about", self._about, None)
        ]

        for action, callback, accel in action_entries:
            simple_action = Gio.SimpleAction.new(action, None)
            simple_action.connect('activate', callback)
            self.add_action(simple_action)
            if accel is not None:
                self._app.set_accels_for_action(*accel)

    def _setup_view(self):
        self._settings.bind(
            "width", self, "default-width",
            Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind(
            "height", self, "default-height",
            Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind(
            "is-maximized", self, "maximized",
            Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind(
            "is-fullscreen", self, "fullscreened",
            Gio.SettingsBindFlags.DEFAULT)

        self.settings.bind(
            "folder-path", self, "folder-path",
            Gio.SettingsBindFlags.DEFAULT)

        self._menu_button.set_popover(self._app_menu)
        self._scrolled_window.set_child(self._gpx_column_view)

    def _set_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource("/com/github/pygpxviewer/style.css")
        Gtk.StyleContext.add_provider_for_display(self.get_display(), css_provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @Gtk.Template.Callback()
    def _on_open_button_clicked(self, button: Gtk.Button) -> None:
        self.file_chooser = Gtk.FileChooserNative.new(
            title=_("Select folder"),
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER)
        self.file_chooser.connect("response", self._on_file_chooser_response)
        self.file_chooser.show()

    @Gtk.Template.Callback()
    def _on_search_entry_search_changed(self, search_entry: Gtk.SearchEntry) -> None:
        self._gpx_column_view.refresh(search_entry.get_text().lower())

    def _on_file_chooser_response(self, dialog: Gtk.FileChooserNative, response: Gtk.ResponseType) -> None:
        if response == Gtk.ResponseType.ACCEPT:
            self.folder_path = dialog.get_file().get_path()
            self._update_records()

    def _update_records(self):
        self.set_sensitive(False)
        self._spinner.start()

        thread = WorkerUpdateRecords(self.folder_path, self._on_update_records_ended)
        thread.start()

    def _on_update_records_ended(self):
        self._gpx_column_view.refresh()
        self._spinner.stop()
        self.set_sensitive(True)

    def _refresh(self, action: Gio.SimpleAction, param: Optional[GLib.Variant]) -> None:
        self._update_records()

    def _window_settings(self, action: Gio.SimpleAction, param: Optional[GLib.Variant]) -> None:
        window_settings = WindowSettings(self)
        window_settings.props.transient_for = self
        window_settings.present()

    def _about(self, action: Gio.SimpleAction, param: Optional[GLib.Variant]) -> None:
        # ToDo: Add AboutWindow
        # https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/class.AboutWindow.html
        pass
