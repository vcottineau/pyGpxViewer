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

import json
import os

from gi.repository import Adw, Gio, GLib, GObject, Gtk

import pygpxviewer.config as config
from pygpxviewer.helpers.gpxhelper import GpxHelper
from pygpxviewer.widgets.elevationprofile import ElevationProfile
from pygpxviewer.widgets.shumatemap import ShumateMap


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/GpxDetailedView.ui")
class GpxDetailedView(Adw.Window):
    __gtype_name__ = "GpxDetailedView"

    _menu_button = Gtk.Template.Child()
    _box_container = Gtk.Template.Child()
    _points_label = Gtk.Template.Child()
    _length_label = Gtk.Template.Child()
    _up_hill_label = Gtk.Template.Child()
    _down_hill_label = Gtk.Template.Child()

    def __init__(self, path):
        super().__init__()

        self._path = path
        self._gpx_helper = GpxHelper(self._path)
        self._settings = Gio.Settings.new("com.github.pygpxviewer.app.window.detailed")

        self.set_title(os.path.basename(self._path))

        self._shumate_map = None
        self._elevation_profile = None

        self._setup_actions()
        self._setup_view()
        self._setup_layers_menu()

    @GObject.Property(type=Gio.Settings, flags=GObject.ParamFlags.READABLE)
    def settings(self):
        return self._settings

    @GObject.Property(type=GObject.GObject, flags=GObject.ParamFlags.READABLE)
    def gpx_helper(self):
        return self._gpx_helper

    def _setup_actions(self):
        action_group = Gio.SimpleActionGroup()
        actions = (
            ("layer", self._on_layer_action),
        )
        for (name, callback) in actions:
            action = Gio.SimpleAction.new(name, GLib.VariantType.new("s"))
            action.connect("activate", callback)
            action_group.add_action(action)

        self.insert_action_group("view", action_group)

    def _setup_view(self):
        self._settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("is-fullscreen", self, "fullscreened", Gio.SettingsBindFlags.DEFAULT)

        _, points, length, up_hill, down_hill = self._gpx_helper.get_gpx_details()
        self._points_label.set_text(str(points))
        self._length_label.set_text(str(round(length)))
        self._up_hill_label.set_text(str(round(up_hill)))
        self._down_hill_label.set_text(str(round(down_hill)))

        self._shumate_map = ShumateMap(self)
        self._box_container.append(self._shumate_map)

        if self._gpx_helper.gpx.has_elevations():
            self._elevation_profile = ElevationProfile(self)
            self._elevation_profile.connect("on-mouse-move-event", self._shumate_map.on_mouse_move_event)
            self._box_container.append(self._elevation_profile)

    def _setup_layers_menu(self):
        menu_model = Gio.Menu()
        self._menu_button.set_menu_model(menu_model)

        map_sources = self._get_map_sources()
        for provider in map_sources["providers"]:
            sub_menu = Gio.Menu()
            for layer in provider["layers"]:
                name, url = layer["name"], layer["url"]
                sub_menu.append(name, f"view.layer('{url}')")
            menu_model.append_submenu(provider["name"], sub_menu)

    def _get_map_sources(self):
        with open(config.map_file) as json_file:
            return json.load(json_file)

    def _get_map_source_from_url(self, layer_url):
        map_sources = self._get_map_sources()
        for provider in map_sources["providers"]:
            for layer in provider["layers"]:
                if layer["url"] == layer_url:
                    return layer_url + provider["api_key"]

    def _on_layer_action(
            self, action: Gio.SimpleAction,
            data: GLib.Variant) -> None:
        layer_url = self._get_map_source_from_url(data.get_string())
        self._settings.set_string("layer-url", layer_url)
        self._shumate_map.set_map_source_from_layer_url(layer_url)
