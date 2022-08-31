[![Python application](https://github.com/vcottineau/pyGpxViewer/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/vcottineau/pyGpxViewer/actions/workflows/python-app.yml)

# pyGpxViewer

**pyGpxViewer** is a simple python applications based on [Gtk4](https://www.gtk.org/)
, [libshumate](https://wiki.gnome.org/Projects/libshumate) and [matplotlib](https://matplotlib.org/) to parse gpx files.
<p align="center">
  <img src="../master/resources/app_window.png" width="400"/>
  <img src="../master/resources/app_window_details.png" width="400"/>
</p>

## Virtual Environments

pyGpxViewer uses [pipenv](https://pypi.org/project/pipenv/) to manage virtualenvs:

```console
pipenv shell
pipenv update --dev
```

## Build

pyGpxViewer uses the [Meson](https://mesonbuild.com/) and [Ninja](https://ninja-build.org/) build systems. Use the
following commands to build from the source directory:

```console
meson setup build
meson compile -C build
```

## Run

To run locally the application:

```console
python build/pygpxviewer_local
```

## Install

To install the application:

```console
meson install -C build
```

## Layers

To add a new layer edit the file under `~/.config/pygpxviewer/sources.json`:

```json
{
  "providers": [
    {
      "name": "OpenStreetMap",
      "api_key": "",
      "layers": [
        {
          "name": "Standard",
          "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        }
      ]
    },
    {
      "name": "Thunderforest",
      "api_key": "?apikey=",
      "layers": [
        {
          "name": "Landscape",
          "url": "https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png"
        },
        {
          "name": "Outdoors",
          "url": "https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png"
        }
      ]
    },
    {
      "name": "Mapbox",
      "api_key": "?access_token=",
      "layers": [
        {
          "name": "Outdoors",
          "url": "https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/tiles/{z}/{x}/{y}"
        },
        {
          "name": "Imagery",
          "url": "https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/tiles/{z}/{x}/{y}"
        }
      ]
    }
  ]
}
```

## License

pyGpxViewer is licensed under the MIT License.
