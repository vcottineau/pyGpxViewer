import os


from gi.repository import Gio, Gtk, Gdk, GLib
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
from matplotlib.figure import Figure


from pygpxviewer.gpx_helper import gpx_helper
from pygpxviewer.app_webview import AppWebView


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/app_window_details.glade")
class AppWindowDetails(Gtk.Window):
    __gtype_name__ = "app_window_details"

    app_window_details_label_points = Gtk.Template.Child()
    app_window_details_label_length = Gtk.Template.Child()
    app_window_details_label_up_hill = Gtk.Template.Child()
    app_window_details_label_down_hill = Gtk.Template.Child()
    app_window_details_webview = Gtk.Template.Child()
    app_window_details_matplotlib = Gtk.Template.Child()

    def __init__(self, gpx_file):
        super().__init__()

        self.set_title(os.path.basename(gpx_file))

        self.app_window_details_label_points.set_text(str(round(gpx_helper.get_gpx_points_nb(gpx_file))))
        self.app_window_details_label_length.set_text(str(round(gpx_helper.get_gpx_length(gpx_file))))
        self.app_window_details_label_up_hill.set_text(str(round(gpx_helper.get_gpx_up_hill(gpx_file))))
        self.app_window_details_label_down_hill.set_text(str(round(gpx_helper.get_gpx_down_hill(gpx_file))))

        self.bounds = gpx_helper.get_gpx_bounds(gpx_file)
        self.locations = gpx_helper.get_gpx_locations(gpx_file)
        self.webview = AppWebView(self.bounds, self.locations)
        self.app_window_details_webview.add(self.webview)

        figure = self.get_matplotlib_figure(gpx_file)
        canvas = FigureCanvasGTK3Agg(figure)
        self.app_window_details_matplotlib.add(canvas)

    def get_matplotlib_figure(self, gpx_file):
        length = gpx_helper.get_gpx_length(gpx_file)
        min_elev, max_elev = gpx_helper.get_gpx_elevation_extremes(gpx_file)
        distances, elevations = gpx_helper.get_gpx_distances_and_elevations(gpx_file)

        min_elev = round(min_elev)
        max_elev = round(max_elev)
        mean_elev = round((sum(elevations)/len(elevations)))

        figure = Figure()
        figure.tight_layout()

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

        return figure
