from lxml import etree


import gpxpy
import gpxpy.gpx
import srtm


from pygpxviewer.utils import get_resource_as_string



class GpxHelper:
    @staticmethod
    def get_gpx(gpx_file):
        return gpxpy.parse(open(gpx_file, 'r'))

    def get_gpx_points_nb(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return gpx.get_points_no()

    def get_gpx_length(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return gpx.length_3d() / 1000

    def get_gpx_up_hill(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return gpx.get_uphill_downhill()[0]

    def get_gpx_down_hill(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return gpx.get_uphill_downhill()[1]

    def get_gpx_bounds(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return gpx.get_bounds()

    def get_gpx_elevation_extremes(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return gpx.get_elevation_extremes()

    def get_gpx_locations(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        return [[point_data[0].longitude, point_data[0].latitude] for point_data in gpx.get_points_data()]

    def get_gpx_distances_and_elevations(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)
        distances = []
        elevations = []
        for point_data in gpx.get_points_data():
            distances.append(point_data[1])
            elevations.append(point_data[0].elevation)
        return distances, elevations

    def set_gpx_info(self, gpx_file):
        gpx = GpxHelper.get_gpx(gpx_file)

        parser = etree.XMLParser(remove_blank_text=True)

        tree = etree.parse(gpx_file, parser)
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

        tree.write(gpx_file, pretty_print=True)
        
        gpx.schema_locations = [
            "http://www.topografix.com/GPX/1/1",
            "http://www.topografix.com/GPX/1/1/gpx.xsd"
        ]
        gpx.nsmap['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        gpx.version = "1.1"
        gpx.creator = "pygpxviewer"

        # Simplify
        gpx.simplify(5)

        # Elevation
        elevation_data = srtm.get_data()
        elevation_data.add_elevations(gpx, smooth=True)

        with open(gpx_file, 'w') as f:
            f.write(gpx.to_xml())


gpx_helper = GpxHelper()
