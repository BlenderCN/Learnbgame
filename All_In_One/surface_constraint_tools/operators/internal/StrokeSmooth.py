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

# <pep8-80 compliant

import bpy
from mathutils import Vector
from ..MeshBrush import MeshBrush
from ...function_modules.modifiers import apply_shrinkwrap
from ...function_modules.modifiers import apply_smooth

class StrokeSmoothBrush(bpy.types.Operator):
    bl_idname = "mesh.sct_stroke_smooth"
    bl_label = "Stroke Smooth Brush"
    bl_options = {'INTERNAL'}

    addon_key = __package__.split(".")[0]

    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]
        self.props = self.addon.preferences.mesh_brush 

    def dab(self):
        active_object = bpy.context.active_object
        preferences = self.addon.preferences
        props = self.props 
        brushes = props.brushes
        primary_brush = brushes.primary_brush
        derived_brushes = brushes.derived_brushes
        vertices = active_object.data.vertices

        # The primary brush must be on the mesh in order to execute a dab.
        if not primary_brush.is_on_mesh:
            return

        # Determine which vertex indices are affected by the dab.
        indices_affected_by_dab = set()
        for brush in [primary_brush] + derived_brushes:
            indices_affected_by_dab.update(brush.indices)

        # Only proceed if at least one vertex is affected by the dab.
        if not indices_affected_by_dab:
            return

        # Record the pre-dab coordinates of the affected vertex indices.
        pre_dab_object_space_map = {
            index : vertices[index].co.copy()
            for index in indices_affected_by_dab
        }

        # Apply a smoothing operation to the affected vertex indices.
        apply_smooth(
            iterations = props.iterations,
            affected_indices = list(indices_affected_by_dab)
        )

        # Apply falloff to the result of the smoothing operation, if necessary.
        if props.falloff_curve.profile != 'CONSTANT':
            # With multiple brushes, brush volumes can overlap, and one or more
            # indices may have multiple falloff values associated with it.
            if derived_brushes:
                # Create a combined falloff map from the brushes, ensuring that
                # each index maps to its most intense falloff value.
                falloff_map = dict()
                for brush in [primary_brush] + derived_brushes:
                    brush_falloff_map = brush.falloff_map
                    for index in brush_falloff_map:
                        if (
                            index not in falloff_map or
                            falloff_map[index] < brush_falloff_map[index]
                        ):
                            falloff_map[index] = brush_falloff_map[index]

            # Brush volume overlap is not a concern if only the primary brush
            # exists.
            else:
                falloff_map = primary_brush.falloff_map

            # Apply the falloff by interpolating between the pre-dab and
            # post-dab coordinates.
            for index in indices_affected_by_dab:
                co = vertices[index].co
                falloff = falloff_map[index]
                vertices[index].co = falloff * co + (1 - falloff) * (
                    pre_dab_object_space_map[index]
                )

        # Constrain the vertices to the specified target, if necessary.
        if self.target:
            surface_constraint_props = self.surface_constraint_props
            apply_shrinkwrap(
                offset = self.offset, target = self.target,
                wrap_method = self.wrap_method,
                affected_indices = list(indices_affected_by_dab)
            )

        # Record the post-dab coordinates of the affected vertex indices.
        post_dab_object_space_map = {
            index : vertices[index].co.copy()
            for index in indices_affected_by_dab
        }

        # Update the octree.
        model_matrix = active_object.matrix_world
        world_space_submap = {
            index : model_matrix * post_dab_object_space_map[index]
            for index in indices_affected_by_dab
        }
        octree = props.octree
        octree.coordinate_map.update(world_space_submap)
        octree.insert_indices(indices_affected_by_dab)

        # Update the stroke displacement map.
        stroke_displacement_submap = {
            index : post_dab_object_space_map[index] - (
                        pre_dab_object_space_map[index]
                    )
            for index in indices_affected_by_dab
        }
        stroke_displacement_map = self.stroke_displacement_map
        for index in indices_affected_by_dab:
            if index in stroke_displacement_map:
                stroke_displacement_map[index] +=\
                    stroke_displacement_submap[index]
            else:
                stroke_displacement_map[index] =\
                    stroke_displacement_submap[index]

    def finish(self):
        props = self.props

        # If a duplicate of the active object was created and referenced as the
        # temporary target of the surface constraint, delete it.
        if self.target != self.surface_constraint_props.target:
            target_object = bpy.data.objects[self.target]
            mesh_data = target_object.data
            bpy.context.scene.objects.unlink(target_object)
            bpy.data.objects.remove(target_object)
            bpy.data.meshes.remove(mesh_data)

        # Push any changes caused by the stroke to the undo stack.
        if self.stroke_displacement_map:
            # Clear the redo stack.
            props.redo_stack.clear()

            # Push the stroke displacement map to the undo stack.
            props.undo_stack.append(self.stroke_displacement_map) 

    def invoke(self, context, event): 
        # Record the object space displacement of each vertex affected by the
        # stroke.
        self.stroke_displacement_map = dict()

        # If the target is also the mesh object that is being operated upon,
        # create a duplicate of it, and reference the duplicate as the
        # temporary target of the surface constraint.
        surface_constraint_props = self.addon.preferences.surface_constraint
        self.surface_constraint_props = surface_constraint_props
        self.offset = surface_constraint_props.offset
        self.target = surface_constraint_props.target
        self.wrap_method = surface_constraint_props.wrap_method_map[
            surface_constraint_props.direction
        ]
        if self.target:
            active_object = context.active_object
            if bpy.data.objects[self.target] == active_object:
                # Duplicate the active object.
                mesh_data = active_object.data.copy()
                temp_target = bpy.data.objects.new(
                    "Temporary Surface Constraint", mesh_data
                )
                temp_target.location = active_object.location
                temp_target.rotation_axis_angle =\
                    active_object.rotation_axis_angle
                temp_target.rotation_quaternion =\
                    active_object.rotation_quaternion
                temp_target.rotation_euler =\
                    active_object.rotation_euler
                temp_target.rotation_mode = active_object.rotation_mode
                temp_target.scale = active_object.scale
                temp_target.hide = True
                context.scene.objects.link(temp_target)

                # Set the temporary target of the surface constraint.
                self.target =  temp_target.name

        # Execute the first dab, and record its position.
        self.dab()
        self.previous_dab_position =\
            Vector((event.mouse_region_x, event.mouse_region_y))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        props = self.props
        context.region.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.move_brush(event.mouse_region_x, event.mouse_region_y)

            # Determine the distance between the mouse cursor's position and
            # previous dab's position.
            mouse_cursor_co =\
                Vector((event.mouse_region_x, event.mouse_region_y))
            distance = (mouse_cursor_co - self.previous_dab_position).length
            relative_distance = distance / props.radius * 100

            # Execute a dab if the relative distance is greater than the user
            # defined interval.
            if relative_distance > props.spacing:
                self.dab()
                self.previous_dab_position = mouse_cursor_co

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.move_brush(event.mouse_region_x, event.mouse_region_y)

            self.finish()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    # Reference the ability to move the mesh brush upon completion of the
    # stroke.
    move_brush = MeshBrush.move_brush