import gpxpy
import gpxpy.gpx


def get_gpx_info(gpx_file):
    gpx = gpxpy.parse(open(gpx_file, 'r'))
    return gpx.length_3d() / 1000, gpx.get_uphill_downhill()[0], gpx.get_uphill_downhill()[1]
