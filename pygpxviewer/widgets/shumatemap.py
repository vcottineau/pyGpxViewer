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

from gi.repository import Gio, GObject, Gtk, Shumate

from pygpxviewer.widgets.elevationprofile import ElevationProfile


class ShumateMap(Shumate.SimpleMap):
    """Display an interactive map.

    Contains the following elements:
        * Zoom
        * License
        * Scale
        * Compass
    """

    def __init__(self, window):
        super().__init__()

        self._settings = window.settings
        self._gpx_helper = window.gpx_helper

        self._path_layer = None
        self._marker_layer = None
        self._marker = None

        self._set_map()
        self._set_marker()
        self._set_layers()

    @GObject.Property(type=GObject.GObject, flags=GObject.ParamFlags.READABLE)
    def path_layer(self):
        """Get the path layer property.

        @return: Path layer of the map
        @rtype: GObject.GObject
        """
        return self._path_layer

    @GObject.Property(type=GObject.GObject, flags=GObject.ParamFlags.READABLE)
    def marker_layer(self):
        """Get the marker layer property.

        @return: Marker layer of the map
        @rtype: GObject.GObject
        """
        return self._marker_layer

    def _set_map(self):
        layer_provider = self._settings.get_string("layer-provider")
        layer_url = self._settings.get_string("layer-url")
        self.set_map_source_from_layer_url(layer_provider, layer_url)

        self._settings.bind("zoom-level", self.get_viewport(), "zoom-level", Gio.SettingsBindFlags.GET_NO_CHANGES)
        self._settings.bind("latitude", self.get_viewport(), "latitude", Gio.SettingsBindFlags.GET_NO_CHANGES)
        self._settings.bind("longitude", self.get_viewport(), "longitude", Gio.SettingsBindFlags.GET_NO_CHANGES)

        bounds = self._gpx_helper.gpx.get_bounds()

        min_latitude = bounds.min_latitude
        min_longitude = bounds.min_longitude
        max_latitude = bounds.max_latitude
        max_longitude = bounds.max_longitude

        distance = self._gpx_helper.get_gpx_distance_between_locations(
            min_latitude, min_longitude,
            max_latitude, max_longitude) / 1000

        self.get_scale().set_unit(Shumate.Unit.METRIC)
        self.get_map().go_to_full(
            (min_latitude + max_latitude) / 2,
            (min_longitude + max_longitude) / 2,
            self._get_zoom_level(distance))

    def set_map_source_from_layer_url(self, layer_provider: str, layer_url: str) -> None:
        """Set the raster renderer provider of the map.

        @param layer_provider: Name of the layer provider
        @type layer_provider: str
        @param layer_url: Url of the layer provider
        @type layer_url: str
        """
        map_source = Shumate.RasterRenderer.new_from_url(layer_url)
        map_source.set_license(layer_provider)
        self.set_map_source(map_source)

    def _set_layers(self):
        self._path_layer = Shumate.PathLayer().new(self.get_viewport())
        self._marker_layer = Shumate.MarkerLayer().new(self.get_viewport())

        locations = self._gpx_helper.get_gpx_locations()
        for location in locations:
            self._path_layer.add_node(Shumate.Coordinate().new_full(location[1], location[0]))

        self._marker.set_location(locations[0][1], locations[0][0])
        self._marker_layer.add_marker(self._marker)

        self.add_overlay_layer(self._path_layer)
        self.add_overlay_layer(self._marker_layer)

    def _set_marker(self):
        self._marker = Shumate.Marker().new()

        marker_image = Gtk.Image().new_from_icon_name("media-record-symbolic")
        marker_image.set_pixel_size(15)

        context = marker_image.get_style_context()
        Gtk.StyleContext.add_class(context, "marker_image")

        self._marker.set_child(marker_image)

    @staticmethod
    def _get_zoom_level(distance: float) -> int:
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
        return zoom_level

    def on_mouse_move_event(self, widget: ElevationProfile, latitude: float, longitude: float) -> None:
        """Handle the mouse move event on the ElevationProfile widget.

        @param widget:
        @type widget: ElevationProfile
        @param latitude: Latitude where the mouse move event occurred
        @type latitude: float
        @param longitude: Longitude where the mouse move event occurred
        @type longitude: float
        """
        self._marker.set_location(latitude, longitude)
