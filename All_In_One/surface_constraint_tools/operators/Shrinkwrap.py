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
from ..auxiliary_classes.VertexFilter import VertexFilter
from ..auxiliary_classes.VertexProperties import VertexProperties
from ..function_modules.modifiers import apply_shrinkwrap

class Shrinkwrap(bpy.types.Operator):
    bl_idname = "mesh.sct_shrinkwrap"
    bl_label = "Shrinkwrap"
    bl_options = {'UNDO'}
    bl_description =\
        "Shrinkwrap the mesh's vertices to the surface constraint's target."

    addon_key = __package__.split(".")[0]

    @classmethod
    def poll(cls, context):
        # An active mesh object in Edit mode is required, and the surface
        # constraint's target must exist and not reference the active object.
        # Additionally, the operator is only valid in a 'VIEW_3D' space.
        active_object = context.active_object
        addon = bpy.context.user_preferences.addons[cls.addon_key]
        target = addon.preferences.surface_constraint.target
        return (
            active_object and
            active_object.type == 'MESH' and
            active_object.mode == 'EDIT' and
            target and
            target in bpy.data.objects and
            target != active_object.name and
            context.space_data.type == 'VIEW_3D'
        )

    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]
        self.props = self.addon.preferences.shrinkwrap

    def execute(self, context):
        active_object = context.active_object
        preferences = self.addon.preferences
        props = self.props
        surface_constraint_props = preferences.surface_constraint
        vertices = active_object.data.vertices

        # Disable automatic shrinkwrapping for the duration of this operator.
        initially_auto_shrinkwrap_is_enabled =\
            surface_constraint_props.auto_shrinkwrap_is_enabled
        if initially_auto_shrinkwrap_is_enabled:
            surface_constraint_props.auto_shrinkwrap_is_enabled = False

        # Write Edit mode's data to the mesh object.
        active_object.update_from_editmode()

        # Determine the affected vertex indices.
        properties = {'HIDDEN'}
        if props.only_selected_are_affected:
            properties.add('SELECTED')
        vertex_properties = VertexProperties()
        vertex_properties.mesh_object = active_object
        vertex_properties.determine_indices(properties)
        vertex_filter = VertexFilter()
        vertex_filter.indices = list(range(len(vertices)))
        vertex_filter.discard_indices(vertex_properties.hidden_indices)
        if props.only_selected_are_affected:
            vertex_filter.retain_indices(vertex_properties.selected_indices)
        vertex_indices = vertex_filter.indices

        # Only proceed if at least one vertex remains following the filtration
        # steps.
        if not vertex_indices: 
            # Reactivate automatic shrinkwrapping, if necessary.
            if initially_auto_shrinkwrap_is_enabled:
                surface_constraint_props.auto_shrinkwrap_is_enabled = True

            return {'CANCELLED'}

        # Shrinkwrap the vertices to the surface constraint's target.
        apply_shrinkwrap(
            offset = surface_constraint_props.offset,
            target = surface_constraint_props.target,
            wrap_method = surface_constraint_props.wrap_method_map[
                surface_constraint_props.direction
            ],
            affected_indices = vertex_indices
        )

        # Reactivate automatic shrinkwrapping, if necessary.
        if initially_auto_shrinkwrap_is_enabled:
            surface_constraint_props.auto_shrinkwrap_is_enabled = True

        return {'FINISHED'}