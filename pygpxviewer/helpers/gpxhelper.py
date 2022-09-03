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
import math

import gpxpy
import gpxpy.gpx
from gmalthgtparser import HgtParser
from gpxpy import geo
from lxml import etree

from pygpxviewer import config, utils
from pygpxviewer.helpers.downloadhelper import DownloadHelper


class GpxHelper:
    def __init__(self, gpx_file):
        super().__init__()

        self.gpx = None
        self._gpx_file = gpx_file

    @property
    def gpx(self):
        if self._gpx is None:
            self._gpx = gpxpy.parse(open(self._gpx_file, 'r'))
        return self._gpx

    @gpx.setter
    def gpx(self, value):
        self._gpx = value

    def get_gpx_details(self):
        return (
            str(self._gpx_file),
            self.gpx.get_points_no(),
            self.gpx.length_3d() / 1000,
            self.gpx.get_uphill_downhill()[0],
            self.gpx.get_uphill_downhill()[1]
        )

    def get_gpx_locations(self):
        return [[point_data[0].longitude, point_data[0].latitude] for point_data in self.gpx.get_points_data()]

    def get_gpx_distances_and_elevations(self):
        distances = []
        elevations = []
        for point_data in self.gpx.get_points_data():
            distances.append(point_data[1] / 1000)
            elevations.append(point_data[0].elevation)
        return distances, elevations

    def get_gpx_lat_lng_from_distance(self, length, distance):
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
        return None, None

    def get_gpx_distance_between_locations(self, min_latitude, min_longitude, max_latitude, max_longitude):
        start_location = geo.Location(min_latitude, min_longitude)
        end_location = geo.Location(max_latitude, max_longitude)
        return start_location.distance_3d(end_location)

    def set_gpx_details(self, clean=True, headers=True, simplify=True, elevation=True):
        if clean:
            self._clean_gpx()

        if headers:
            self._set_gpx_headers()

        if simplify:
            self._gpx.simplify(5)

        if elevation:
            self._set_gpx_elevations()

        with open(self._gpx_file, 'w') as f:
            f.write(self._gpx.to_xml())

    def _clean_gpx(self):
        parser = etree.XMLParser(remove_blank_text=True)

        tree = etree.parse(self._gpx_file, parser)
        xslt = etree.fromstring(utils.get_resource_as_string("/xslt/stylesheet.xslt"))

        tree = tree.xslt(xslt)
        root = tree.getroot()

        # Single occurrence
        for node_name in [".//metadata", ".//type", ".//number", ".//cmt"]:
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
        self.gpx = None

    def _set_gpx_headers(self):
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

        for point_data in self._gpx.get_points_data():
            elevation = self._get_elevation(point_data[0].latitude, point_data[0].longitude)
            if elevation is not None:
                point_data[0].elevation = elevation

    def _get_hgt_file_name(self, latitude, longitude):
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
            urls = self._get_hgt_file_urls(missing_hgt_files)
            download_helper = DownloadHelper(urls)
            download_helper.fetch_urls()

    def _get_hgt_file_urls(self, hgt_files):
        with open(config.dem_file) as json_file:
            json_data = json.load(json_file)

        urls = {}
        for fragment in json_data:
            for fragment_file in fragment["files"]:
                if fragment_file in hgt_files:
                    urls[fragment["name"]] = {
                        "link": fragment["link"], "size": fragment["size"]
                    }
        return urls

    def _get_elevation(self, latitude, longitude):
        hgt_file_name = self._get_hgt_file_name(latitude, longitude)
        hgt_file_path = config.dem_path.joinpath(hgt_file_name)

        if hgt_file_path.is_file():
            with HgtParser(hgt_file_path) as parser:
                _, _, elevation = parser.get_elevation((latitude, longitude))
                return elevation
        return None
