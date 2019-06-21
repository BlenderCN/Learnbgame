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

# <pep8-80 compliant>

import bpy

def draw_smooth_vertices_ui(layout):
    addon = bpy.context.user_preferences.addons[__package__.split(".")[0]]
    props = addon.preferences.smooth_vertices

    if not props.settings_ui_is_visible:
        box = layout.box()
        row = box.row()

        op = row.operator(
            "wm.context_toggle", text = "", icon = 'TRIA_RIGHT', emboss = False
        )
        op.data_path = "{0}.settings_ui_is_visible".format(props.data_path)
        row.label("Smooth Vertices")
        row.operator(
            "mesh.sct_smooth_vertices", text = "", icon = 'MOD_SMOOTH'
        )
    else:
        col = layout.column(align = True)
        box = col.box()
        row = box.row()

        op = row.operator( 
            "wm.context_toggle", text = "", icon = 'TRIA_DOWN', emboss = False
        )
        op.data_path = "{0}.settings_ui_is_visible".format(props.data_path)
        row.label("Smooth Vertices") 
        row.operator(
            "mesh.sct_smooth_vertices", text = "", icon = 'MOD_SMOOTH'
        )

        box = col.box()

        box.prop(props, "iterations")

        col = box.column(align = True)

        col.prop(props, "boundary_is_locked")
        col.prop(props, "only_selected_are_affected")