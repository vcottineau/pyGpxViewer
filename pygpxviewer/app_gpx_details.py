import os


from gi.repository import Gio, Gtk, Gdk, GLib
from gi.repository.WebKit2 import WebView
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
from matplotlib.figure import Figure


from pygpxviewer.helper import get_gpx_info, get_gpx_elevation_extremes, get_gpx_points_data


@Gtk.Template(resource_path="/fr/vcottineau/pygpxviewer/ui/app_gpx_details.glade")
class AppGpxDetails(Gtk.Window):
    __gtype_name__ = "app_gpx_details"

    app_gpx_details_label_points = Gtk.Template.Child()
    app_gpx_details_label_length = Gtk.Template.Child()
    app_gpx_details_label_up_hill = Gtk.Template.Child()
    app_gpx_details_label_down_hill = Gtk.Template.Child()
    app_gpx_details_scrolled_window = Gtk.Template.Child()
    app_gpx_details_webkit_webview = Gtk.Template.Child()

    def __init__(self, gpx_file):
        super().__init__()

        self.gpx_file = gpx_file
        self.set_title(os.path.basename(self.gpx_file))

        min_elev, max_elev = get_gpx_elevation_extremes(self.gpx_file)
        points, length, up_hill, down_hill = get_gpx_info(self.gpx_file)
        points_data = get_gpx_points_data(self.gpx_file)

        self.app_gpx_details_label_points.set_text(str(round(points)))
        self.app_gpx_details_label_length.set_text(str(round(length)))
        self.app_gpx_details_label_up_hill.set_text(str(round(up_hill)))
        self.app_gpx_details_label_down_hill.set_text(str(round(down_hill)))

        self.app_gpx_details_webkit_webview.load_uri("file://" + "/home/vcottineau/Documents/Informatique/Projets/GitHub/Python/pyGpxViewer/pygpxviewer/map.html")

        distances = []
        elevations = []
        for point_data in points_data:
            distances.append(point_data[1]/1000)
            elevations.append(point_data[0].elevation)

        min_elev = round(min_elev)
        max_elev = round(max_elev)
        mean_elev = round((sum(elevations)/len(elevations)))

        fig = Figure()
        #fig = Figure(figsize=(5, 4), dpi=100)

        ax = fig.add_subplot()
        ax.plot(distances, elevations)
        ax.plot([0, length],[min_elev, min_elev],'--g',label='min: '+str(min_elev)+' m')
        ax.plot([0, length],[max_elev, max_elev],'--r',label='max: '+str(max_elev)+' m')
        ax.plot([0, length],[mean_elev, mean_elev],'--y',label='ave: '+str(mean_elev)+' m')
        ax.fill_between(distances,elevations,min_elev,alpha=0.1)        
        ax.grid()
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Elevation (m)")
        ax.legend(fontsize='small')

        canvas = FigureCanvasGTK3Agg(fig)
        #canvas.set_size_request(800, 600)
        self.app_gpx_details_scrolled_window.add(canvas)
