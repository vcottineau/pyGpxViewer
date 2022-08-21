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

import inspect
import os

from gi.repository import GLib, GObject


class Logger(GObject.GObject):
    """GLib logging wrapper

    A tiny wrapper aroung the default GLib logger.

    * Message is for user facing warnings, which ideally should be in
      the application.
    * Warning is for logging non-fatal errors during execution.
    * Debug is for developer use as a way to get more runtime info.
    """

    _DOMAIN = "com.github.pygpxviewer"

    def _log(self, message, level):
        stack = inspect.stack()

        filename = os.path.basename(stack[2][1])
        line = stack[2][2]
        function = stack[2][3]

        if level in [GLib.LogLevelFlags.LEVEL_DEBUG,
                     GLib.LogLevelFlags.LEVEL_INFO,
                     GLib.LogLevelFlags.LEVEL_WARNING]:
            message = "({}, {}, {}) {}".format(
                filename, function, line, message)

        variant_message = GLib.Variant("s", message)
        variant_file = GLib.Variant("s", filename)
        variant_line = GLib.Variant("i", line)
        variant_func = GLib.Variant("s", function)

        variant_dict = GLib.Variant("a{sv}", {
            "MESSAGE": variant_message,
            "CODE_FILE": variant_file,
            "CODE_LINE": variant_line,
            "CODE_FUNC": variant_func
        })

        GLib.log_variant(self._DOMAIN, level, variant_dict)

    def message(self, message):
        self._log(message, GLib.LogLevelFlags.LEVEL_MESSAGE)

    def warning(self, message):
        self._log(message, GLib.LogLevelFlags.LEVEL_WARNING)

    def info(self, message):
        self._log(message, GLib.LogLevelFlags.LEVEL_INFO)

    def debug(self, message):
        self._log(message, GLib.LogLevelFlags.LEVEL_DEBUG)
