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
import pathlib
import threading
from typing import Callable, Tuple

from gi.repository import GObject, Gtk

from pygpxviewer.helpers.gpxhelper import GpxHelper
from pygpxviewer.helpers.sqlitehelper import SQLiteHelper


class WorkerUpdateRecords(threading.Thread):
    def __init__(self, folder_path: str, callback: Callable[[], None]):
        threading.Thread.__init__(self)
        self.folder_path = folder_path
        self.callback = callback

    def run(self):
        sqlite_helper = SQLiteHelper()
        sqlite_helper.clear_records()

        records = []
        for gpx_file in pathlib.Path(self.folder_path).glob("**/*.gpx"):
            gpx_helper = GpxHelper(gpx_file)
            records.append(gpx_helper.get_gpx_details())

        sqlite_helper.add_records(records)
        GObject.idle_add(self.callback)


class WorkerUpdateRecord(threading.Thread):
    def __init__(self, selected_item: Gtk.ListItem, callback: Callable[[Gtk.ListItem, Tuple], None]):
        threading.Thread.__init__(self)
        self.selected_item = selected_item
        self.callback = callback

    def run(self):
        sqlite_helper = SQLiteHelper()
        gpx_helper = GpxHelper(self.selected_item.path)

        gpx_helper.set_gpx_details()
        record = gpx_helper.get_gpx_details()

        sqlite_helper.update_record(self.selected_item.id, record)
        GObject.idle_add(self.callback, self.selected_item, record)
