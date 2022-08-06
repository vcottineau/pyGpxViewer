from lxml import etree


import gpxpy
import gpxpy.gpx
import srtm


def get_gpx_info(gpx_file):
    gpx = gpxpy.parse(open(gpx_file, 'r'))
    return gpx.length_3d() / 1000, gpx.get_uphill_downhill()[0], gpx.get_uphill_downhill()[1]


def set_gpx_info(gpx_file):
    parser = etree.XMLParser(remove_blank_text=True)

    tree = etree.parse(gpx_file, parser)
    xslt = etree.parse("pygpxviewer/clean_xml.xslt")

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

    gpx = gpxpy.parse(open(gpx_file, 'r'))

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
