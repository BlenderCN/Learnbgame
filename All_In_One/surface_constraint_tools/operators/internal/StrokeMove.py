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

class StrokeMove(bpy.types.Operator):
    bl_idname = "mesh.sct_stroke_move"
    bl_label = "Stroke Move"
    bl_options = {'INTERNAL'}

    addon_key = __package__.split(".")[0]

    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]
        self.props = self.addon.preferences.mesh_brush

    def finish(self):
        active_object = bpy.context.active_object
        props = self.props
        indices_affected_by_stroke = self.indices_affected_by_stroke
        vertices = active_object.data.vertices

        # If a duplicate of the active object was created and referenced as the
        # temporary target of the surface constraint, delete it.
        if self.target != self.surface_constraint_props.target:
            target_object = bpy.data.objects[self.target]
            mesh_data = target_object.data
            bpy.context.scene.objects.unlink(target_object)
            bpy.data.objects.remove(target_object)
            bpy.data.meshes.remove(mesh_data)

        # Update the octree.
        model_matrix = active_object.matrix_world
        world_space_submap = {
            index : model_matrix * vertices[index].co.copy()
            for index in indices_affected_by_stroke
        }
        octree = props.octree
        octree.coordinate_map.update(world_space_submap)
        octree.insert_indices(indices_affected_by_stroke)

        # Map each affected vertex index to a displacement vector between
        # its post-stroke and pre-stroke positions.
        pre_stroke_object_space_map = self.pre_stroke_object_space_map
        stroke_displacement_map = {
            index : vertices[index].co - pre_stroke_object_space_map[index]
            for index in indices_affected_by_stroke
        }

        # Push any changes caused by the stroke to the undo stack.
        if stroke_displacement_map:
            # Clear the redo stack.
            props.redo_stack.clear()

            # Push the stroke displacement map to the undo stack.
            props.undo_stack.append(stroke_displacement_map)

        # Enable the brush graphic, if necessary.
        if props.brush_is_visible:
            props.brush_graphic.is_enabled = True

    def invoke(self, context, event):
        active_object = bpy.context.active_object
        props = self.props
        brushes = props.brushes
        primary_brush = brushes.primary_brush
        derived_brushes = brushes.derived_brushes
        vertices = active_object.data.vertices

        # Determine which vertex indices are affected by the stroke.
        indices_affected_by_stroke = set()
        for brush in [primary_brush] + derived_brushes:
            indices_affected_by_stroke.update(brush.indices)
        self.indices_affected_by_stroke = indices_affected_by_stroke

        # Record the pre-stroke coordinates of the affected vertex indices.
        self.pre_stroke_object_space_map = {
            index : vertices[index].co.copy()
            for index in indices_affected_by_stroke
        }

        # Record the stroke' z-depth.
        perspective_matrix = bpy.context.region_data.perspective_matrix
        co = primary_brush.center.resized(4)
        co.w = 1
        co = perspective_matrix * co
        self.stroke_z_depth = co.z / co.w

        # If the target is also the mesh object that is being operated upon,
        # create a duplicate of it, and reference the duplicate as the
        # temporary target of the surface constraint.
        surface_constraint_props = self.addon.preferences.surface_constraint
        self.offset = surface_constraint_props.offset
        self.target = surface_constraint_props.target
        self.surface_constraint_props = surface_constraint_props
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

        # Disable the brush graphic, if necessary.
        if props.brush_is_visible:
            props.brush_graphic.is_enabled = False

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.region.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.stroke(event.mouse_region_x, event.mouse_region_y)

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.move_brush(event.mouse_region_x, event.mouse_region_y)

            self.finish()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    # Reference the ability to move the mesh brush upon completion of the
    # stroke.
    move_brush = MeshBrush.move_brush

    def stroke(self, region_x, region_y):
        props = self.props
        brushes = props.brushes
        derived_brushes = brushes.derived_brushes
        primary_brush = brushes.primary_brush

        active_object = bpy.context.active_object
        indices_affected_by_stroke = self.indices_affected_by_stroke
        vertices = active_object.data.vertices

        # The primary brush must be on the mesh in order to execute a stroke.
        if not primary_brush.is_on_mesh:
            return

        # Only proceed if at least one vertex is affected by the stroke.
        if not indices_affected_by_stroke:
            return

        # Determine the terminal position of the stroke in world space
        # coordinates.
        inverted_perspective_matrix =\
            bpy.context.region_data.perspective_matrix.inverted()
        co = Vector((region_x, region_y))
        co.x = co.x * 2 / bpy.context.region.width - 1
        co.y = co.y * 2 / bpy.context.region.height - 1
        co.resize(4)
        co.z = self.stroke_z_depth
        co.w = 1
        co = inverted_perspective_matrix * co
        w = co.w
        co.resize(3)
        co /= w
        stroke_terminal_co = co

        # Apply the stroke to each brush.
        inverted_model_matrix = active_object.matrix_world.inverted()
        for brush in [primary_brush] + brushes.derived_brushes:
            # Determine the displaced position of the brush caused by the
            # stroke.
            displaced_brush_center =\
                brush.transformation_matrix * stroke_terminal_co

            # Calculate an object space displacement vector between the brush's
            # original position and its displaced position.
            object_space_displacement = (
                inverted_model_matrix *  displaced_brush_center -
                inverted_model_matrix * brush.center
            )

            # Move the brush to its displaced position.
            brush.center = displaced_brush_center

            # Add the displacement vector to the coordinates of the brush's
            # affected vertices, taking into account brush falloff.
            falloff_map = brush.falloff_map
            for index in brush.indices:
                vertices[index].co +=\
                    falloff_map[index] * object_space_displacement

        # Constrain the vertices to the specified target, if necessary.
        if self.target:
            surface_constraint_props = self.surface_constraint_props
            apply_shrinkwrap(
                offset = self.offset, target = self.target,
                wrap_method = surface_constraint_props.wrap_method_map[
                    surface_constraint_props.direction
                ],
                affected_indices = list(indices_affected_by_stroke)
            )

        # Update the octree's coordinate map.
        model_matrix = active_object.matrix_world
        world_space_submap = {
            index : model_matrix * vertices[index].co
            for index in indices_affected_by_stroke
        }
        self.props.octree.coordinate_map.update(world_space_submap)