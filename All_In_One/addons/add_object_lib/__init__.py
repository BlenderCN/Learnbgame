# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Contributed to by
# meta-androcto, macouno #

bl_info = {
    "name": "Petunia",
    "author": "Macouno, Meta-Androcto",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "location": "View3D > Add > Mesh > Mesh Objects",
    "description": "Add extra object types",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
from bpy.props import *
import os

def import_object(obname):
    opath = "//petunia_original.blend\\Group\\" + obname
    s = os.sep
    dpath = bpy.utils.script_paths()[0] + \
        '%saddons_extern%sadd_object_lib%spetunia_original.blend\\Group\\' % (s, s, s)

    # DEBUG
    #print('import_object: ' + opath)

    bpy.ops.wm.link_append(
            filepath=opath,
            filename=obname,
            directory=dpath,
            filemode=1,
            link=False,
            autoselect=True,
            active_layer=True,
            instance_groups=False,
            relative_path=True)

    for ob in bpy.context.selected_objects:
        ob.location = bpy.context.scene.cursor_location

class Import_Petunia(bpy.types.Operator):
    '''Imports a rigidbody recorder'''
    bl_idname = "object.import_petunia"
    bl_label = "Add Petunia!"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import_object("Petunia")

        return {'FINISHED'}

class INFO_MT_mesh_petunia_add(bpy.types.Menu):
    # Define the "mesh objects" menu
    bl_idname = "INFO_MT_object_petunia"
    bl_label = "Petunia"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("object.import_petunia",
            text="Petunia")


# Register all operators and panels

# Define "Extras" menu
def menu_func(self, context):
    self.layout.menu("INFO_MT_object_petunia", icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)

    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Extras" menu from the "Add Mesh" menu.
    bpy.types.INFO_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()