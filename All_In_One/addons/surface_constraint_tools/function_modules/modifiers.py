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

def apply_shrinkwrap(offset, target, wrap_method, affected_indices = list()):
    # Check the wrap_method parameter.
    if wrap_method not in {'PROJECT', 'NEAREST_SURFACEPOINT', 'NEAREST_VERTEX'}:
        raise Exception((
                "Invalid target argument '{0}' not found in " +
                "('PROJECT', 'NEAREST_SURFACEPOINT', 'NEAREST_VERTEX')"
            ).format(wrap_method)
        )

    context = bpy.context
    active_object = context.active_object
    initially_in_edit_mode = context.mode == 'EDIT_MESH'
    modifiers = active_object.modifiers

    # Enter Object mode, if necessary.
    if initially_in_edit_mode:
        bpy.ops.object.mode_set(mode = 'OBJECT')

    # Group the affected vertex indices.
    vertex_group = active_object.vertex_groups.new("Affected Indices")
    vertex_group.add(affected_indices, 1, 'ADD')

    # Add a shrinkwrap modifier to the active object.
    shrinkwrap_modifier = modifiers.new(name = "", type = 'SHRINKWRAP')
    shrinkwrap_modifier.offset = offset
    shrinkwrap_modifier.target = bpy.data.objects[target]
    shrinkwrap_modifier.use_keep_above_surface = True
    shrinkwrap_modifier.use_negative_direction = True
    shrinkwrap_modifier.vertex_group = vertex_group.name
    shrinkwrap_modifier.wrap_method = wrap_method

    # Move the shrinkwrap modifier to the top of the stack.
    while modifiers[0] != shrinkwrap_modifier:
        bpy.ops.object.modifier_move_up(
            modifier = shrinkwrap_modifier.name
        )

    # Apply the shrinkwrap modifier.
    bpy.ops.object.modifier_apply(modifier = shrinkwrap_modifier.name)

    # Delete the vertex group.
    active_object.vertex_groups.remove(vertex_group)

    # Return to Edit mode, if necessary.
    if initially_in_edit_mode:
        bpy.ops.object.mode_set(mode = 'EDIT')

def apply_smooth(iterations, affected_indices = list()):
    context = bpy.context
    active_object = context.active_object
    initially_in_edit_mode = context.mode == 'EDIT_MESH'
    modifiers = active_object.modifiers

    # Group the affected vertex indices.
    if active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode = 'OBJECT')
    vertex_group = active_object.vertex_groups.new("Affected Indices")
    vertex_group.add(affected_indices, 1, 'ADD')

    # Add a smooth modifier to the active object.
    smooth_modifier = modifiers.new(name = "", type = 'SMOOTH')
    smooth_modifier.factor = 1.0
    smooth_modifier.iterations = iterations
    smooth_modifier.vertex_group = vertex_group.name

    # Move the smooth modifier to the top of the stack.
    while modifiers[0] != smooth_modifier:
        bpy.ops.object.modifier_move_up(modifier = smooth_modifier.name)

    # Apply the smooth modifier.
    bpy.ops.object.modifier_apply(modifier = smooth_modifier.name) 

    # Delete the vertex group.
    active_object.vertex_groups.remove(vertex_group) 

    # Return to Edit mode, if necessary.
    if initially_in_edit_mode:
        bpy.ops.object.mode_set(mode = 'EDIT')