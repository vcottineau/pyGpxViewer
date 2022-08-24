[![Python application](https://github.com/vcottineau/pyGpxViewer/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/vcottineau/pyGpxViewer/actions/workflows/python-app.yml)
# pyGpxViewer
**pyGpxViewer** is a simple python applications based on [Gtk4](https://www.gtk.org/), [libshumate](https://wiki.gnome.org/Projects/libshumate) and [matplotlib](https://matplotlib.org/) to parse gpx files.
<p align="center">
  <img src="../master/resources/app_window.png" width="400"/>
  <img src="../master/resources/app_window_details.png" width="400"/>
</p>

## Virtual Environments
pyGpxViewer uses [pipenv](https://pypi.org/project/pipenv/) to manage virtualenvs:

```
pipenv shell
pipenv update --dev
```

## Build
pyGpxViewer uses the [Meson](https://mesonbuild.com/) and [Ninja](https://ninja-build.org/) build systems. Use the following commands to build from the source directory:

```
meson setup build
meson compile -C build
```

## Run
To run locally the application:

```
python build/pygpxviewer_local
```

## Install
To install the application:

```
meson install -C build
```

## License
pyGpxViewer is licensed under the MIT License.
