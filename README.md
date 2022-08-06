# pyGpxViewer
![app_window.png](../master/resources/app_window.png) ![app_window_detals.png](../master/resources/app_window_details.png)

**pyGpxViewer** is a simple python applications based on [Gtk3](https://www.gtk.org/). Map services are provided by [Mapbox](https://www.mapbox.com/) to render 3D terrain.

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