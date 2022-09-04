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

from gi.repository import Adw, Gio, GLib, GObject

from pygpxviewer.logger import Logger
from pygpxviewer.window import Window


class Application(Adw.Application):
    """Main application manager."""

    __gtype_name__ = "Application"

    def __init__(self, application_id: str):
        super().__init__(
            application_id=application_id,
            flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.props.resource_base_path = "/com/github/pygpxviewer"
        GLib.set_application_name("pyGpxViewer")
        GLib.set_prgname(application_id)

        self._log = Logger()

        self._app_window = None

    @GObject.Property(type=Logger, default=None, flags=GObject.ParamFlags.READABLE)
    def log(self) -> Logger:
        """Get the logger property.

        @return: Logger to display message(s)
        @rtype: Logger
        """
        return self._log

    def do_startup(self):
        """Start the application."""
        Adw.Application.do_startup(self)

    def do_activate(self):
        """Activate the application."""
        if not self._app_window:
            self._app_window = Window(application=self)
            self._app_window.set_default_icon_name(self.props.application_id)
        self._app_window.present()
