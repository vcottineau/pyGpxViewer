#!/usr/bin/env python3

import subprocess
from os import environ, path


build_root = environ.get("MESON_BUILD_ROOT")
source_root = environ.get("MESON_SOURCE_ROOT")

subprocess.call([
    "chmod", "+x",
    path.join(build_root, "pygpxviewer")
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