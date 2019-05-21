bl_info = {
    'name': 'MMVT',
    'author': 'Ohad Felsenstein & Noam Peled',
    'version': (1, 2),
    'blender': (2, 7, 9),
    'location': 'Press [Space], search for "mmvt_addon"',
    'wiki_url': 'https://github.com/pelednoam/mmvt/wiki',
    'category': 'Development',
}

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
import sys
import os
import importlib as imp

# How to crate a launcher in mac:
# http://apple.stackexchange.com/questions/115114/how-to-put-a-custom-launcher-in-the-dock-mavericks


def current_dir():
    return os.path.dirname(os.path.realpath(__file__))


def mmvt_dir():
    return bpy.path.abspath('//')


# https://github.com/sybrenstuvel/random-blender-addons/blob/master/remote_debugger.py
class MMVTLoaderAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    mmvt_folder = StringProperty(
        name='Path of the mmvt addon folder', description='', subtype='DIR_PATH',
        default='') #os.path.join(mmvt_dir(), 'mmvt_addon'))
    python_cmd = StringProperty(
        name='Path to python (anaconda 3.5)', description='', subtype='FILE_PATH', default='python')
    freeview_cmd = StringProperty(
        name='Path to freeview command', description='', subtype='FILE_PATH', default='freeview')
    freeview_cmd_verbose = BoolProperty( name='Use the verbose flag', default=False)
    freeview_cmd_stdin = BoolProperty(name='Use the stdin flag', default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'mmvt_folder')
        layout.prop(self, 'python_cmd')
        layout.prop(self, 'freeview_cmd')
        layout.prop(self, 'freeview_cmd_verbose')
        layout.prop(self, 'freeview_cmd_stdin')


class MMVTLoaderAddon(bpy.types.Operator):
    bl_idname = 'mmvt_addon.run_addon'
    bl_label = 'Run MMVT addon'
    bl_description = 'Runs the mmvt_addon addon'

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        # mmvt_root = os.path.abspath(addon_prefs.mmvt_folder)
        mmvt_root = bpy.path.abspath(addon_prefs.mmvt_folder)
        print('mmvt_root: {}'.format(mmvt_root))
        sys.path.append(mmvt_root)
        import mmvt_addon
        # If you change the code and rerun the addon, you need to reload MMVT_Addon
        imp.reload(mmvt_addon)
        print(mmvt_addon)
        mmvt_addon.main(addon_prefs)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MMVTLoaderAddon)
    bpy.utils.register_class(MMVTLoaderAddonPreferences)


def unregister():
    bpy.utils.unregister_class(MMVTLoaderAddon)
    bpy.utils.unregister_class(MMVTLoaderAddonPreferences)


if __name__ == '__main__':
    register()