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
from typing import Union

from gi.repository import Gio, GLib, Gtk


def get_resource(path: str, decode: bool = False) -> Union[str, GLib.Bytes]:
    """Get a resource file as string.

    :param path: Path of the resource file
    :type path: str
    :param decode: Get resource file as string
    :type decode: bool
    :returns: Resource file as string
    :rtype: Union[str, GLib.Bytes]
    """
    resource = Gio.resources_lookup_data("/com/github/pygpxviewer" + path, Gio.ResourceLookupFlags.NONE)
    if decode:
        return resource.get_data().decode('utf-8')
    return resource.get_data()


def is_dark_theme_enable() -> bool:
    """Check if the dark theme is enabled.

    :returns: True if dark theme is enabled
    :rtype: bool
    """
    return Gtk.Settings.get_default().props.gtk_application_prefer_dark_theme
