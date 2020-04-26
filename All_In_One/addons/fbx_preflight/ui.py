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

import bpy


class ExportObjectUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        # We could write some code to decide which icon to use here...
        label = self.label_for_object_name(obj=item.obj_pointer)
        icon = self.icon_for_object_name(obj=item.obj_pointer)
        layout.label(label, icon=icon)

    def label_for_object_name(self, obj):

        if obj is not None:
            return "{0} ({1})".format(obj.name, obj.type)
        return "(unset)"

    def icon_for_object_name(self, obj):

        if obj is None:
            return "ERROR"
        if not obj.name:
            return "QUESTION"

        if obj.type == "LAMP":
            return "LAMP"
        if obj.type == "ARMATURE":
            return "ARMATURE_DATA"
        if obj.type == "MESH":
            return "MESH_DATA"
        if obj.type == "CAMERA":
            return "CAMERA_DATA"

        return 'OBJECT_DATAMODE'
