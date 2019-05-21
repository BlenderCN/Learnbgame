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
    "author": "poor & jendabek@gmail.com",
    "version": (0, 5),
    "blender": (2, 80, 0),
    "location": "3D View",
    "category": "Learnbgame",
}


class ViewportRenameOperator(bpy.types.Operator):
    """Rename Objects in 3D View"""
    bl_idname = "view3d.viewport_rename"
    bl_label = "Viewport Rename (for batch, ## means 2 digits)"
    bl_options = {'REGISTER', 'UNDO'}
    type = bpy.props.StringProperty()
    start = bpy.props.IntProperty(default=0)
    data_flag = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        user_input = self.type
        start = self.start
        reverse = False
        if user_input.endswith("#r"):
            reverse = True
            user_input = user_input[:-1]

        suff = re.findall("#+$", user_input)
        if user_input and suff:
            number = ('%0'+str(len(suff[0])) + 'd', len(suff[0]))
            real_name = re.sub("#", '', user_input)

            objs = context.selected_objects
            objs.sort(key=lambda o: o.name)
            names_before = [n.name for n in objs]
            for c, o in enumerate(objs, start):
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
        self.type = context.active_object.name
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "type", text="New Name")
        row.prop(self, "start", text="Start Index")
        row.prop(self, "data_flag", text="Rename Data-Block")


# ------------------------------------------------------------------------
#    register and unregister functions
# ------------------------------------------------------------------------

addon_keymaps = []


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
