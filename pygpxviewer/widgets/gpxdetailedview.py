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
from pathlib import Path

import matplotlib.pyplot as plt
from gi.repository import Adw, Gio, GLib, Gtk, Shumate
from matplotlib.backends.backend_gtk4 import \
    NavigationToolbar2GTK4 as NavigationToolbar
from matplotlib.backends.backend_gtk4agg import \
    FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure

from pygpxviewer import utils
from pygpxviewer.helpers import GpxHelper


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
        self._map_sources = Path.home().joinpath(".config", "pygpxviewer", "sources.json")

        self.set_title(os.path.basename(self._path))
        self._settings = Gio.Settings.new("com.github.pygpxviewer.app.window.detailed")
        self._gpx_helper = GpxHelper(self._path)

        self._shumate_map = self._get_shumate_map()

        self._setup_actions()
        self._setup_view()
        self._setup_layers()

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

        self._box_container.append(self._shumate_map)
        if self._gpx_helper.gpx.has_elevations():
            self._box_container.append(self.get_matplotlib_box())

    def _setup_layers(self):
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
        with open(self._map_sources) as json_file:
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
        map_source = self._get_map_source_from_url(data.get_string())
        self._set_map_source(map_source)

    def _set_map_source(self, url):
        self._settings.set_string("layer-url", url)
        map_source = Shumate.RasterRenderer.new_from_url(url)
        self._shumate_map.set_map_source(map_source)

    def _get_shumate_map(self):
        shumate_map = Shumate.SimpleMap()
        shumate_map.get_scale().set_unit(Shumate.Unit.METRIC)

        bounds = self._gpx_helper.gpx.get_bounds()
        locations = self._gpx_helper.get_locations()

        layer_url = self._settings.get_string("layer-url")
        map_source = Shumate.RasterRenderer.new_from_url(layer_url)
        shumate_map.set_map_source(map_source)

        viewport = shumate_map.get_viewport()
        path_layer = Shumate.PathLayer.new(viewport)

        self._settings.bind("zoom-level", viewport, "zoom-level", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("latitude", viewport, "latitude", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("longitude", viewport, "longitude", Gio.SettingsBindFlags.DEFAULT)

        for location in locations:
            path_layer.add_node(Shumate.Coordinate.new_full(location[1], location[0]))
            shumate_map.add_overlay_layer(path_layer)

        min_latitude = bounds.min_latitude
        min_longitude = bounds.min_longitude
        max_latitude = bounds.max_latitude
        max_longitude = bounds.max_longitude

        distance = self._gpx_helper.get_distance_between_locations(
            min_latitude, min_longitude,
            max_latitude, max_longitude) / 1000

        zoom_level = 5
        if distance <= 5:
            zoom_level = 14
        elif distance <= 10:
            zoom_level = 12
        elif distance <= 25:
            zoom_level = 11
        elif distance <= 50:
            zoom_level = 10
        elif distance <= 100:
            zoom_level = 9
        elif distance <= 500:
            zoom_level = 7

        shumate_map.get_map().go_to_full(
            (min_latitude + max_latitude) / 2,
            (min_longitude + max_longitude) / 2,
            zoom_level)

        return shumate_map

    def get_matplotlib_box(self):
        length = self._gpx_helper.gpx.length_3d() / 1000
        min_elev, max_elev = self._gpx_helper.gpx.get_elevation_extremes()
        distances, elevations = self._gpx_helper.get_distances_and_elevations()

        min_elev = round(min_elev)
        max_elev = round(max_elev)
        mean_elev = round(
            sum(elevations)
            / len(elevations))

        if utils.get_dark_theme_enable():
            plt.style.use('dark_background')

        figure = Figure(tight_layout=True)

        ax = figure.add_subplot()
        ax.grid()
        ax.plot(distances, elevations)
        ax.plot([0, length], [max_elev, max_elev], '--r', label='max: ' + str(max_elev) + ' m')
        ax.plot([0, length], [mean_elev, mean_elev], '--y', label='ave: ' + str(mean_elev) + ' m')
        ax.plot([0, length], [min_elev, min_elev], '--g', label='min: ' + str(min_elev) + ' m')
        ax.fill_between(distances, elevations, min_elev, alpha=0.1)
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Elevation (m)")
        ax.legend()

        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.append(canvas)
        box.append(toolbar)

        return box
