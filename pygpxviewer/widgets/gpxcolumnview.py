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

from gi.repository import Gio, GObject, Gtk, Pango

from pygpxviewer.helpers import GpxHelper, sqlite_helper
from pygpxviewer.widgets.gpxdetailedview import GpxDetailedView


class GpxItem(GObject.GObject):
    __gtype_name__ = "GpxItem"

    path = GObject.Property(type=str)
    points = GObject.Property(type=int)
    length = GObject.Property(type=float)
    up_hill = GObject.Property(type=float)
    down_hill = GObject.Property(type=float)

    def __init__(self, path, points, length, up_hill, down_hill):
        super().__init__()

        self.path = path
        self.points = points
        self.length = length
        self.up_hill = up_hill
        self.down_hill = down_hill


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/GpxColumnView.ui")
class GpxColumnView(Gtk.ColumnView):
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

        self._list_store = Gio.ListStore()
        self._sort_list_model.set_model(self._list_store)

        self.sort_by_column(self._path_view_column, Gtk.SortType.ASCENDING)
        self._setup_column_view()

    def refresh(self, search_entry=None):
        self._list_store.remove_all()
        if search_entry:
            records = sqlite_helper.search_records(search_entry)
        else:
            records = sqlite_helper.get_records()
        for record in records:
            _, path, points, length, up_hill, down_hill = record
            gpx_item = GpxItem(path, points, length, up_hill, down_hill)
            self._list_store.append(gpx_item)

    def _setup_column_view(self) -> None:
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

        button_view = Gtk.Button.new_from_icon_name("mark-location-symbolic")
        button_view.connect("clicked", self._on_button_view_clicked, list_item)
        context = button_view.get_style_context()
        Gtk.StyleContext.add_class(context, "column_view_button")
        box.append(button_view)

        button_refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        button_refresh.connect("clicked", self._on_button_refresh_clicked, list_item)
        context = button_refresh.get_style_context()
        Gtk.StyleContext.add_class(context, "column_view_button")
        box.append(button_refresh)

        list_item.set_child(box)

    def _factory_bind(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem, property_name: str) -> None:
        label = list_item.get_child()
        data = list_item.get_item()
        if property_name == "path":
            value = data.get_property(property_name).replace(self._window.folder_path, "")
            label.set_text(value)
        else:
            value = str(round(data.get_property(property_name)))
            label.set_text(value)

    def _on_button_view_clicked(self, button: Gtk.Button, list_item: Gtk.ListItem) -> None:
        selected_item = self._get_selected_item(list_item)
        app_detailed_view = GpxDetailedView(selected_item.path)
        app_detailed_view.props.transient_for = self._window
        app_detailed_view.present()

    def _on_button_refresh_clicked(self, button: Gtk.Button, list_item: Gtk.ListItem) -> None:
        selected_item = self._get_selected_item(list_item)

        gpx_helper = GpxHelper(selected_item.path)
        gpx_helper.set_gpx_info()

        record = gpx_helper.get_gpx_details()
        sqlite_helper.update_record(record)

        selected_item.points = record[1]
        selected_item.length = record[2]
        selected_item.up_hill = record[3]
        selected_item.down_hill = record[4]

    def _get_selected_item(self, list_item: Gtk.ListItem) -> Gtk.ListItem:
        position = list_item.get_position()
        self._single_selection.set_selected(position)
        return self._single_selection.get_selected_item()
