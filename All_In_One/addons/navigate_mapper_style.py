bl_info = {
    "name": "Navigation for mappers",
    "author": "nemyax",
    "version": (0, 5, 20130417),
    "blender": (2, 6, 6),
    "location": "",
    "description": "Navigate as in game map editors",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import mathutils as mu
import math
from bpy.props import FloatProperty

def nudge(event, opposites):
    if event.value != 'RELEASE':
        if event.type == opposites[1]:
            return 1
        else:
            return -1
    else:
        return 0

class NavigateMapperStyle(bpy.types.Operator):
    """Navigate as in game map editors"""
    bl_idname = "view3d.navigate_mapper_style"
    bl_label = "Navigate Mapper Style"
    bl_options = {'GRAB_POINTER', 'BLOCKING'}
    rot_speed = FloatProperty(
        name="Rotation Speed",
        description="Rotation speed",
        min=0.1,
        max=100.0,
        default=1.0)
    mov_speed = FloatProperty(
        name="Movement Speed",
        description="Movement speed in Blender units per pulse",
        min=0.01,
        max=100.0,
        default=0.1)

    def modal(self, context, event):
        new_view_matrix = context.region_data.view_matrix
        left_right = ('A', 'D')
        fwd_back = ('W', 'S')
        down_up = ('Z', 'SPACE')
        if event.type == 'MOUSEMOVE':
            new_x = event.mouse_x
            new_y = event.mouse_y
            x_delta = (new_x - self.initial_x) * -self.rot_speed_factor
            y_delta = (new_y - self.initial_y) * -self.rot_speed_factor
            elevation_delta = math.atan2(y_delta, 1.0)
            azimuth_delta = math.atan2(x_delta, 1.0)
            old_view_matrix = context.region_data.view_matrix
            r_x = mu.Matrix.Rotation(elevation_delta, 4, 'X')
            r_z = mu.Matrix.Rotation(azimuth_delta, 4, 'Z').inverted()
            r_orig = old_view_matrix.to_3x3().to_4x4()
            new_view_matrix = \
                r_x * \
                r_orig * \
                r_z * \
                r_orig.inverted() * \
                old_view_matrix
            self.initial_x = new_x
            self.initial_y = new_y
        elif event.type in fwd_back:
            self.mov.z = nudge(event, fwd_back)
        elif event.type in left_right:
            self.mov.x = nudge(event, left_right)
        elif event.type in down_up:
            self.mov.y = nudge(event, down_up)
        elif event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return {'FINISHED'}
        elif event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            return {'FINISHED'}
        context.region_data.view_matrix = \
            mu.Matrix.Translation(self.mov * self.mov_speed).inverted() * \
            new_view_matrix
        context.region_data.update()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.initial_x = event.mouse_x
            self.initial_y = event.mouse_y
            self.rot_speed_factor = self.rot_speed * 0.01
            self.mov = mu.Vector((0, 0, 0))
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(NavigateMapperStyle)

def unregister():
    bpy.utils.unregister_class(NavigateMapperStyle)

if __name__ == "__main__":
    register()

