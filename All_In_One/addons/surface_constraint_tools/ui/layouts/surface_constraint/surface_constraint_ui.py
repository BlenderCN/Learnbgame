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

def draw_surface_constraint_ui(layout):
    addon = bpy.context.user_preferences.addons[__package__.split(".")[0]]
    props = addon.preferences.surface_constraint

    if not props.settings_ui_is_visible:
        box = layout.box()
        row = box.row()

        op = row.operator(
            "wm.context_toggle", text = "", icon = 'TRIA_RIGHT', emboss = False
        )
        op.data_path = "{0}.settings_ui_is_visible".format(props.data_path)
        row.label("Surface Constraint")
        row.operator(
            "view3d.sct_pick_surface_constraint", text = "", icon = 'HAND'
        )
    else:
        col = layout.column(align = True)
        box = col.box()
        row = box.row()

        op = row.operator( 
            "wm.context_toggle", text = "", icon = 'TRIA_DOWN', emboss = False
        )
        op.data_path = "{0}.settings_ui_is_visible".format(props.data_path)
        row.label("Surface Constraint") 
        row.operator(
            "view3d.sct_pick_surface_constraint", text = "", icon = 'HAND'
        )

        # Generate a collection of mesh objects that are available as targets
        # for the surface constraint.
        available_targets = props.available_targets
        available_targets.clear()
        for object in bpy.context.scene.objects:
            if object.type == 'MESH':
                item = available_targets.add()
                item.name = object.name

        # Ensure that the surface constraint's target is still among the
        # collection of available targets.
        if props.target:
            if props.target not in props.available_targets:
                props.target = str()

        box = col.box()
        col = box.column(align = True)
        row = col.row(align = True)
        subrow = row.row(align = True)

        active_object = bpy.context.active_object
        if not (
            active_object and
            active_object.type == 'MESH' and
            props.target and
            props.target != active_object.name
           ):
            subrow.active = False

        subrow.prop(
            props, "auto_shrinkwrap_is_enabled", text = "", icon = 'AUTO'
        )
        row.prop_search(
            props, "target", props, "available_targets", text = "",
            icon = 'OBJECT_DATA'
        )

        row = col.row(align = True)

        row.prop_menu_enum(props, "direction", text = "", icon = 'SNAP_NORMAL')
        row.prop(props, "offset", text = "Offset")