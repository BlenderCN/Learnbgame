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

def draw_falloff_ui(layout):
    addon = bpy.context.user_preferences.addons[__package__.split(".")[0]]
    props = addon.preferences.mesh_brush

    col = layout.column()
    row = col.row(align = True)

    if not props.falloff_ui_is_visible:
        op = row.operator(
            "wm.context_toggle", text = "", icon = 'DISCLOSURE_TRI_RIGHT',
            emboss = False
        )
        op.data_path = "{0}.falloff_ui_is_visible".format(props.data_path)
        row.label(text = "Falloff") 
    else:
        op = row.operator(
            "wm.context_toggle", text = "", icon = 'DISCLOSURE_TRI_DOWN',
            emboss = False
        )
        op.data_path = "{0}.falloff_ui_is_visible".format(props.data_path)
        row.label(text = "Falloff")

        row = col.row()

        row.prop(props, "falloff_profile", expand = True, icon_only = True)
        row.alignment = 'CENTER'
        col.separator()