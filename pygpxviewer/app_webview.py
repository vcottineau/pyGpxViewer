import json
from pathlib import Path


from gi.repository import Gio, Gtk, Gdk, GLib
from gi.repository import WebKit2


from config import Config
from pygpxviewer.utils import get_resource_as_string


@Gtk.Template(resource_path="/com/github/pygpxviewer/ui/app_webview.glade")
class AppWebView(WebKit2.WebView):
    __gtype_name__ = "app_webview"

    app_webview = Gtk.Template.Child()

    def __init__(self, bounds, locations):
        super().__init__()

        self.bounds = bounds
        self.locations = locations

        self.html = get_resource_as_string("/map/map.html")
        self.load_html(self.html)

        self.script = get_resource_as_string("/map/map.js")
        self.user_script = WebKit2.UserScript.new(self.script, 0, 1, None, None)

        self.user_content_manager = self.get_user_content_manager()
        self.user_content_manager.add_script(self.user_script)

        self.user_content_manager.connect("script-message-received::test_callback", self.on_test_callback)
        self.user_content_manager.register_script_message_handler("test_callback")
        
    def on_test_callback(self, user_content_manager, js_result):
        print("on_test_callback")

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
