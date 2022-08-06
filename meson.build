project('pygpxviewer',
    version: '1.0',
    meson_version: '>= 0.63.0'
)

# Importing modules
gnome = import('gnome')
python = import('python')

# Module objects
py_installation = python.find_installation('python3')

# Make sure Python is installed and found
if not py_installation.found()
    error('No valid python3 binary found')
endif

# Python 3.7 is needed for postponed evalution of annotations
if not py_installation.language_version().version_compare('>= 3.7')
  error('Python 3.7 or newer is required.')
endif

# Constants
PROJECT_RDNN_NAME = 'fr.vcottineau.pygpxviewer'
APPLICATION_ID = 'fr.vcottineau.pygpxviewer'
PYTHON_DIR = py_installation.get_path('purelib')
PKGDATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), APPLICATION_ID)
PKGLIB_DIR = join_paths(get_option('prefix'), get_option('libdir'), APPLICATION_ID)

# Dependencies
dependency('glib-2.0', version: '>= 2.72.3')
dependency('gobject-introspection-1.0', version: '>= 1.72.0')
dependency('gtk+-3.0', version: '>= 3.24.34')
dependency('pygobject-3.0', version: '>= 3.42.2')

subdir('data')

install_subdir(
    'pygpxviewer',
    install_dir: py_installation.get_install_dir()
)

# Install the executable file
bin_config = configuration_data()
bin_config.set('application_id', APPLICATION_ID)
bin_config.set('rdnn_name', PROJECT_RDNN_NAME)
bin_config.set('pkgdatadir', PKGDATA_DIR)
bin_config.set('pythondir', PYTHON_DIR)
bin_config.set('schemasdir', PKGDATA_DIR)

bin_config.set('local_build', 'False')

configure_file(
    input: 'pygpxviewer.in',
    output: 'pygpxviewer',
    configuration: bin_config,
    install_dir: get_option('bindir')
)

# Install the builddir executable
local_config = configuration_data()
local_config.set('application_id', APPLICATION_ID)
local_config.set('rdnn_name', PROJECT_RDNN_NAME)
local_config.set('pkgdatadir', join_paths(meson.current_build_dir(), 'data'))
local_config.set('pythondir', meson.current_source_dir())
local_config.set('schemasdir', join_paths(meson.current_build_dir(), 'data'))

local_config.set('local_build', 'True')

configure_file(
    input: 'pygpxviewer.in',
    output: 'pygpxviewer_local',
    configuration: local_config
)

gnome.post_install(
    glib_compile_schemas: true,
    gtk_update_icon_cache: true,
    update_desktop_database: true
)

meson.add_postconf_script('build-aux/meson/postconf.py')