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
from .display_properties_ui import draw_display_properties_ui
from .falloff_ui import draw_falloff_ui
from .options_ui import draw_options_ui
from .symmetry_ui import draw_symmetry_ui

def draw_mesh_brush_ui(layout):
    addon = bpy.context.user_preferences.addons[__package__.split(".")[0]]
    props = addon.preferences.mesh_brush

    if not props.settings_ui_is_visible:
        box = layout.box()
        row = box.row()

        op = row.operator(
            "wm.context_toggle", text = "", icon = 'TRIA_RIGHT', emboss = False
        )
        op.data_path = "{0}.settings_ui_is_visible".format(props.data_path)
        row.label("Mesh Brush")
        row.operator("mesh.sct_mesh_brush", text = "", icon = 'BRUSH_DATA') 
    else:
        col = layout.column(align = True)
        box = col.box()
        row = box.row()

        op = row.operator( 
            "wm.context_toggle", text = "", icon = 'TRIA_DOWN', emboss = False
        )
        op.data_path = "{0}.settings_ui_is_visible".format(props.data_path)
        row.label("Mesh Brush") 
        row.operator("mesh.sct_mesh_brush", text = "", icon = 'BRUSH_DATA')

        box = col.box()

        box.prop(props, "iterations")
        box.prop(props, "radius", slider = True)
        box.prop(props, "spacing", slider = True)

        col = box.column(align = True)

        draw_display_properties_ui(col)
        draw_falloff_ui(col)
        draw_options_ui(col)
        draw_symmetry_ui(col)