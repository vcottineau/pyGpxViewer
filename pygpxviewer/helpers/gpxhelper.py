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
import math
import os
from typing import Optional

import gpxpy
import gpxpy.gpx
from gmalthgtparser import HgtParser
from gpxpy import geo
from lxml import etree

from pygpxviewer import config, utils
from pygpxviewer.helpers.downloadhelper import DownloadHelper
from pygpxviewer.helpers.sqlitehelper import SQLiteHelper


class GpxHelper:
    """Helper to handle gpx file content."""

    def __init__(self, gpx_file):
        super().__init__()

        self._gpx: Optional[gpxpy.gpx.GPX] = None
        self._gpx_file = gpx_file
        self._update = False

    @property
    def gpx(self) -> gpxpy.gpx.GPX:
        """Get the gpx object property.

        :returns: Gpx object
        :rtype: gpxpy.gpx.GPX
        """
        if self._gpx is None or self._update:
            self._gpx = gpxpy.parse(open(self._gpx_file, 'r'))
            self._update = False
        return self._gpx

    @gpx.setter
    def gpx(self, value: Optional[gpxpy.gpx.GPX]) -> None:
        """Set the gpx object property.

        :param value: Gpx object
        :type value: gpxpy.gpx.GPX
        """
        self._gpx = value

    def get_gpx_details(self) -> tuple:
        """Get main properties of a gpx file.

        Main properties are:
            * path: File system path
            * mode: Traveling mode
            * points: Number of track points
            * length: Total distance in km
            * up_hill: Total ascent in m
            * down_hill: Total descent in m

        :returns: Main gpx properties
        :rtype: tuple
        """
        return (
            str(self._gpx_file),
            self.get_gpx_mode(),
            self.gpx.get_points_no(),
            self.gpx.length_3d() / 1000,
            self.gpx.get_uphill_downhill()[0],
            self.gpx.get_uphill_downhill()[1]
        )

    def get_gpx_locations(self) -> list[list[float]]:
        """Get all the locations of a gpx file.

        :returns: List of all the locations
        :rtype: list[list[float]
        """
        return [[point_data[0].latitude, point_data[0].longitude] for point_data in self.gpx.get_points_data()]

    def get_gpx_distances_and_elevations(self) -> tuple:
        """Get the distance and elevation values for all the locations in a gpx file.

        :returns: Distance and elevation values
        :rtype: tuple
        """
        distances = []
        elevations = []
        for point_data in self.gpx.get_points_data():
            distances.append(point_data[1] / 1000)
            elevations.append(point_data[0].elevation)
        return distances, elevations

    def get_gpx_lat_lng_from_distance(self, length: float, distance: float) -> Optional[tuple[float, float]]:
        """Get the closest location based on the distance from the first point.

        Delta variable is used for rendering purposes

        :param length: Length of the gpx file in km
        :type length: float
        :param distance: Distance from the first point in km
        :type distance: float
        :returns: Location latitude and longitude
        :rtype: tuple[float, float]
        """
        delta = 1.00
        if length <= 500:
            delta = 0.05
        elif length <= 800:
            delta = 0.10
        elif length <= 1000:
            delta = 0.25
        elif length <= 10000:
            delta = 0.50

        for point_data in self.gpx.get_points_data():
            if abs(point_data[1] / 1000 - distance) <= delta:
                return point_data[0].latitude, point_data[0].longitude
        return None

    def get_gpx_distance_between_locations(self, min_latitude: float, min_longitude: float, max_latitude: float,
                                           max_longitude: float) -> Optional[float]:
        """Get the distance between two locations in m.

        :param min_latitude:
        :type min_latitude: float
        :param min_longitude:
        :type min_longitude: float
        :param max_latitude:
        :type max_latitude: float
        :param max_longitude:
        :type max_longitude: float
        :returns: Distance in m
        :rtype: float
        """
        start_location = geo.Location(min_latitude, min_longitude)
        end_location = geo.Location(max_latitude, max_longitude)
        return start_location.distance_3d(end_location)

    def set_gpx_details(self, clean_headers, clean_attributes, elevation, simplify):
        """Set many attributes to a gpx file.

        :param clean_attributes: Remove specific unused nodes
        :type clean_attributes: bool
        :param clean_headers: Add xsd schemas
        :type clean_headers: bool
        :param simplify: Remove track points to reduce the size
        :type simplify: bool
        :param elevation: Add missing elevation data
        :type elevation: bool
        """
        if clean_attributes:
            self._clean_attributes()

        if clean_headers:
            self._clean_headers()

        if simplify:
            self.gpx.simplify(5)

        if elevation:
            self._set_gpx_elevations()

        self._set_attributes()
        self._save_gpx()

    def get_gpx_mode(self) -> int:
        """Get mode attributes of a gpx file."""
        mode = self.gpx.keywords
        if mode not in ["0", "1"]:
            mode = "2"

        return int(mode)

    def set_gpx_mode(self, mode):
        """Set mode attributes to a gpx file.

        :param mode: Traveling mode
        :type mode: str
        """
        self.gpx.keywords = str(mode)
        self._save_gpx()

    def _save_gpx(self):
        gpx_to_xml = self.gpx.to_xml()
        with open(self._gpx_file, 'w') as f:
            f.write(gpx_to_xml)

    def _clean_attributes(self) -> None:
        parser = etree.XMLParser(remove_blank_text=True)

        tree = etree.parse(self._gpx_file, parser)
        xslt = etree.fromstring(utils.get_resource("/xslt/stylesheet.xslt", decode=True))

        tree = tree.xslt(xslt)
        root = tree.getroot()

        # Single occurrence
        for node_name in [".//type", ".//number", ".//cmt"]:
            node = root.find(node_name, namespaces=root.nsmap)
            if node is not None:
                node.getparent().remove(node)

        # Multiple occurrences
        for node_name in [".//extensions", ".//number", ".//desc", ".//name", ".//wpt", ".//time"]:
            nodes = [node for node in root.iterfind(node_name, namespaces=root.nsmap)]
            if nodes is not None:
                for node in nodes:
                    node.getparent().remove(node)

        tree.write(self._gpx_file, pretty_print=True)
        self._update = True

    def _set_attributes(self) -> None:
        _, _, _, length, up_hill, down_hill = self.get_gpx_details()

        self.gpx.name = os.path.basename(self._gpx_file)
        self.gpx.description = f"Length={round(length)}km, UpHill={round(up_hill)}m, DownHill={round(down_hill)}m"
        self.gpx.bounds = self.gpx.get_bounds()

    def _clean_headers(self) -> None:
        self.gpx.schema_locations = [
            "http://www.topografix.com/GPX/1/1",
            "http://www.topografix.com/GPX/1/1/gpx.xsd"
        ]
        self.gpx.nsmap['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        self.gpx.version = "1.1"
        self.gpx.creator = "pygpxviewer"

    def _set_gpx_elevations(self):
        hgt_files = set()
        for point_data in self.gpx.get_points_data():
            hgt_files.add(self._get_hgt_file_name(point_data[0].latitude, point_data[0].longitude))
        self._fetch_hgt_files(hgt_files)

        for point_data in self.gpx.get_points_data():
            elevation = self._get_elevation(point_data[0].latitude, point_data[0].longitude)
            if elevation is not None:
                point_data[0].elevation = elevation

    def _get_hgt_file_name(self, latitude: float, longitude: float) -> str:
        if latitude >= 0:
            north_south = 'N'
        else:
            north_south = 'S'

        if longitude >= 0:
            east_west = 'E'
        else:
            east_west = 'W'

        file_name = '%s%s%s%s.hgt' % (north_south, str(int(abs(math.floor(latitude)))).zfill(2),
                                      east_west, str(int(abs(math.floor(longitude)))).zfill(3))

        return file_name

    def _fetch_hgt_files(self, hgt_files):
        missing_hgt_files = []
        for hgt_file in hgt_files:
            if not config.dem_path.joinpath(hgt_file).is_file():
                missing_hgt_files.append(hgt_file)

        if missing_hgt_files:
            sqlite_helper = SQLiteHelper()
            records = sqlite_helper.search_dem_record(missing_hgt_files)

            urls = []
            for record in records:
                urls.append(
                    {"folder": record[0], "size": int(record[1]), "link": record[2]}
                )

            download_helper = DownloadHelper(urls)
            download_helper.fetch_urls()

    def _get_elevation(self, latitude: float, longitude: float) -> Optional[int]:
        hgt_file_name = self._get_hgt_file_name(latitude, longitude)
        hgt_file_path = config.dem_path.joinpath(hgt_file_name)

        if hgt_file_path.is_file():
            with HgtParser(hgt_file_path) as parser:
                _, _, elevation = parser.get_elevation((latitude, longitude))
                return elevation
        return None
