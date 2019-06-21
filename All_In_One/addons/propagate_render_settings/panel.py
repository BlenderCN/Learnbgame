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
from bpy.props import BoolProperty, StringProperty

class RENDER_PT_propagate(bpy.types.Panel):
    bl_label = "Propagate Render Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("scene.propagate_render_settings")

        row = layout.row()
        row.prop(context.scene, "propagate_filter_scene")

        row = layout.row()
        row.prop(context.scene, "propagate_scale")

        row = layout.row()
        row.prop(context.scene, "propagate_res")

        row = layout.row()
        row.prop(context.scene, "propagate_osa")

        row = layout.row()
        row.prop(context.scene, "propagate_threads")

        row = layout.row()
        row.prop(context.scene, "propagate_fields")

        row = layout.row()
        row.prop(context.scene, "propagate_stamp")

