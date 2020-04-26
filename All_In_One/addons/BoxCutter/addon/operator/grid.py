import bpy
import gpu

from mathutils import Vector, Matrix
from math import radians

from bgl import *
from gpu_extras.batch import batch_for_shader

from bpy.types import GizmoGroup, Operator, Gizmo
from bpy.props import *

from bpy_extras.view3d_utils import region_2d_to_location_3d, location_3d_to_region_2d

from .. utility import addon, active_tool


class BC_OT_AddGridGizmo(Operator):
    bl_idname = 'bc.addgridgizmo'
    bl_label = 'Show Grid Gizmo'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Show Grid Gizmo'

    def execute(self, context):
        bpy.context.window_manager.gizmo_group_type_ensure(BC_WGT_GridGizmo.bl_idname)
        # addon.preference().cursor = True
        return {'FINISHED'}


class BC_OT_RemoveGridGizmo(Operator):
    bl_idname = 'bc.removegridgizmo'
    bl_label = 'Hide Grid Gizmo'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Hide Grid Gizmo'

    def execute(self, context):
        bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_GridGizmo.bl_idname)
        # addon.preference().cursor = False
        return {'FINISHED'}


class BC_WGT_GridGizmo(GizmoGroup):
    bl_idname = 'bc.gridgizmo'
    bl_label = 'Grid Gizmo'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'DEPTH_3D', 'SCALE'}

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'BoxCutter'

    def setup(self, context):

        grid = self.gizmos.new(BC_GT_GridLayout.bl_idname)
        rpx = grid.target_set_operator('transform.translate')
        rpx.cursor_transform = True
        rpx.constraint_axis = (True, False, False)
        rpx.release_confirm = True
        grid.hide_select = True
        grid.color = 0.37, 0.37, 0.37
        grid.alpha = 0.4
        grid.line_width = 0.1

        self.grid = grid

    def draw_prepare(self, context):
        preference = addon.preference()
        bc = context.window_manager.bc

        abc = active_tool()
        if abc.idname != 'BoxCutter':
            bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_GridGizmo.bl_idname)

        grid = self.grid

        if bc.running:
            grid.hide = True
        elif preference.surface == 'CURSOR':
            grid.hide = False
        else:
            grid.hide = True

        orig_loc = context.scene.cursor.location
        orig_rot = context.scene.cursor.rotation_euler

        if preference.cursor_axis == 'X':
            rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'Y')
        elif preference.cursor_axis == 'Y':
            rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'X')
        elif preference.cursor_axis == 'Z':
            rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Z')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_scale_mat = Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1))
        x_dial_matrix_world = orig_loc_mat @ rot_mat @ orig_scale_mat

        grid.matrix_basis = x_dial_matrix_world.normalized()


class BC_GT_GridLayout(Gizmo):
    bl_idname = 'bc.gridlayout'
    bl_target_properties = (
        {'id': 'offset', 'type': 'FLOAT', 'array_length': 1},
    )

    __slots__ = (
        'custom_shape'
    )

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.new_custom_shape('LINES', lines), select_id=select_id)

    def setup(self):
        if not hasattr(self, 'custom_shape'):
            self.custom_shape = self.new_custom_shape('LINES', lines)

    def exit(self, context, cancel):
        context.area.header_text_set(None)


lines = (
    (-10, -10, 0.0), (10, -10, 0.0),
    (-10, -9, 0.0), (10, -9, 0.0),
    (-10, -8, 0.0), (10, -8, 0.0),
    (-10, -7, 0.0), (10, -7, 0.0),
    (-10, -6, 0.0), (10, -6, 0.0),
    (-10, -5, 0.0), (10, -5, 0.0),
    (-10, -4, 0.0), (10, -4, 0.0),
    (-10, -3, 0.0), (10, -3, 0.0),
    (-10, -2, 0.0), (10, -2, 0.0),
    (-10, -1, 0.0), (10, -1, 0.0),
    (-10, 0, 0.0), (10, 0, 0.0),
    (-10, 1, 0.0), (10, 1, 0.0),
    (-10, 2, 0.0), (10, 2, 0.0),
    (-10, 3, 0.0), (10, 3, 0.0),
    (-10, 4, 0.0), (10, 4, 0.0),
    (-10, 5, 0.0), (10, 5, 0.0),
    (-10, 6, 0.0), (10, 6, 0.0),
    (-10, 7, 0.0), (10, 7, 0.0),
    (-10, 8, 0.0), (10, 8, 0.0),
    (-10, 9, 0.0), (10, 9, 0.0),
    (-10, 10, 0.0), (10, 10, 0.0),
    (-10, -10, 0.0), (-10, 10, 0.0),
    (-9, -10, 0.0), (-9, 10, 0.0),
    (-8, -10, 0.0), (-8, 10, 0.0),
    (-7, -10, 0.0), (-7, 10, 0.0),
    (-6, -10, 0.0), (-6, 10, 0.0),
    (-5, -10, 0.0), (-5, 10, 0.0),
    (-4, -10, 0.0), (-4, 10, 0.0),
    (-3, -10, 0.0), (-3, 10, 0.0),
    (-2, -10, 0.0), (-2, 10, 0.0),
    (-1, -10, 0.0), (-1, 10, 0.0),
    (0, -10, 0.0), (0, 10, 0.0),
    (1, -10, 0.0), (1, 10, 0.0),
    (2, -10, 0.0), (2, 10, 0.0),
    (3, -10, 0.0), (3, 10, 0.0),
    (4, -10, 0.0), (4, 10, 0.0),
    (5, -10, 0.0), (5, 10, 0.0),
    (6, -10, 0.0), (6, 10, 0.0),
    (7, -10, 0.0), (7, 10, 0.0),
    (8, -10, 0.0), (8, 10, 0.0),
    (9, -10, 0.0), (9, 10, 0.0),
    (10, -10, 0.0), (10, 10, 0.0)
)
