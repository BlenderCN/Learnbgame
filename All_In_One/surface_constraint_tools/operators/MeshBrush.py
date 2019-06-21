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

import bgl
import bpy
from ..auxiliary_classes.ModalHelper import ModalHelper
from ..auxiliary_classes.VertexProperties import VertexProperties

class MeshBrush(bpy.types.Operator):
    bl_idname = "mesh.sct_mesh_brush"
    bl_label = "Mesh Brush"
    bl_options = {'UNDO'}
    bl_description = (
        "Manipulate the mesh's vertices with a brush, constraining the " +
        "result if necessary."
    )

    addon_key = __package__.split(".")[0]

    @classmethod
    def poll(cls, context):
        # An active mesh object with polygons in Edit mode is required, and the
        # operator is only valid in a 'VIEW_3D' space.
        active_object = context.active_object
        return (
            active_object and
            active_object.type == 'MESH' and
            active_object.data.polygons and
            active_object.mode == 'EDIT' and
            context.space_data.type == 'VIEW_3D'
        )

    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]
        self.props = self.addon.preferences.mesh_brush 

    def draw_post_pixel_callback(self):
        props = self.props

        # Draw the primary brush, if necessary.
        if props.brush_is_visible:
            if not props.brushes.primary_brush.is_on_mesh:
                # Draw the primary brush oriented to the view.
                props.brush_graphic.draw_region_circle(
                    region_x = props.position_x,
                    region_y = props.position_y,
                    radius = props.radius,
                    outline_color = props.outline_color,
                    outline_thickness = props.outline_thickness,
                    interior_color = props.interior_color
                )

    def draw_post_view_callback(self):
        props = self.props
        brushes = props.brushes
        brush_graphic = props.brush_graphic
        brush_influence_graphic = props.brush_influence_graphic 
        primary_brush = brushes.primary_brush

        if primary_brush.is_on_mesh:
            # Draw the influenced vertices, if necessary.
            if props.brush_influence_is_visible:
                for brush in [primary_brush] + brushes.derived_brushes:
                    brush_influence_graphic.draw_brush_influence(
                        brush, props.octree.coordinate_map
                    )

            # Draw the primary brush, if necessary.
            if props.brush_is_visible:
                # Draw the primary brush oriented to the mesh.
                brush_graphic.draw_brush(
                    brush = primary_brush,
                    outline_color = props.outline_color,
                    outline_thickness = props.outline_thickness,
                    interior_color = props.interior_color
                )

    def draw_pre_view_callback(self): 
        bgl.glEnable(bgl.GL_POLYGON_OFFSET_FILL)
        bgl.glPolygonOffset(2, 0)

    def finish(self):
        active_object = bpy.context.active_object
        props = self.props

        # Remove the draw callback handle.
        bpy.types.SpaceView3D.draw_handler_remove(
            self.draw_post_pixel_handle, 'WINDOW'
        )
        bpy.types.SpaceView3D.draw_handler_remove(
            self.draw_post_view_handle, 'WINDOW'
        )
        bpy.types.SpaceView3D.draw_handler_remove(
            self.draw_pre_view_handle, 'WINDOW'
        )

        # Reset/clear persistent objects.
        props.brushes.reset()
        props.color_ramp.reset()
        props.falloff_curve.reset()
        props.octree.reset()
        props.redo_stack.clear()
        props.undo_stack.clear()

        # Reselect the active mesh object.
        active_object.select = True

        # Recombine the separate pieces of the original mesh object, if
        # necessary.
        if props.selection_is_isolated and self.selection_is_isolatable:
            # Reveal the hidden mesh object.
            self.hidden_portion.hide = False

            # Rejoin the separate mesh objects into one.
            bpy.ops.object.join()

            # Remove duplicate vertices along the selection border.
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.remove_doubles(
                threshold = 0.00001, use_unselected = True
            )

            # Restore the selection.
            active_object.vertex_groups.active_index =\
                self.selected_indices.index
            bpy.ops.object.vertex_group_select() 

            # Remove the relevant vertex groups.
            active_object.vertex_groups.remove(self.unselected_faces)
            active_object.vertex_groups.remove(self.selected_indices)

            # Restore the state of the mesh selection mode.
            mesh_select_mode = bpy.context.tool_settings.mesh_select_mode
            mesh_select_mode[0] = self.mesh_select_mode[0]
            mesh_select_mode[1] = self.mesh_select_mode[1]
            mesh_select_mode[2] = self.mesh_select_mode[2]

        # Reactive automatic shrinkwrapping, if necessary.
        surface_constraint_props = self.addon.preferences.surface_constraint
        if self.initially_auto_shrinkwrap_is_enabled:
            surface_constraint_props.auto_shrinkwrap_is_enabled = True

        # Restore the visibility state of active mesh object's modifiers.
        modifiers = active_object.modifiers
        for i in range(len(modifiers)):
            modifiers[i].show_viewport = self.modifiers_visibility_state[i]

        # Restore the display state of the active mesh object.
        active_object.show_all_edges = self.display_state[0]
        active_object.show_wire = self.display_state[1]

        # Return to Edit mode, if necessary.
        if active_object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode = 'EDIT')

        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set()

    def invoke(self, context, event):
        props = self.props
        octree = props.octree

        active_object = context.active_object
        modifiers = active_object.modifiers
        polygons = active_object.data.polygons
        vertices = active_object.data.vertices

        # Disable automatic shrinkwrapping for the duration of this operator.
        surface_constraint_props = self.addon.preferences.surface_constraint
        self.initially_auto_shrinkwrap_is_enabled =\
            surface_constraint_props.auto_shrinkwrap_is_enabled
        if self.initially_auto_shrinkwrap_is_enabled:
            surface_constraint_props.auto_shrinkwrap_is_enabled = False

        # Store the visibility state of the active mesh object's modifiers.
        self.modifiers_visibility_state =\
            [mod.show_viewport for mod in modifiers]

        # Disable the realtime display of all modifiers for the duration of the
        # tool's operation.
        for mod in modifiers:
            mod.show_viewport = False

        # Store the display state of the active mesh object.
        self.display_state = [
            active_object.show_wire, active_object.show_all_edges
        ]

        # Set the display state of the active mesh object.
        active_object.show_all_edges = True
        active_object.show_wire = True

        # Isolate the selection, if necessary.
        if props.selection_is_isolated:
            # The isolation of a mesh requires that part of it be selected and
            # part of it be unselected; a fully selected or deselected mesh is
            # invalid.

            # Begin with the assumption that the mesh object's selection cannot
            # be isolated--all or no polygons are selected.  Test this
            # assumption, and state the result.  At least one polygon must
            # be selected, and at one polygon must be unselected for the
            # assumption to be incorrect.
            active_object.update_from_editmode()
            self.selection_is_isolatable = False
            selected_polygon_exists = False
            unselected_polygon_exists = False
            for polygon in polygons:
                if selected_polygon_exists and unselected_polygon_exists:
                    self.selection_is_isolatable = True
                    break
                else:
                    polygon_is_selected = polygon.select
                    if (
                        not selected_polygon_exists and
                        polygon_is_selected
                    ):
                        selected_polygon_exists = True
                    elif (
                        not unselected_polygon_exists and
                        not polygon_is_selected
                    ):
                        unselected_polygon_exists = True

            # Isolate the selection.
            if self.selection_is_isolatable: 
                # Determine what objects are selected in the scene.
                selected = set(context.selected_objects)

                # Create a vertex group, and assign it to the selected indices.
                self.selected_indices =\
                    active_object.vertex_groups.new("Selected Indices")
                bpy.ops.object.vertex_group_assign()

                # Record the state of the mesh selection mode, and force face
                # selection mode.
                mesh_select_mode = context.tool_settings.mesh_select_mode
                self.mesh_select_mode =\
                    [component for component in mesh_select_mode]
                mesh_select_mode[2] = True
                mesh_select_mode[1] = False
                mesh_select_mode[0] = False

                # Create a vertex group, and assign it to the unselected faces.
                bpy.ops.mesh.select_all(action = 'INVERT')
                self.unselected_faces =\
                    active_object.vertex_groups.new("Unselected Faces")
                bpy.ops.object.vertex_group_assign()

                # Separate the active mesh object into two objects containing
                # the selected and unselected faces, respectively.  Hide the
                # inactive object, thus isolating the portion of interest.
                bpy.ops.mesh.separate(type = 'SELECTED')
                self.hidden_portion =\
                    set(context.selected_objects).difference(selected).pop()
                self.hidden_portion.name =\
                    "{0} (Hidden)".format(active_object.name)
                self.hidden_portion.hide = True

                # Now, the only vertices that remain in the active mesh
                # object's active vertex group are those that were along the
                # selection border.  Select these vertices, and write Edit
                # mode's data to the mesh object.
                bpy.ops.object.vertex_group_select()
                bpy.ops.object.mode_set(mode = 'OBJECT')

                # Create an octree that organizes the active mesh object's
                # vertex indices according to their world space coordinates.
                octree.insert_object(active_object, 'WORLD')

                # Remove the vertex indices that were along the selection
                # boundary.  This is only necessary if the "Lock Boundary"
                # option is not enabled.
                if not props.boundary_is_locked:
                    octree.remove_indices([
                            vertex.index
                            for vertex in vertices
                            if vertex.select
                        ]
                    )

        # Enter Object mode and create an octree that organizes the active
        # mesh object's vertex indices according to their world space
        # coordinates.  This step will be skipped if the "Isolate Selection"
        # option is enabled and the selection is isolatable, as the octree was
        # already generated.
        if (
            not props.selection_is_isolated or
            (props.selection_is_isolated and not self.selection_is_isolatable)
        ):
            octree.insert_object(active_object, 'WORLD')

        # Remove boundary indices from the octree, if necessary.
        if props.boundary_is_locked:
            vertex_properties = VertexProperties()
            vertex_properties.mesh_object = active_object
            vertex_properties.determine_indices({'BOUNDARY'})
            octree.remove_indices(vertex_properties.boundary_indices)

        # Deselect the active mesh object so that its wireframe color matches
        # Edit mode's edge color.
        active_object.select = False

        # Derive the symmetrical brushes, if necessary.
        symmetry_axes = set()
        if props.x_axis_symmetry_is_enabled:
            symmetry_axes.add('X')
        if props.y_axis_symmetry_is_enabled:
            symmetry_axes.add('Y')
        if props.z_axis_symmetry_is_enabled:
            symmetry_axes.add('Z')
        if symmetry_axes:
            brushes = props.brushes
            brushes.set_symmetry_from_object(active_object, symmetry_axes)
            if props.symmetry_type == 'MIRROR':
                brushes.derive_mirrored()
            else:
                brushes.derive_radial(props.radial_count)

        # Generate the falloff curve.
        props.falloff_curve.profile = props.falloff_profile
        props.falloff_curve.generate_curve()

        # Generate the color ramp, if necessary.
        if props.brush_influence_is_visible:
            props.color_ramp.generate_ramp()

        # Set the initial position of the brush in region space.
        props.position_x = event.mouse_region_x
        props.position_y = event.mouse_region_y

        # Designate the draw callback functions.
        args = ()
        self.draw_post_pixel_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_post_pixel_callback, args, 'WINDOW', 'POST_PIXEL'
        )
        self.draw_post_view_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_post_view_callback, args, 'WINDOW', 'POST_VIEW'
        )
        self.draw_pre_view_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_pre_view_callback, args, 'WINDOW', 'PRE_VIEW'
        )

        # Determine the events that are associated with basic navigation
        # operators.
        self.modal_helper = ModalHelper()
        keymap_names = ['3D View']
        operator_ids = {
            'view3d.move', 'view3d.rotate', 'view3d.zoom', 'view3d.view_all',
            'view3d.view_center_pick', 'view3d.view_persportho',
            'view3d.viewnumpad'
        }
        self.modal_helper.generate_event_map(keymap_names, operator_ids)

        # Display the operator's instructions in the active area's header.
        context.area.header_text_set(
            "Move: LMB    Smooth: Shift+LMB    Resize: RMB    Undo: " +
            "Ctrl+Z    Redo: Ctrl+Shift+Z    Confirm: Enter/Escape"
        )

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.region.tag_redraw()

        modal_helper = self.modal_helper
        props = self.props
        queue = modal_helper.queue

        # Execute the queued tasks.
        if queue:
            for task in queue:
                exec(task)
            queue.clear()

        if event.type == 'MOUSEMOVE':
            self.move_brush(event.mouse_region_x, event.mouse_region_y)

        elif (
            event.type == 'LEFTMOUSE' and event.value == 'PRESS' and
            (event.alt, event.ctrl, event.shift) == (False, False, False)
        ):
            bpy.ops.mesh.sct_stroke_move('INVOKE_DEFAULT')

        elif (
            event.type == 'LEFTMOUSE' and event.value == 'PRESS' and
            (event.alt, event.ctrl, event.shift) == (False, False, True)
        ):
            bpy.ops.mesh.sct_stroke_smooth('INVOKE_DEFAULT')

        elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            bpy.ops.mesh.sct_resize_mesh_brush('INVOKE_DEFAULT')

        elif (
            event.type == 'Z' and event.value == 'PRESS' and
            (event.alt, event.ctrl, event.shift) == (False, True, False)
        ):
            self.undo()

        elif (
            event.type == 'Z' and event.value == 'PRESS' and
            (event.alt, event.ctrl, event.shift) == (False, True, True)
        ):
            self.redo()

        elif event.type in {'ESC', 'RET'}:
            self.finish()
            return {'FINISHED'}

        else:
            event_key = (
                event.alt, event.ctrl, event.oskey, event.shift, event.type,
                event.value
            )

            # Permit basic navigation inputs.
            if event_key in modal_helper.event_map:
                props.brush_graphic.is_enabled = False
                props.brush_influence_graphic.is_enabled = False
                queue.append("props.brush_graphic.is_enabled = True")
                queue.append("props.brush_influence_graphic.is_enabled = True")
                return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def move_brush(self, region_x, region_y):
        context = bpy.context
        active_object = context.active_object
        props = self.props
        brushes = props.brushes 

        # Move the brush in region space.
        props.position_x = region_x
        props.position_y = region_y

        # Update the primary brush's parameters according to the region space
        # position.
        brushes.ray_cast_primary_brush_onto_mesh(
            region_x, region_y, active_object, props.backfacing_are_ignored
        )
        brushes.resize_primary_brush(props.radius)

        # Determine the brush's influence if it is on the mesh.
        if brushes.primary_brush.is_on_mesh:
            brushes.determine_influence(
                props.octree, props.falloff_curve,
                props.backfacing_are_ignored, active_object
            )
            if props.brush_influence_is_visible:
                brushes.generate_color_maps(props.color_ramp)

    def redo(self):
        props = self.props
        redo_stack = props.redo_stack
        undo_stack = props.undo_stack

        # Execute a redo operation if at least one redoable stroke exists in
        # the stack.
        if redo_stack:
            active_object = bpy.context.active_object
            octree = props.octree
            vertices = active_object.data.vertices

            # The redo stack contains stroke displacement maps.  A stroke can
            # be redone by adding the respective displacement vector from the
            # coordinates of each vertex index in the map.
            stroke_displacement_map = redo_stack.pop()
            for index in stroke_displacement_map:
                vertices[index].co += stroke_displacement_map[index] 

            # Push the redone stroke to the undo stack.
            undo_stack.append(stroke_displacement_map)

            # Update the octree.
            model_matrix = active_object.matrix_world
            world_space_submap = {
                index : model_matrix * vertices[index].co.copy()
                for index in stroke_displacement_map
            }
            octree.coordinate_map.update(world_space_submap)
            octree.insert_indices(stroke_displacement_map.keys())

            # Force the brush to update by moving it to its current position.
            self.move_brush(props.position_x, props.position_y)

    def undo(self):
        props = self.props
        redo_stack = props.redo_stack
        undo_stack = props.undo_stack

        # Execute an undo operation if at least one undoable stroke exists in
        # the stack.
        if undo_stack:
            active_object = bpy.context.active_object
            octree = props.octree
            vertices = active_object.data.vertices

            # The undo stack contains stroke displacement maps.  A stroke can
            # be undone by subtracting the respective displacement vector from
            # the coordinates of each vertex index in the map.
            stroke_displacement_map = undo_stack.pop()
            for index in stroke_displacement_map:
                vertices[index].co -= stroke_displacement_map[index]

            # Push the undone stroke to the redo stack.
            redo_stack.append(stroke_displacement_map)

            # Update the octree.
            model_matrix = active_object.matrix_world
            world_space_submap = {
                index : model_matrix * vertices[index].co.copy()
                for index in stroke_displacement_map
            }
            octree.coordinate_map.update(world_space_submap)
            octree.insert_indices(stroke_displacement_map.keys())

            # Force the brush to update by moving it to its current position.
            self.move_brush(props.position_x, props.position_y)