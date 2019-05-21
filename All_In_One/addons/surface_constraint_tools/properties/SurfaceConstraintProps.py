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
from ..function_modules import auto_shrinkwrap_handlers

class SurfaceConstraintProps(bpy.types.PropertyGroup):
    data_path =(
        "user_preferences.addons['{0}'].preferences.surface_constraint"
    ).format(__package__.split(".")[0])

    def update_auto_shrinkwrap(self, context):
        handlers = bpy.app.handlers
        load_pre = handlers.load_pre
        save_pre = handlers.save_pre
        save_post = handlers.save_post
        scene_update_pre = handlers.scene_update_pre

        # Automatic shrinkwrapping has been enabled.
        if self.auto_shrinkwrap_is_enabled:
            # Ensure that automatic shrinkwrapping is not paused.
            if self.auto_shrinkwrap_is_paused:
                self.auto_shrinkwrap_is_paused = False

            # Add the relevant handlers.  Do not append duplicates.

            # Ensure that an auto shrinkwrap pre scene update handler is
            # present.
            if (
                auto_shrinkwrap_handlers.scene_update_pre not in
                scene_update_pre
            ):
                scene_update_pre.append(
                    auto_shrinkwrap_handlers.scene_update_pre
                )

            # Ensure that blend file saving handlers are present to manage the
            # state of automatic shrinkwrapping before and after saving.  These
            # handlers persist until the current blend file is closed.
            if auto_shrinkwrap_handlers.save_pre not in save_pre:
                save_pre.append(auto_shrinkwrap_handlers.save_pre)
            if auto_shrinkwrap_handlers.save_post not in save_post:
                save_post.append(auto_shrinkwrap_handlers.save_post)

            # Ensure that a blend file loading handler is present to manage
            # the state of automatic shrinkwrapping before loading a blend
            # file.  This handler persists until the current blend file is
            # closed.
            if auto_shrinkwrap_handlers.load_pre not in load_pre:
                load_pre.append(auto_shrinkwrap_handlers.load_pre)

        # Automatic shrinkwrapping has been disabled.
        else:
            # Remove all auto shrinkwrap pre scene update handlers.
            i = len(scene_update_pre)
            while i:
                i -= 1
                if (
                    scene_update_pre[i] ==
                    auto_shrinkwrap_handlers.scene_update_pre
                ):
                    scene_update_pre[-1], scene_update_pre[i] = (
                        scene_update_pre[i], scene_update_pre[-1]
                    )
                    scene_update_pre.pop()

        # Attempt to apply the referenced modifier on the active object.
        active_object = bpy.context.active_object
        modifier_uid = self.modifier_uid
        if active_object and modifier_uid:
            modifier_uid_map = {
                str(modifier.as_pointer()) : modifier
                for modifier in active_object.modifiers
            }
            if modifier_uid in modifier_uid_map:
                modifier = modifier_uid_map[modifier_uid]

                # Apply the modifier.
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.modifier_apply(modifier = modifier.name)
                bpy.ops.object.mode_set(mode = 'EDIT')

    # Surface Constraint Settings
    available_targets =\
        bpy.props.CollectionProperty(type = bpy.types.PropertyGroup)
    auto_shrinkwrap_is_enabled = bpy.props.BoolProperty(
        name = "Auto Shrinkwrap",
        description = (
            "Maintain a shrinkwrap modifier on the active mesh object, and " +
            "reapply it after the end of each operation."
        ),
        default = False,
        update = update_auto_shrinkwrap
    )
    auto_shrinkwrap_is_enabled_pre_save = bpy.props.BoolProperty(
        description = (
            "Indicate whether or not automatic shrinkwrapping is enabled " +
            "prior to saving the blend file."
        ),
        default = False
    )
    auto_shrinkwrap_is_paused = bpy.props.BoolProperty(
        description =\
            "Control the execution of the auto shrinkwrap handler.",
        default = False
    )
    direction = bpy.props.EnumProperty(
        name = "Shrinkwrap Direction",
        description = (
            "Shrinkwrap along vertex normals or towards the closest points " +
            "on the target object."
        ),
        default = 'CLOSEST_POINT',
        items = [
            ('CLOSEST_POINT', "Closest Point", ""),
            ('VERTEX_NORMAL', "Vertex Normal", "")
        ]
    )
    offset = bpy.props.FloatProperty(
        name = "Offset",
        description = (
            "Distance to keep constrained vertices offset from the target " +
            "mesh object's surface"
        ),
        default = 0.0,
        step = 1
    )
    target = bpy.props.StringProperty(
        name = "Target",
        description = (
            "Target object to which the active mesh object's vertices are " +
            "constrained"
        )
    )
    wrap_method_map =\
        {'CLOSEST_POINT' : 'NEAREST_SURFACEPOINT', 'VERTEX_NORMAL' : 'PROJECT'}

    # Unique Identifiers
    mesh_object_uid = bpy.props.StringProperty()
    modifier_uid = bpy.props.StringProperty()
    operator_uid = bpy.props.StringProperty()

    # UI Visibility
    settings_ui_is_visible = bpy.props.BoolProperty(
        name = "Settings UI Visibility",
        description = "Show/hide the Settings UI.",
        default = False
    )
