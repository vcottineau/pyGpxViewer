import json
from pathlib import Path


from gi.repository import Gio, Gtk, Gdk, GLib
from gi.repository.WebKit2 import WebView
from gi.repository import WebKit2


from config import Config


@Gtk.Template(resource_path="/fr/vcottineau/pygpxviewer/ui/app_webview.glade")
class AppWebView(WebKit2.WebView):
    __gtype_name__ = "app_webview"

    app_webview = Gtk.Template.Child()

    def __init__(self, bounds, locations):
        super().__init__()

        self.bounds = bounds
        self.locations = locations

        self.load_uri("file://" + str(Path(__file__).resolve().parent) + "/app_webview.html")

    @Gtk.Template.Callback()
    def on_app_webview_load_changed(self, web_view, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED:
            self.run_javascript(f"""init(
                {json.dumps(Config.MAPBOX_API_KEY)},
                {self.bounds.min_longitude},
                {self.bounds.max_longitude},
                {self.bounds.min_latitude},
                {self.bounds.max_latitude},
                {json.dumps([location for location in self.locations])})"""
            )



    # def run_javascript_finish(self, webview, result, user_data):
    #     javascript_result = self.web_view.run_javascript_finish(result)
    #     if javascript_result:
    #         value = javascript_result.get_js_value()
    #         print(value.to_string())