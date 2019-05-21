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
# <pep8 compliant>

import bpy
import re

bl_info = {
    "name": "Viewport Rename",
    "author": "Christian Brinkmann (p2or)",
    "version": (0, 5),
    "blender" : (2, 80, 0),
    "location": "3D View > Ctrl+R",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/p2or/blender-viewport-rename",
    "tracker_url": "https://github.com/p2or/blender-viewport-rename/issues",
    "category": "Learnbgame",
}


class ViewportRenameOperator(bpy.types.Operator):
    """Rename selected object(s) in 3D View"""
    bl_idname = "view3d.viewport_rename"
    bl_label = "Viewport Rename"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "new_name"

    new_name : bpy.props.StringProperty(name="New Name")
    data_flag : bpy.props.BoolProperty(name="Rename Data-Block", default=False)

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        user_input = self.new_name
        reverse = False
        if user_input.endswith("#r"):
            reverse = True
            user_input = user_input[:-1]

        suff = re.findall("#+$", user_input)
        if user_input and suff:
            number = ('%0'+str(len(suff[0]))+'d', len(suff[0]))
            real_name = re.sub("#", '', user_input)           

            objs = context.selected_objects[::-1] if reverse else context.selected_objects
            names_before = [n.name for n in objs]
            for c, o in enumerate(objs, start=1):
                o.name = (real_name + (number[0] % c))
                if self.data_flag and o.data is not None:
                    o.data.name = (real_name + (number[0] % c))
            self.report({'INFO'}, "Renamed {}".format(", ".join(names_before)))
            return {'FINISHED'}

        elif user_input:
            old_name = context.active_object.name
            context.active_object.name = user_input
            if self.data_flag and context.active_object.data is not None:
                context.active_object.data.name = user_input
            self.report({'INFO'}, "{} renamed to {}".format(old_name, user_input))
            return {'FINISHED'}

        else:
            self.report({'INFO'}, "No input, operation cancelled")
            return {'CANCELLED'}

    def invoke(self, context, event):
        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = 450 * dpi * ui_size
        self.new_name = context.active_object.name
        return wm.invoke_props_dialog(self, width=dialog_size)

    def draw(self, context):
        row = self.layout
        row.row()
        row.prop(self, "new_name")
        row.prop(self, "data_flag")
        row.row()


# ------------------------------------------------------------------------
#    register, unregister and hotkey
# ------------------------------------------------------------------------

addon_keymaps = []

def register():
    from bpy.utils import register_class

    addon_keymaps.clear()
    register_class(ViewportRenameOperator)

    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(ViewportRenameOperator.bl_idname, type='R', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    from bpy.utils import unregister_class

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    unregister_class(ViewportRenameOperator)

if __name__ == "__main__":
    register()
