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
from pathlib import Path

from gi.repository import Adw, Gio, Gtk

from pygpxviewer import config
from pygpxviewer.logger import Logger

logger = Logger()


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/WindowSettings.ui")
class WindowSettings(Adw.Window):
    """Window settings manager."""

    __gtype_name__ = "WindowSettings"

    _clean_headers_switch = Gtk.Template.Child()
    _clean_attributes_switch = Gtk.Template.Child()
    _elevation_switch = Gtk.Template.Child()
    _simplify_switch = Gtk.Template.Child()
    _clear_cache_label = Gtk.Template.Child()

    def __init__(self, window):
        super().__init__(title="Settings")

        self._window = window
        self._settings = Gio.Settings.new("com.github.pygpxviewer.gpx")
        self._size = None

        self._set_binding()
        self._set_cache()

    def _set_binding(self):
        self._settings.bind(
            "clean-headers", self._clean_headers_switch, "active",
            Gio.SettingsBindFlags.DEFAULT)

        self._settings.bind(
            "clean-attributes", self._clean_attributes_switch, "active",
            Gio.SettingsBindFlags.DEFAULT)

        self._settings.bind(
            "elevation", self._elevation_switch, "active",
            Gio.SettingsBindFlags.DEFAULT)

        self._settings.bind(
            "simplify", self._simplify_switch, "active",
            Gio.SettingsBindFlags.DEFAULT)

    def _set_cache(self):
        self._size = sum(f.stat().st_size for f in Path(config.dem_path).glob("**/*.hgt") if f.is_file())
        self._size = round(self._size / 1000 / 1000)
        self._clear_cache_label.set_label(f"{self._size} MB")

    @Gtk.Template.Callback()
    def _on_clear_cache_button_clicked(self, widget):
        for path in Path(config.dem_path).glob("**/*.hgt"):
            path.unlink()
        logger.info(f"cache cleared: {self._size} MB")
        self._set_cache()
