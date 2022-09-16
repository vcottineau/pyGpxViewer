[![build](https://github.com/vcottineau/pyGpxViewer/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/vcottineau/pyGpxViewer/actions/workflows/build.yml)
[![docs](https://github.com/vcottineau/pyGpxViewer/actions/workflows/docs.yml/badge.svg)](https://github.com/vcottineau/pyGpxViewer/actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# pyGpxViewer

**pyGpxViewer** is a simple python applications based on [Gtk4](https://www.gtk.org/)
, [libshumate](https://wiki.gnome.org/Projects/libshumate) and [matplotlib](https://matplotlib.org/).\
[gpxpy](https://github.com/tkrajina/gpxpy) and [ViewFinder Panoramas](http://viewfinderpanoramas.org/dem3.html) (3DEM)
are used to parse gpx
files.

<p align="center">
  <img src="../master/resources/app_window.png" width="400"/>
  <img src="../master/resources/app_window_details.png" width="400"/>
</p>

## Documentation

pyGpxViewer uses [sphinx](https://www.sphinx-doc.org/en/master/) and [readthedocs](https://readthedocs.org/) to manage
documentation: [pygpxviewer.readthedocs.io](https://pygpxviewer.readthedocs.io/en/latest/)

## Virtual Environments

pyGpxViewer uses [pipenv](https://pypi.org/project/pipenv/) to manage virtualenvs:

```console
pipenv shell
pipenv update --dev
```

## Build

pyGpxViewer uses the [meson](https://mesonbuild.com/) build systems. Use the following commands to build from the source
directory:

```console
meson setup _build
meson compile -C _build
meson test -C _build
```

## Run

To run locally the application:

```console
G_MESSAGES_DEBUG=com.github.pygpxviewer _build/pygpxviewer_local
```

To run locally the application with the built-in interactive debugging support:

```console
GTK_DEBUG=interactive _build/pygpxviewer_local  
```

## Install

To install the application:

```console
meson install -C _build
```

## Localisation

To generate .pot & .po files:

```console
meson compile -C _build com.github.pygpxviewer-pot
meson compile -C _build com.github.pygpxviewer-update-po
```

## Layers

To add a new layer edit the file under `~/.config/pygpxviewer/map.json`:

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
