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

addon = bpy.context.user_preferences.addons[__package__.split(".")[0]]

def load_pre(scene):
    # Disable automatic shrinkwrapping before saving.
    props = addon.preferences.surface_constraint
    if props.auto_shrinkwrap_is_enabled:
        props.auto_shrinkwrap_is_enabled = False

def save_post(scene):
    # If automatic shrinkwrapping was enabled prior to saving, reactivate it.
    props = addon.preferences.surface_constraint
    if props.auto_shrinkwrap_is_enabled_pre_save:
        props.auto_shrinkwrap_is_enabled = True

def save_pre(scene):
    # Disable automatic shrinkwrapping before saving.
    props = addon.preferences.surface_constraint
    props.auto_shrinkwrap_is_enabled_pre_save =\
        props.auto_shrinkwrap_is_enabled
    if props.auto_shrinkwrap_is_enabled_pre_save:
        props.auto_shrinkwrap_is_enabled = False

def scene_update_pre(scene):
    props = addon.preferences.surface_constraint

    # Exit this handler early if it is paused.
    if props.auto_shrinkwrap_is_paused:
        return

    # Pause additional event handling in order to avoid recursion caused by a
    # scene update being triggered while processing this handler.
    props.auto_shrinkwrap_is_paused = True

    active_object = bpy.context.active_object
    target = props.target

    # There are five cases that may require the referenced modifier to be
    # removed, if a reference to it exists.
    # 1: An active object does not exist.
    # 2: The active object is not in Edit mode.
    # 3: The active object is not the referenced object.
    # 4: No target exists.
    # 5: The active object is the target.
    if (
        props.modifier_uid and (
            not active_object or
            active_object.mode != 'EDIT' or
            str(active_object.as_pointer()) != props.mesh_object_uid or
            not target or
            target == active_object.name
        )
    ):
        # Attempt to find the referenced mesh object.
        object_uid_map = {
            str(object_.as_pointer()) : object_ for object_ in bpy.data.objects
        }
        if props.mesh_object_uid in object_uid_map:
            referenced_object = object_uid_map[props.mesh_object_uid]

            # Attempt to remove the referenced modifier.
            modifier_uid_map = {
                str(modifier.as_pointer()) : modifier
                for modifier in referenced_object.modifiers
            }
            if props.modifier_uid in modifier_uid_map:
                referenced_object.modifiers.remove(
                    modifier_uid_map[props.modifier_uid]
                )

        # Clear the unique identifiers.
        props.mesh_object_uid = ""
        props.modifier_uid = ""

    # Ensure that an appropriate shrinkwrap modifier exists on the active
    # object, provided that all of the following criteria are satisfied:
    # 1: An active object exists.
    # 2: the active object is in Edit mode.
    # 3: The active object is a mesh.
    # 4: The target exists.
    # 5: The active object is not the target.
    if (
        active_object and
        active_object.mode == 'EDIT' and
        active_object.type == 'MESH' and
        target and
        target != active_object.name
    ):
        offset = props.offset
        wrap_method = props.wrap_method_map[props.direction]

        # Record a unique identifier for the active mesh object, if necessary.
        if not props.mesh_object_uid:
            props.mesh_object_uid = str(active_object.as_pointer())

        # If a reference to the modifier exists, create a mapping between
        # unique identifiers and the active object's modifiers.
        if props.modifier_uid:
            modifier_uid_map = {
                str(modifier.as_pointer()) : modifier
                for modifier in active_object.modifiers
            }

        # If the modifier is not referenced, or the referenced modifier does
        # not exist, add a shrinkwrap modifier to the top of the stack, and
        # record its unique identifier.
        if (
            not props.modifier_uid or
            props.modifier_uid not in modifier_uid_map
        ):
            # Add a shrinkwrap modifier to the active mesh object.
            modifier = active_object.modifiers.new(
                name = "Surface Constraint Preview", type = 'SHRINKWRAP'
            )
            modifier.offset = offset
            modifier.show_expanded = False
            modifier.show_viewport = True
            modifier.show_in_editmode = True
            modifier.show_on_cage = True
            modifier.target = bpy.data.objects[target]
            modifier.use_keep_above_surface = True
            modifier.use_negative_direction = True
            modifier.wrap_method = wrap_method

            # Move the modifier to the top of the stack.
            while active_object.modifiers[0] != modifier:
                bpy.ops.object.modifier_move_up(modifier = modifier.name)

            # Record a unique identifier for the modifier.
            props.modifier_uid = str(modifier.as_pointer())

        # Otherwise, validate the existing, referenced modifier.
        else:
            modifier = modifier_uid_map[props.modifier_uid]

            # Validate the modifier's properties.
            if modifier.offset != offset:
                modifier.offset = offset
            if modifier.show_expanded != False:
                modifier.show_expanded = False
            if modifier.show_viewport != True:
                modifier.show_viewport = True
            if modifier.show_in_editmode != True:
                modifier.show_in_editmode = True
            if modifier.show_on_cage != True:
                modifier.show_on_cage = True
            if modifier.target != bpy.data.objects[target]:
                modifier.target = bpy.data.objects[target]
            if modifier.use_keep_above_surface != True:
                modifier.use_keep_above_surface = True
            if modifier.use_negative_direction != True:
                modifier.use_negative_direction = True
            if modifier.wrap_method != wrap_method:
                modifier.wrap_method = wrap_method

            # Move the modifier to the top of the stack.
            while active_object.modifiers[0] != modifier:
                bpy.ops.object.modifier_move_up(modifier = modifier.name)

        # Determine if the modifier needs to be applied.

        # The contextual "active_operator" attribute references the most recent
        # registered, undoable operator that returned 'FINISHED'.  This
        # attribute's value will change when the next valid operator finishes.
        active_operator = bpy.context.active_operator

        # Compare the current active operator's unique ID with that of the
        # stored operator.  Inequality indicates that a more recent operator
        # has finished.
        if (
            active_operator and
            str(active_operator.as_pointer()) != props.operator_uid
        ):
            # Apply the modifier.
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_apply(modifier = modifier.name)
            bpy.ops.object.mode_set(mode = 'EDIT')

            # Record a unique identifier for the most recently finished
            # operator.
            props.operator_uid = str(active_operator.as_pointer())

    # Resume the event handling.
    props.auto_shrinkwrap_is_paused = False
