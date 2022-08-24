#!/usr/bin/env python3

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

import subprocess
from os import environ, path

build_root = environ.get("MESON_BUILD_ROOT")
source_root = environ.get("MESON_SOURCE_ROOT")

subprocess.call([
    "chmod", "+x",
    path.join(build_root, "pygpxviewer")
])

subprocess.call([
    "chmod", "+x",
    path.join(build_root, "pygpxviewer_local")
])

subprocess.call([
    "cp", "-R",
    path.join(source_root, "data", "icons"),
    path.join(build_root, "data")
])

subprocess.call([
    "gtk-update-icon-cache", "-qtf",
    path.join(build_root, "data", "icons", "hicolor")
])

subprocess.call([
    "glib-compile-schemas",
    path.join(source_root, "data")
])

subprocess.call([
    "mkdir", "-p",
    path.join(build_root, "data", "glib-2.0", "schemas")
])

subprocess.call([
    "mv",
    path.join(source_root, "data", "gschemas.compiled"),
    path.join(build_root, "data", "glib-2.0", "schemas")
])
