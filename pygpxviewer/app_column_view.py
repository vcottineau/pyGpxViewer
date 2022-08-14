from gi.repository import Gio, Gtk, GObject, Pango


from pygpxviewer.app_window_details import AppWindowDetails
from pygpxviewer.helpers import sqlite_helper, gpx_helper


class Item(GObject.GObject):
    __gtype_name__ = "item"

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


class AppColumnView(Gtk.ColumnView):
    __gtype_name__ = "app_column_view"

    def __init__(self,):
        super().__init__()

        self.folder_path = None
        self.search_entry_value = None

        self.set_show_row_separators(True)
        self.set_show_column_separators(True)

        self.single_selection = Gtk.SingleSelection()
        self.sort_list_model = Gtk.SortListModel()
        self.list_store = Gio.ListStore()

        self.set_model(self.single_selection)
        self.single_selection.set_model(self.sort_list_model)
        self.sort_list_model.set_model(self.list_store)
        self.sort_list_model.set_sorter(self.get_sorter())

        columns = [
            {"title": "Path", "property": "path", "expand": True, "setup": self.factory_setup_label, "bind": self.factory_bind_label},
            {"title": "Points (nb)", "property": "points", "expand":  False, "setup": self.factory_setup_label, "bind": self.factory_bind_label},
            {"title": "Length (km)", "property": "length", "expand":  False, "setup": self.factory_setup_label, "bind": self.factory_bind_label},
            {"title": "UpHill (m)", "property": "up_hill", "expand":  False, "setup": self.factory_setup_label, "bind": self.factory_bind_label},
            {"title": "DownHill (m)", "property": "down_hill", "expand":  False, "setup": self.factory_setup_label, "bind": self.factory_bind_label},
            {"title": "Actions", "property": None, "expand":  False, "setup": self.factory_setup_actions, "bind": None}
        ]

        for column in columns:
            column_view_column = Gtk.ColumnViewColumn()
            column_view_column.set_title(column["title"])
            column_view_column.set_expand(column["expand"])

            signal_list_item_factory = Gtk.SignalListItemFactory()
            signal_list_item_factory.connect("setup", column["setup"])

            if column["bind"]:
                signal_list_item_factory.connect("bind", column["bind"], column["property"])

                # property_expression = Gtk.PropertyExpression.new(Item, None, column["property"])
                # string_sorter = Gtk.StringSorter()
                # string_sorter.set_expression(property_expression)
                # column.set_sorter(string_sorter)

            column_view_column.set_factory(signal_list_item_factory)
            self.append_column(column_view_column)

        self.reset_liststore()

    def reset_liststore(self):
        self.list_store.remove_all()
        records = sqlite_helper.get_records()
        for record in records:
            _, path, points, length, up_hill, down_hill = record
            item = Item(path, points, length, up_hill, down_hill)
            if self.search_entry_value:
                if self.search_entry_value in path.lower():
                    self.list_store.append(item)
            else:
                self.list_store.append(item)

    def on_folder_path_changed(self, app_window, g_param_spec):
        self.folder_path = app_window.get_property(g_param_spec.name)

    def on_search_entry_changed(self, editable):
        self.search_entry_value = editable.get_text().lower()
        self.reset_liststore()

    def factory_setup_label(self, factory, list_item):
        label = Gtk.Label()
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_halign(Gtk.Align.START)
        list_item.set_child(label)

    def factory_setup_actions(self, factory, list_item):
        box = Gtk.Box(spacing=6)

        button_view = Gtk.Button.new_from_icon_name("mark-location-symbolic")
        button_refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic")

        context = button_view.get_style_context()
        Gtk.StyleContext.add_class(context, "column_view_button")

        context = button_refresh.get_style_context()
        Gtk.StyleContext.add_class(context, "column_view_button")

        button_view.connect("clicked", self.on_button_view_clicked, list_item)
        button_refresh.connect("clicked", self.on_button_refresh_clicked, list_item)

        box.append(button_view)
        box.append(button_refresh)

        list_item.set_child(box)

    def factory_bind_label(self, factory, list_item, property):
        label = list_item.get_child()
        data = list_item.get_item()
        if property == "path":
            label.set_text(data.get_property(property).replace(self.folder_path, ""))
        else:
            label.set_text(str(round(data.get_property(property))))

    def on_button_view_clicked(self, button, list_item):
        position = list_item.get_position()
        self.single_selection.set_selected(position)
        selected_item = self.single_selection.get_selected_item()
        app_window_details = AppWindowDetails(selected_item.path)
        app_window_details.show()

    def on_button_refresh_clicked(self, button, list_item):
        position = list_item.get_position()
        self.single_selection.set_selected(position)
        selected_item = self.single_selection.get_selected_item()

        gpx_helper.set_gpx(selected_item.path)
        gpx_helper.set_gpx_info()

        path = str(selected_item.path)
        points = gpx_helper.get_gpx_points_nb()
        length = gpx_helper.get_gpx_length()
        up_hill = gpx_helper.get_gpx_up_hill()
        down_hill = gpx_helper.get_gpx_down_hill()

        record = (path, points, length, up_hill, down_hill)
        sqlite_helper.update_record(record)

        selected_item.path = path
        selected_item.points = points
        selected_item.length = length
        selected_item.up_hill = up_hill
        selected_item.down_hill = down_hill
