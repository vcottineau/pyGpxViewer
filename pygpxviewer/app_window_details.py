import os


from matplotlib.backends.backend_gtk4 import (NavigationToolbar2GTK4 as NavigationToolbar)
from matplotlib.backends.backend_gtk4agg import (FigureCanvasGTK4Agg as FigureCanvas)
from matplotlib.figure import Figure


from gi.repository import Gio, Gtk, Shumate


from pygpxviewer.helpers import gpx_helper


class AppWindowDetails(Gtk.Window):
    __gtype_name__ = "app_window_details"

    def __init__(self, gpx_file):
        super().__init__()

        gpx_helper.set_gpx(gpx_file)

        self.set_title(os.path.basename(gpx_file))
        self.settings = Gio.Settings.new("com.github.pygpxviewer.app.window.details")

        self.settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-fullscreen", self, "fullscreened", Gio.SettingsBindFlags.DEFAULT)        

        gpx_info = self.get_gpx_info()
        shumate_map = self.get_shumate_map()
        canvas = self.get_matplotlib_canvas(gpx_file)
        
        gpx_map_and_elevation_profile = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        gpx_map_and_elevation_profile.set_homogeneous(True)
        gpx_map_and_elevation_profile.append(shumate_map)
        gpx_map_and_elevation_profile.append(canvas)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.append(gpx_info)
        box.append(gpx_map_and_elevation_profile)

        self.set_child(box)

    def get_gpx_info(self):
        box_row_1 = Gtk.Box()
        box_row_1.set_homogeneous(True)
        box_row_1.append(Gtk.Label.new("Points (nb)"))
        box_row_1.append(Gtk.Label.new(str(round(gpx_helper.get_gpx_points_nb()))))
        box_row_1.append(Gtk.Label.new("UpHill (m)"))
        box_row_1.append(Gtk.Label.new(str(round(gpx_helper.get_gpx_up_hill()))))

        box_row_2 = Gtk.Box()
        box_row_2.set_homogeneous(True)
        box_row_2.append(Gtk.Label.new("Length (km)"))
        box_row_2.append(Gtk.Label.new(str(round(gpx_helper.get_gpx_length()))))
        box_row_2.append(Gtk.Label.new("DownHill (m)"))
        box_row_2.append(Gtk.Label.new(str(round(gpx_helper.get_gpx_down_hill()))))

        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_box.append(box_row_1)
        list_box.append(box_row_2)

        return list_box

    def get_shumate_map(self):
        shumate_map = Shumate.SimpleMap()
        shumate_map.get_scale().set_unit(Shumate.Unit.METRIC)

        bounds = gpx_helper.get_gpx_bounds()
        locations = gpx_helper.get_gpx_locations()

        shumate_map_source = Shumate.RasterRenderer.new_from_url("https://tile.openstreetmap.org/{z}/{x}/{y}.png")
        shumate_map.set_map_source(shumate_map_source)

        viewport = shumate_map.get_viewport()
        path_layer = Shumate.PathLayer.new(viewport)

        self.settings.bind("zoom-level", viewport, "zoom-level", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("latitude", viewport, "latitude", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("longitude", viewport, "longitude", Gio.SettingsBindFlags.DEFAULT)

        for location in locations:
            path_layer.add_node(Shumate.Coordinate.new_full(location[1], location[0]))
        shumate_map.add_overlay_layer(path_layer)

        min_latitude = bounds.min_latitude
        min_longitude = bounds.min_longitude
        max_latitude = bounds.max_latitude
        max_longitude = bounds.max_longitude

        distance = gpx_helper.get_gpx_distance_between_locations(min_latitude, min_longitude, max_latitude, max_longitude) / 1000

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
            zoom_level
        )

        return shumate_map

    def get_matplotlib_canvas(self, gpx_file):
        length = gpx_helper.get_gpx_length()
        min_elev, max_elev = gpx_helper.get_gpx_elevation_extremes()
        distances, elevations = gpx_helper.get_gpx_distances_and_elevations()

        min_elev = round(min_elev)
        max_elev = round(max_elev)
        mean_elev = round((sum(elevations)/len(elevations)))

        figure = Figure(tight_layout=True)

        ax = figure.add_subplot()
        ax.grid()
        ax.plot(distances, elevations)
        ax.plot([0, length], [max_elev, max_elev], '--r', label='max: '+str(max_elev)+' m')
        ax.plot([0, length], [mean_elev, mean_elev], '--y', label='ave: '+str(mean_elev)+' m')
        ax.plot([0, length], [min_elev, min_elev], '--g', label='min: '+str(min_elev)+' m')
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
