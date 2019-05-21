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
    'name': 'Make True Parent',
    'description': 'Make True Parent',
    'location': 'View3D > Ctrl+Shift+Alt+P',
    'author': 'Bartek Skorupa',
    'version': (1, 1),
    'blender': (2, 72, 0),
    'category': 'Object',
    "warning": "",
    }

import bpy
from bpy.props import EnumProperty

def main(option):
    selected = bpy.context.selected_objects
    active = bpy.context.active_object
    
    for ob in [o for o in selected if o != active]:
        m = ob.matrix_world
        ob.parent = active
        if option == 'KEEP_VISUAL_TRANSFORMATIONS':
            ob.matrix_world = m
        elif option == 'RESET':
            ob.matrix_local.identity()
        # when option is 'KEEP_TRANSFORMATIONS_VALUES' - do nothing
        # this will keep transforms values untouched, but move children accordingly.
    return {'FINISHED'}

class MakeTrueParent(bpy.types.Operator):
    bl_idname = "object.make_true_parent"
    bl_label = "Make True Parent"
    bl_options = {'REGISTER', 'UNDO'}
    
    option = EnumProperty(
        name="Parenting Option",
        items=(
            ("KEEP_VISUAL_TRANSFORMATIONS", "Keep Visual Transformations", "Keep Visual Transformations, change values"),
            ("RESET", "Reset Transformations", "Reset Transformations"),
            ("KEEP_TRANSFORMATIONS_VALUES", "Keep Transformations Values", "Keep Transformations Values"),
            )
        )
    
    @classmethod
    def poll(cls, context):
        return (context.active_object != None and len(context.selected_objects) > 1)
    
    def execute(self, context):
        return main(self.option)


class MakeTrueParentMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_make_true_parent"
    bl_label = "Make True Parent"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.make_true_parent", text="Keep Visual Transformations").option = "KEEP_VISUAL_TRANSFORMATIONS"
        layout.operator("object.make_true_parent", text="Reset Transformations").option = "RESET"
        layout.operator("object.make_true_parent", text="Keep Transformations Values").option = "KEEP_TRANSFORMATIONS_VALUES"
    
addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    addon_keymaps.clear()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode')
    kmi = km.keymap_items.new('wm.call_menu', 'P', 'PRESS', shift = True, ctrl = True, alt = True)
    kmi.properties.name = 'OBJECT_MT_make_true_parent'
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
