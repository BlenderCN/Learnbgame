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
from mathutils import Vector
from ..MeshBrush import MeshBrush

class ResizeMeshBrush(bpy.types.Operator):
    bl_idname = "mesh.sct_resize_mesh_brush"
    bl_label = "Resize Mesh Brush"
    bl_options = {'INTERNAL'}

    addon_key = __package__.split(".")[0]

    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]
        self.props = self.addon.preferences.mesh_brush

    def invoke(self, context, event):
        # Record the mouse cursor's initial position and the brush's initial
        # radius for future reference.
        self.center_point =\
            Vector((event.mouse_region_x, event.mouse_region_y))
        self.initial_radius = self.props.radius

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()
        props = self.props
        brushes = props.brushes

        if event.type == 'MOUSEMOVE':
            # Increment/decrement the brush's radius by the mouse cursor's
            # region space distance along the x-axis relative to the recorded
            # center point.
            mouse_position =\
                Vector((event.mouse_region_x, event.mouse_region_y))
            delta = 0.75 * (mouse_position - self.center_point).x
            radius = self.initial_radius + delta
            if radius < 1:
                props.radius = 1
            else:
                props.radius = radius

            # Resize the brushes.
            brushes.resize_primary_brush(props.radius)

            # Determine the brushes' influence if it is on the mesh.
            if brushes.primary_brush.is_on_mesh:
                brushes.determine_influence(
                    props.octree, props.falloff_curve,
                    props.backfacing_are_ignored, context.active_object
                )
                if props.brush_influence_is_visible:
                    brushes.generate_color_maps(props.color_ramp)

        elif event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            self.move_brush(event.mouse_region_x, event.mouse_region_y)

            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    # Reference the ability to move the mesh brush upon completion of the
    # resize operation.
    move_brush = MeshBrush.move_brush