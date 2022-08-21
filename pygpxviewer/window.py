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

from typing import Optional

from gi.repository import Adw, Gio, GLib, GObject, Gtk

from pygpxviewer.widgets.appmenu import AppMenu


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/Window.ui")
class Window(Adw.ApplicationWindow):
    __gtype_name__ = "Window"

    _headerbar = Gtk.Template.Child()
    _menu_button = Gtk.Template.Child()
    _scrolled_window = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)

        self._app = application

        self._set_css()
        self._settings = Gio.Settings.new("com.github.pygpxviewer.window")

        self._set_actions()
        self._setup_view()

    @GObject.Property(
        type=Gio.Settings, flags=GObject.ParamFlags.READABLE)
    def settings(self):
        return self._settings

    def _set_actions(self):
        action_entries = [
            ('refresh', self._refresh, ("win.refresh", ["<Ctrl>R"])),
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

        self._menu_button.set_popover(AppMenu())

    def _set_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource("/com/github/pygpxviewer/style.css")
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @Gtk.Template.Callback()
    def _on_open_button_clicked(
            self, button: Gtk.Button) -> None:
        print("_on_open_button_clicked")

    @Gtk.Template.Callback()
    def _on_search_entry_search_changed(
            self, search_entry: Gtk.SearchEntry) -> None:
        print("_on_search_entry_changed")

    def _refresh(self, action: Gio.SimpleAction,
                 param: Optional[GLib.Variant]) -> None:
        print("_refresh")

    def _about(self, action: Gio.SimpleAction,
               param: Optional[GLib.Variant]) -> None:
        print("_about")
