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
from ..auxiliary_classes.RayCaster import RayCaster

class PickSurfaceConstraint(bpy.types.Operator):
    bl_idname = "view3d.sct_pick_surface_constraint"
    bl_label = "Pick Surface Constraint"
    bl_description = "Pick the surface constraint's target."

    addon_key = __package__.split(".")[0]

    @classmethod
    def poll(cls, self):
        return bpy.context.space_data.type == 'VIEW_3D'

    def __init__(self):
        self.addon = bpy.context.user_preferences.addons[self.addon_key]
        self.props = self.addon.preferences.surface_constraint 

    def finish(self):
        # Return to Edit mode, if necessary.
        if self.initially_in_edit_mode:
            bpy.ops.object.mode_set(mode = 'EDIT')

        # Reveal the temporarily hidden objects.
        for hidden_object in self.temporarily_hidden_objects:
            hidden_object.hide = False

        # Restore the active area's header to it's initial state.
        bpy.context.area.header_text_set()

    def invoke(self, context, event): 
        # Exit Edit mode, if necessary.
        self.initially_in_edit_mode = context.mode == 'EDIT_MESH'
        if self.initially_in_edit_mode:
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Add the name of each visible mesh object in the scene to the set of
        # mesh objects to use for the raycast distance test.  Temporarily hide
        # all other visible objects.
        self.mesh_objects = list()
        mesh_objects = self.mesh_objects
        self.temporarily_hidden_objects = list()
        temporarily_hidden_objects = self.temporarily_hidden_objects
        for visible_object in context.visible_objects:
            if visible_object.type == 'MESH':
                mesh_objects.append(visible_object)
            else:
                visible_object.hide = True
                temporarily_hidden_objects.append(visible_object)

        # Display the operator's instructions in the active area's header.
        context.area.header_text_set(
            "Pick (LMB) a mesh object to use as the surface constraint's " +
            "target. Escape/RMB: Cancel"
        )

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw() 

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Assign the name of the nearest mesh object determined to be under
            # the mouse cursor to the surface constraint's target.
            self.props.target =\
                self.raycast_pick(event.mouse_region_x, event.mouse_region_y)

            self.finish()
            return {'FINISHED'}

        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            self.finish()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def raycast_pick(self, region_x, region_y):
        ray_caster = RayCaster()
        ray_caster.coordinate_system = 'WORLD'
        ray_caster.set_ray_from_region(region_x, region_y)
        ray_origin = ray_caster.ray_origin

        # Determine the nearest mesh object under the mouse cursor.
        nearest_intersection = list() 
        for mesh_object in self.mesh_objects:
            ray_caster.mesh_object = mesh_object
            location, normal, face_index = ray_caster.ray_cast()

            # Determine the square of the distance in world space from the
            # mouse cursor to the point of intersection.
            if face_index != -1:
                distance_squared = (location - ray_origin).length_squared 

                # Compare this distance with that of any previously determined
                # intersection, retaining only the lesser value.
                if nearest_intersection:
                   if distance_squared < nearest_intersection[1]:
                        nearest_intersection =\
                            [mesh_object.name, distance_squared]
                else:
                    nearest_intersection = [mesh_object.name, distance_squared]

        # Record the name of the first mesh object that the ray intersects.
        if nearest_intersection:
            return nearest_intersection[0]
        else:
            return str()
