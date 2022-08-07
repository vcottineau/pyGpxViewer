from gi.repository import Gio


def get_resource_as_string(path):
    resource = Gio.resources_lookup_data("/com/github/pygpxviewer" + path, Gio.ResourceLookupFlags.NONE)
    return resource.get_data().decode('utf-8')
