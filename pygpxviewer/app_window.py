from gi.repository import Gio, Gtk, Gdk


from config import Config
from pygpxviewer.app_treeview import AppTreeView


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/app_window.glade")
class AppWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "app_window"

    app_header_bar = Gtk.Template.Child()
    app_window_scrolled_window = Gtk.Template.Child()
    app_button_menu_popover = Gtk.Template.Child()
    app_spinner = Gtk.Template.Child()    

    def __init__(self, application):
        super().__init__(application=application, title=Config.PROGRAM_NAME)

        self.set_icon_name(self.get_application().get_application_id())
        self.settings = Gio.Settings.new("com.github.pygpxviewer.app.window")

        self.css = Gtk.CssProvider()
        self.css.load_from_resource("/com/github/pygpxviewer/style.css")

        self.app_treeview = AppTreeView(self.get_folder_path())
        self.app_window_scrolled_window.add(self.app_treeview)

        self.show_all()

    def start_refresh(self):
        self.app_button_menu_popover.popdown()
        self.app_spinner.start()
        self.set_sensitive(False)
        self.app_treeview.refresh_treeview(self.stop_refresh)

    def stop_refresh(self):
        self.app_treeview.update_treeview()
        self.app_spinner.stop()
        self.set_sensitive(True)

    def get_folder_path(self):
        return self.settings.get_string("folder-path")

    @Gtk.Template.Callback()
    def on_app_button_open_clicked(self,button):
        dialog = Gtk.FileChooserDialog(
            title="Select folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.settings.set_string("folder-path", dialog.get_filename())
            self.app_treeview.folder = self.get_folder_path()
            self.app_treeview.reset_treeview()

        dialog.destroy()

    @Gtk.Template.Callback()
    def on_window_state_event(self, widget, event):
        if bool(widget.get_window().get_state() & Gdk.WindowState.MAXIMIZED):
            print("is_maximized")
