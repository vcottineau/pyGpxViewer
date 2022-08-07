import pathlib


from gi.repository import Gio, Gtk, Gdk


from pygpxviewer.gpx_helper import gpx_helper
from pygpxviewer.workers import WorkerGpxThread
from pygpxviewer.app_window_details import AppWindowDetails


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/app_treeview.glade")
class AppTreeView(Gtk.TreeView):
    __gtype_name__ = "app_treeview"

    LST_COL_PATH = 0
    LST_COL_LENGTH = 1
    LST_COL_UP_HILL = 2
    LST_COL_DOWN_HILL = 3

    TRV_COL_PATH = 0
    TRV_COL_LENGTH = 1
    TRV_COL_UP_HILL = 2
    TRV_COL_DOWN_HILL = 3
    TRV_COL_VIEW = 4

    app_tree_model = Gtk.Template.Child()
    app_tree_selection = Gtk.Template.Child()

    app_tree_col_path = Gtk.Template.Child()
    app_tree_col_length = Gtk.Template.Child()
    app_tree_col_up_hill = Gtk.Template.Child()
    app_tree_col_down_hill = Gtk.Template.Child()

    app_tree_cell_path = Gtk.Template.Child()
    app_tree_cell_length = Gtk.Template.Child()
    app_tree_cell_up_hill = Gtk.Template.Child()
    app_tree_cell_down_hill = Gtk.Template.Child()

    def __init__(self, folder):
        super().__init__()

        self.folder = folder
        self.props.activate_on_single_click = True

        self.app_tree_col_path.set_cell_data_func(self.app_tree_cell_path, self.format_data_func, func_data=AppTreeView.LST_COL_PATH)
        self.app_tree_col_length.set_cell_data_func(self.app_tree_cell_length, self.roud_data_func, func_data=AppTreeView.LST_COL_LENGTH)
        self.app_tree_col_up_hill.set_cell_data_func(self.app_tree_cell_up_hill, self.roud_data_func, func_data=AppTreeView.LST_COL_UP_HILL)
        self.app_tree_col_down_hill.set_cell_data_func(self.app_tree_cell_down_hill, self.roud_data_func, func_data=AppTreeView.LST_COL_DOWN_HILL)

        self.reset_treeview()
        
    def format_data_func(self, tree_column, cell, tree_model, iter, column):
        value = self.app_tree_model.get_value(iter, column)
        cell.set_property('text', value.replace(self.folder + "/", ""))

    def roud_data_func(self, tree_column, cell, tree_model, iter, column):
        value = self.app_tree_model.get_value(iter, column)
        cell.set_property('text', str(round(value)))

    def refresh_treeview(self, callback):
        thread = WorkerGpxThread(self.get_gpx_files(), callback)
        thread.start()

    def reset_treeview(self):
        self.app_tree_model.clear()
        for gpx_file in self.get_gpx_files():
            self.app_tree_model.append([str(gpx_file), 0, 0, 0])
        self.update_treeview()

    def update_treeview(self):
        for row in self.app_tree_model:
            row[AppTreeView.LST_COL_LENGTH] = gpx_helper.get_gpx_length(row[AppTreeView.LST_COL_PATH])
            row[AppTreeView.LST_COL_UP_HILL] = gpx_helper.get_gpx_up_hill(row[AppTreeView.LST_COL_PATH])
            row[AppTreeView.LST_COL_DOWN_HILL] = gpx_helper.get_gpx_down_hill(row[AppTreeView.LST_COL_PATH])
            
    def get_gpx_files(self):
        return pathlib.Path(self.folder).glob("**/*.gpx")

    @Gtk.Template.Callback()
    def on_app_treeview_button_press_event(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            (model, iter) = self.app_tree_selection.get_selected()
            value = self.app_tree_model.get_value(iter, AppTreeView.LST_COL_PATH)
            Gio.AppInfo.launch_default_for_uri(pathlib.Path(value).as_uri())

    @Gtk.Template.Callback()
    def on_row_activated(self, tree_view, path, column):
        if self.get_column(AppTreeView.TRV_COL_VIEW) == column:
            iter = self.app_tree_model.get_iter(path)
            value = self.app_tree_model.get_value(iter, AppTreeView.LST_COL_PATH)
            app_window_details = AppWindowDetails(gpx_file=value)
            app_window_details.show_all()


