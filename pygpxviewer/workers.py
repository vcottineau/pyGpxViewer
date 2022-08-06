import threading


from gi.repository import GObject


from pygpxviewer.helper import set_gpx_info


class WorkerGpxThread(threading.Thread):
    def __init__(self, gpx_files, callback):
        threading.Thread.__init__(self)
        self.gpx_files = gpx_files
        self.callback = callback

    def run(self):
        for gpx_file in self.gpx_files:
            set_gpx_info(str(gpx_file))
        GObject.idle_add(self.callback)
