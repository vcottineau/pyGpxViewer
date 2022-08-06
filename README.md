# pyGpxViewer

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

## Run
To run the application:

```
python build/pygpxviewer_local
```

## License
pyGpxViewer is licensed under the MIT License.