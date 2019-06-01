import bpy, os

def make_path(*args):
    return os.path.realpath(os.path.join(*args))

addon_root = bpy.utils.user_resource('SCRIPTS', 'addons')
elfin_root = make_path(addon_root, 'elfin')

pguide_path = make_path(elfin_root, 'pguide.blend')
modlib_path = make_path(elfin_root, 'library.blend')
xdb_path = make_path(elfin_root, 'xdb.json')