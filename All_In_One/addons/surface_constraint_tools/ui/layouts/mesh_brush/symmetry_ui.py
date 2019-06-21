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

def draw_symmetry_ui(layout):
    addon = bpy.context.user_preferences.addons[__package__.split(".")[0]]
    props = addon.preferences.mesh_brush

    col = layout.column()
    row = col.row(align = True)

    if not props.symmetry_ui_is_visible:
        op = row.operator(
            "wm.context_toggle", text = "", icon = 'DISCLOSURE_TRI_RIGHT',
            emboss = False
        )
        op.data_path = "{0}.symmetry_ui_is_visible".format(props.data_path)
        row.label(text = "Symmetry") 
    else:
        row.operator(
            "wm.context_toggle", text = "", icon = 'DISCLOSURE_TRI_DOWN',
            emboss = False
        ).data_path = "{0}.symmetry_ui_is_visible".format(props.data_path)
        row.label(text = "Symmetry")

        subcol = col.column(align = True)
        row = subcol.row(align = True)

        row.prop(props, "symmetry_type", expand = True)

        row = subcol.row(align = True)

        row.prop(
            props, "x_axis_symmetry_is_enabled", text = "X", toggle = True
        )
        row.prop(
            props, "y_axis_symmetry_is_enabled", text = "Y", toggle = True
        )
        row.prop(
            props, "z_axis_symmetry_is_enabled", text = "Z", toggle = True
        )

        if props.symmetry_type == 'RADIAL':
            row = subcol.row(align = True)

            row.prop(props, "radial_count", text = "Count")

        col.separator()