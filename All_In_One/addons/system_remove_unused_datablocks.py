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

bl_info = {
    'name': 'Remove Unused Datablocks',
    'author': 'Bartek Skorupa',
    'version': (0, 0),
    'blender': (2, 6, 9),
    'location': "File -> Remove Unused Datablocks",
    'description': 'Remove Unused Datablocks',
    'category': 'System',
    "warning": "",
    'wiki_url': "",
    'tracker_url': "",
    }

import bpy
from bpy.props import BoolProperty
datablocks = (
    'particles',
    'actions',
    'armatures',
    'cameras',
    'curves',
    'lamps',
    'lattices',
    'meshes',
    'texts',
    'materials',
    'textures',
    'worlds',
    'images',
    )

class RemoveDatablocks(bpy.types.Operator):
    bl_idname = "system.remove_datablocks"
    bl_label = "Remove Unused Datablocks"
    bl_options = {'REGISTER', 'UNDO'}

    for entry in datablocks:
        vars()[entry] = BoolProperty()
    
    def execute(self, context):
        for blockname in datablocks:
            if getattr(self, blockname):
                block = getattr(bpy.data, blockname)
                for element in (e for e in block if not e.users):
                    element.user_clear()
                    block.remove(element)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        for entry in datablocks:
            setattr(self, entry, True)
        return context.window_manager.invoke_props_dialog(self)

def menu_func(self, context):
    self.layout.operator(RemoveDatablocks.bl_idname, text="Remove Unused Datablocks", icon="X")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file.remove(menu_func)

if __name__ == "__main__":
    register()