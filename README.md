# pyGpxViewer
**pyGpxViewer** is a simple python applications based on [Gtk4](https://www.gtk.org/) to parse gpx files.
<p align="center">
  <img src="../master/resources/app_window.png" width="500"/>
  <img src="../master/resources/app_window_details.png" width="500"/>
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
meson build
ninja -C build
```

## Mapbox API
A [Mapbox](https://www.mapbox.com/) account is required to request an API key and to render 3D terrain maps.
```
nano .env
MAPBOX_API_KEY=$MAPBOX_API_KEY
```

## Run
To run locally the application:

```
python build/pygpxviewer_local
```

## Install
To install the application:

```
ninja -C build install
```

## License
pyGpxViewer is licensed under the MIT License.
