# Compiling the resources
gnome.compile_resources(
    APPLICATION_ID,
    APPLICATION_ID + '.gresource.xml',
    gresource_bundle: true,
    source_dir: meson.current_build_dir(),
    install_dir: PKGDATA_DIR,
    install: true
)

schema_src = APPLICATION_ID + '.gschema.xml'
gnome.compile_schemas(build_by_default: true, depend_files: files(schema_src))

# Configure the appdata file
appdata_conf = configuration_data()
appdata_conf.set('application_id', APPLICATION_ID)
appdata_conf.set('application_url', APPLICATION_URL)
appdata_conf.set('application_version', meson.project_version())
configure_file(
    input: APPLICATION_ID + '.appdata.xml.in',
    output: APPLICATION_ID + '.appdata.xml',
    configuration: appdata_conf,
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'metainfo')
)

# Validating the appdata file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
    test (
        'Validate appdata file',
        appstream_util,
        args: ['validate-relax', join_paths(meson.current_build_dir (), APPLICATION_ID + '.appdata.xml')]
    )
endif

# Configure desktop file
desktop_conf = configuration_data()
desktop_conf.set('icon', APPLICATION_ID)
configure_file(
    input: APPLICATION_ID + '.desktop.in',
    output: APPLICATION_ID + '.desktop',
    configuration: desktop_conf,
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

# Validating the desktop file
desktop_file_validate = find_program('desktop-file-validate', required:false)
if desktop_file_validate.found()
    test (
        'Validate desktop file',
        desktop_file_validate,
        args: join_paths(meson.current_build_dir (), APPLICATION_ID + '.desktop')
    )
endif

# Installing the schema file
install_data(
    schema_src,
    install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

# Installing the default icon
install_data(
    join_paths('icons/hicolor/scalable/apps', APPLICATION_ID + '.svg'),
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'icons/hicolor/scalable/apps')
)
