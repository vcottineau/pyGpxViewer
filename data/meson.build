# Compiling the resources
# about_dialog is defined in data/ui/meson.build to generate the output file in that directory
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
