from lxml import etree
import sqlite3


import gpxpy
import gpxpy.gpx
from gpxpy.geo import Location
import srtm


from pygpxviewer.utils import get_resource_as_string
from config import HOME_DATA_FOLDER


class SQLiteHelper():
    def __init__(self):
        self.db_file = HOME_DATA_FOLDER.joinpath("pygpxviewer.db")
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
        conn, c = self.get_conn()
        # ToDo Update Record
        # ...
        self.close_conn(conn, c)

    def get_records(self):
        sql = "SELECT * FROM gpx"
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


class GpxHelper:
    def __init__(self):
        self.gpx_file = None
        self.gpx = None

    def set_gpx(self, gpx_file):
        self.gpx_file = gpx_file
        self.gpx = gpxpy.parse(open(gpx_file, 'r'))

    def get_gpx_points_nb(self):
        return self.gpx.get_points_no()

    def get_gpx_length(self):
        return self.gpx.length_3d() / 1000

    def get_gpx_up_hill(self):
        return self.gpx.get_uphill_downhill()[0]

    def get_gpx_down_hill(self):
        return self.gpx.get_uphill_downhill()[1]

    def get_gpx_bounds(self):
        return self.gpx.get_bounds()

    def get_gpx_elevation_extremes(self):
        return self.gpx.get_elevation_extremes()

    def get_gpx_distance_between_locations(self, min_latitude, min_longitude, max_latitude, max_longitude):
        start_location = Location(min_latitude, min_longitude)
        end_location = Location(max_latitude, max_longitude)
        return start_location.distance_3d(end_location)

    def get_gpx_locations(self):
        return [[point_data[0].longitude, point_data[0].latitude] for point_data in self.gpx.get_points_data()]

    def get_gpx_distances_and_elevations(self):
        distances = []
        elevations = []
        for point_data in self.gpx.get_points_data():
            distances.append(point_data[1]/1000)
            elevations.append(point_data[0].elevation)
        return distances, elevations

    def set_gpx_info(self):
        parser = etree.XMLParser(remove_blank_text=True)

        tree = etree.parse(self.gpx_file, parser)
        xslt = etree.fromstring(get_resource_as_string("/xslt/stylesheet.xslt"))

        tree = tree.xslt(xslt)
        root = tree.getroot()

        # Single occurrence
        for node_name in [".//extensions", ".//metadata", ".//desc", ".//type", ".//number", ".//cmt"]:
            node = root.find(node_name, namespaces=root.nsmap)
            if node is not None:
                node.getparent().remove(node)

        # Multiple occurrences
        for node_name in [".//name", ".//wpt", ".//time"]:
            nodes = [node for node in root.iterfind(node_name, namespaces=root.nsmap)]
            if nodes is not None:
                for node in nodes:
                    node.getparent().remove(node)

        tree.write(self.gpx_file, pretty_print=True)

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


gpx_helper = GpxHelper()
