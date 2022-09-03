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

import matplotlib.pyplot as plt
from gi.repository import GObject, Gtk
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_gtk4 import NavigationToolbar2GTK4
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg
from matplotlib.figure import Figure

from pygpxviewer import utils


class ElevationProfile(Gtk.Box):
    __gsignals__ = {
        'on-mouse-move-event': (GObject.SIGNAL_RUN_FIRST, None,
                                (float, float,))
    }

    def __init__(self, window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._gpx_helper = window.gpx_helper

        if utils.is_dark_theme_enable():
            plt.style.use('dark_background')

        canvas = FigureCanvasGTK4Agg(self._get_figure())
        toolbar = NavigationToolbar2GTK4(canvas, self)

        self.append(canvas)
        self.append(toolbar)

    def _get_figure(self) -> Figure:
        length = self._gpx_helper.gpx.length_3d() / 1000
        min_elev, max_elev = self._gpx_helper.gpx.get_elevation_extremes()
        distances, elevations = self._gpx_helper.get_gpx_distances_and_elevations()

        min_elev = round(min_elev)
        max_elev = round(max_elev)
        mean_elev = round(
            sum(elevations)
            / len(elevations))

        figure = Figure(tight_layout=True)
        figure.canvas.mpl_connect('motion_notify_event', self._on_motion_notify_event)

        ax = figure.add_subplot()
        ax.plot(distances, elevations)
        ax.plot([0, length], [max_elev, max_elev], '--r', label='max: ' + str(max_elev) + ' m')
        ax.plot([0, length], [mean_elev, mean_elev], '--y', label='ave: ' + str(mean_elev) + ' m')
        ax.plot([0, length], [min_elev, min_elev], '--g', label='min: ' + str(min_elev) + ' m')
        ax.fill_between(distances, elevations, min_elev, alpha=0.1)
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Elevation (m)")
        ax.grid()
        ax.legend()

        return figure

    def _on_motion_notify_event(self, event: MouseEvent) -> None:
        if event.inaxes:
            length = self._gpx_helper.gpx.length_3d() / 1000
            result = self._gpx_helper.get_gpx_lat_lng_from_distance(length, event.xdata)
            if result:
                self.emit("on-mouse-move-event", result[0], result[1])
