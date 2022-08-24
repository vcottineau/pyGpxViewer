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

import sqlite3
from pathlib import Path

import gpxpy
import srtm
from gpxpy.geo import Location
from lxml import etree

from pygpxviewer.utils import get_resource_as_string


class SQLiteHelper:
    def __init__(self):
        db_path = Path.home().joinpath(".cache", "pygpxviewer")
        db_path.mkdir(parents=True, exist_ok=True)

        self.db_file = db_path.joinpath("pygpxviewer.db")

        sql = """
            CREATE TABLE IF NOT EXISTS gpx (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                points INTEGER,
                length REAL,
                up_hill REAL,
                down_hill REAL
            );
        """
        conn, c = self.get_conn()
        c.execute(sql)
        self.close_conn(conn, c)

    def clear_records(self):
        sql = "DELETE from gpx"
        conn, c = self.get_conn()
        c.execute(sql)
        conn.commit()
        self.close_conn(conn, c)

    def add_record(self, record):
        sql = """
            INSERT INTO gpx(path,points,length,up_hill,down_hill)
                VALUES(?,?,?,?,?)
        """
        conn, c = self.get_conn()
        c.execute(sql, record)
        conn.commit()
        self.close_conn(conn, c)

    def update_record(self, record):
        sql = f"""
            UPDATE gpx
            SET
                points = {record[1]},
                length = {record[2]},
                up_hill = {record[3]},
                down_hill = {record[4]}
            WHERE
                path = '{record[0]}';
        """
        conn, c = self.get_conn()
        c.execute(sql)
        conn.commit()
        self.close_conn(conn, c)

    def get_records(self):
        sql = "SELECT * FROM gpx"
        conn, c = self.get_conn()
        c.execute(sql)
        records = c.fetchall()
        self.close_conn(conn, c)
        return records

    def search_records(self, search_entry):
        sql = f"SELECT * FROM gpx WHERE gpx.path LIKE '%{search_entry}%'"
        conn, c = self.get_conn()
        c.execute(sql)
        records = c.fetchall()
        self.close_conn(conn, c)
        return records

    def get_conn(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        return conn, c

    def close_conn(self, conn, c):
        c.close()
        conn.close()


sqlite_helper = SQLiteHelper()


class GpxHelper():
    def __init__(self, gpx_file):
        self.gpx_file = gpx_file
        self.gpx = self._get_gpx()

    def _get_gpx(self):
        return gpxpy.parse(open(self.gpx_file, 'r'))

    def get_gpx_details(self):
        return (
            str(self.gpx_file),
            self.gpx.get_points_no(),
            self.gpx.length_3d() / 1000,
            self.gpx.get_uphill_downhill()[0],
            self.gpx.get_uphill_downhill()[1]
        )

    def get_locations(self):
        return [[point_data[0].longitude, point_data[0].latitude] for point_data in self.gpx.get_points_data()]

    def get_distances_and_elevations(self):
        distances = []
        elevations = []
        for point_data in self.gpx.get_points_data():
            distances.append(
                point_data[1]
                / 1000)
            elevations.append(point_data[0].elevation)
        return distances, elevations

    def get_distance_between_locations(self, min_latitude, min_longitude, max_latitude, max_longitude):
        start_location = Location(min_latitude, min_longitude)
        end_location = Location(max_latitude, max_longitude)
        return start_location.distance_3d(end_location)

    def set_gpx_info(self):
        parser = etree.XMLParser(remove_blank_text=True)

        tree = etree.parse(self.gpx_file, parser)
        xslt = etree.fromstring(get_resource_as_string("/xslt/stylesheet.xslt"))

        tree = tree.xslt(xslt)
        root = tree.getroot()

        # Single occurrence
        for node_name in [".//metadata", ".//type", ".//number", ".//cmt"]:
            node = root.find(node_name, namespaces=root.nsmap)
            if node is not None:
                node.getparent().remove(node)

        # Multiple occurrences
        for node_name in [".//extensions", ".//desc", ".//name", ".//wpt", ".//time"]:
            nodes = [node for node in root.iterfind(node_name, namespaces=root.nsmap)]
            if nodes is not None:
                for node in nodes:
                    node.getparent().remove(node)

        tree.write(self.gpx_file, pretty_print=True)

        self.gpx = self._get_gpx()
        self.gpx.schema_locations = [
            "http://www.topografix.com/GPX/1/1",
            "http://www.topografix.com/GPX/1/1/gpx.xsd"
        ]
        self.gpx.nsmap['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        self.gpx.version = "1.1"
        self.gpx.creator = "pygpxviewer"

        # Simplify
        self.gpx.simplify(5)

        # Elevation
        elevation_data = srtm.get_data()
        elevation_data.add_elevations(self.gpx, smooth=True)

        with open(self.gpx_file, 'w') as f:
            f.write(self.gpx.to_xml())
