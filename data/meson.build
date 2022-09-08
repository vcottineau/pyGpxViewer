# Compiling the resources
gnome.compile_resources(
  APPLICATION_ID,
  APPLICATION_ID + '.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: PKGDATA_DIR,
  install: true,
)

schema_src = APPLICATION_ID + '.gschema.xml'
gnome.compile_schemas(build_by_default: true, depend_files: files(schema_src))

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
