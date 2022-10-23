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
from typing import Optional, Tuple

from gi.repository import Gio, GObject, Gtk, Pango

from pygpxviewer.helpers.sqlitehelper import SQLiteHelper
from pygpxviewer.threads.workers import WorkerUpdateRecord
from pygpxviewer.widgets.gpxdetailedview import GpxDetailedView


class GpxItem(GObject.GObject):
    """GpxItem is the item used to fill to Gio.ListStore."""

    __gtype_name__ = "GpxItem"

    id = GObject.Property(type=int)
    path = GObject.Property(type=str)
    points = GObject.Property(type=int)
    length = GObject.Property(type=float)
    up_hill = GObject.Property(type=float)
    down_hill = GObject.Property(type=float)

    def __init__(self, id: int, path: str, points: int, length: float, up_hill: float, down_hill: float) -> None:
        """Init method.

        :param id: SQLite database id
        :type id: int
        :param path: File system path
        :type path: str
        :param points: Number of track points
        :type points: int
        :param length: Total distance in km
        :type length: float
        :param up_hill: Total ascent in m
        :type up_hill: float
        :param down_hill: Total descent in m
        :type down_hill: float
        """
        super().__init__()

        self.id = id
        self.path = path
        self.points = points
        self.length = length
        self.up_hill = up_hill
        self.down_hill = down_hill


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/GpxColumnView.ui")
class GpxColumnView(Gtk.ColumnView):
    """GpxColumnView is the main Window child.

    Display all .gpx files listed in a folder and their main properties
    """

    __gtype_name__ = "GpxColumnView"

    _single_selection = Gtk.Template.Child()
    _sort_list_model = Gtk.Template.Child()
    _path_view_column = Gtk.Template.Child()

    _factory_path = Gtk.Template.Child()
    _factory_points = Gtk.Template.Child()
    _factory_length = Gtk.Template.Child()
    _factory_up_hill = Gtk.Template.Child()
    _factory_down_hill = Gtk.Template.Child()

    def __init__(self, window):
        super().__init__()

        self._window = window
        self._sqlitehelper = SQLiteHelper()

        self._list_store = Gio.ListStore()
        self._sort_list_model.set_model(self._list_store)

        self.sort_by_column(self._path_view_column, Gtk.SortType.ASCENDING)
        self._setup_column_view()

    def refresh(self, search_entry: Optional[str] = None) -> None:
        """Apply text filter and refresh the view.

        :param search_entry: Text pattern to search
        :type search_entry: Optional[str]
        """
        self._list_store.remove_all()
        if search_entry:
            records = self._sqlitehelper.search_gpx_records(search_entry)
        else:
            records = self._sqlitehelper.get_gpx_records()
        for record in records:
            id, path, points, length, up_hill, down_hill = record
            gpx_item = GpxItem(id, path, points, length, up_hill, down_hill)
            self._list_store.append(gpx_item)

    def _setup_column_view(self):
        self._factory_path.connect("bind", self._factory_bind, "path")
        self._factory_points.connect("bind", self._factory_bind, "points")
        self._factory_length.connect("bind", self._factory_bind, "length")
        self._factory_up_hill.connect("bind", self._factory_bind, "up_hill")
        self._factory_down_hill.connect("bind", self._factory_bind, "down_hill")

    @Gtk.Template.Callback()
    def _factory_setup_label(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        label = Gtk.Label()
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_halign(Gtk.Align.START)
        list_item.set_child(label)

    @Gtk.Template.Callback()
    def _factory_setup_actions(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        box = Gtk.Box(spacing=6)

        buttons = [
            {"icon": "mark-location-symbolic", "callback": self._on_button_view_clicked},
            {"icon": "view-refresh-symbolic", "callback": self._on_button_refresh_clicked},
            {"icon": "user-trash-symbolic", "callback": self._on_button_trash_clicked}
        ]
        for button in buttons:
            action_button = Gtk.Button().new_from_icon_name(button["icon"])
            action_button.connect("clicked", button["callback"], list_item)
            context = action_button.get_style_context()
            Gtk.StyleContext.add_class(context, "column_view_button")
            box.append(action_button)

        list_item.set_child(box)

    def _factory_bind(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem, property_name: str) -> None:
        label = list_item.get_child()
        item = list_item.get_item()
        item.connect(f"notify::{property_name}", self._on_item_property_change, label)
        self._set_label_text(item, property_name, label)

    def _on_item_property_change(self, item: GpxItem, gparamstring: GObject.ParamSpec, label: Gtk.Label) -> None:
        self._set_label_text(item, gparamstring.name, label)

    def _set_label_text(self, item: GpxItem, property_name: str, label: Gtk.Label) -> None:
        if property_name == "path":
            property_value = item.get_property(property_name).replace(self._window.folder_path, "")
        else:
            property_value = str(round(item.get_property(property_name)))
        label.set_text(property_value)

    def _on_button_view_clicked(self, button: Gtk.Button, list_item: Gtk.ListItem) -> None:
        selected_item = self._get_selected_item(list_item)
        app_detailed_view = GpxDetailedView(selected_item.path)
        app_detailed_view.props.transient_for = self._window
        app_detailed_view.present()

    def _on_button_trash_clicked(self, button: Gtk.Button, list_item: Gtk.ListItem) -> None:
        raise NotImplementedError

    def _on_button_refresh_clicked(self, button: Gtk.Button, list_item: Gtk.ListItem) -> None:
        selected_item = self._get_selected_item(list_item)
        self._window.set_sensitive(False)
        self._window.spinner.start()

        thread = WorkerUpdateRecord(selected_item, self._on_update_record_ended)
        thread.start()

    def _on_update_record_ended(self, selected_item: Gtk.ListItem, record: Tuple) -> None:
        selected_item.points = record[1]
        selected_item.length = record[2]
        selected_item.up_hill = record[3]
        selected_item.down_hill = record[4]

        self._window.spinner.stop()
        self._window.set_sensitive(True)

    def _get_selected_item(self, list_item: Gtk.ListItem) -> Gtk.ListItem:
        position = list_item.get_position()
        self._single_selection.set_selected(position)
        return self._single_selection.get_selected_item()
