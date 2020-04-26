import bpy
import gpu

from mathutils import Vector, Matrix
from math import radians

from bgl import *
from gpu_extras.batch import batch_for_shader

from bpy.types import GizmoGroup, Operator, Gizmo
from bpy.props import EnumProperty, BoolProperty

from bpy_extras.view3d_utils import region_2d_to_location_3d, location_3d_to_region_2d

from .. utility import addon, active_tool


class BC_OT_CursorTranslate(Operator):
    bl_idname = 'bc.cursor_translate'
    bl_label = 'Gizmo Translate '
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Move

LMB                    - translate
LMB+shift          - Snap 3DCursor to surface
LMB+shift+ctrl - reset axis
"""
    axis: EnumProperty(
        name='Axis',
        description='Axis',
        items=[
            ('X', 'x', '', '', 0),
            ('Y', 'y', '', '', 1),
            ('Z', 'z', '', '', 2),
            ('ALL', 'All', '', '', 3)],
        default='ALL')

    snap: BoolProperty(
        name='snap to surface',
        description='Reset Axis',
        default=False)

    axis_set = (False, False, False)

    def invoke(self, context, event):
        if self.axis == 'X':
            self.axis_set = (True, False, False)
        elif self.axis == 'Y':
            self.axis_set = (False, True, False)
        elif self.axis == 'Z':
            self.axis_set = (False, False, True)
        else:
            self.axis_set = (False, False, False)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.shift:
            if self.snap:
                bpy.ops.view3d.cursor3d('INVOKE_DEFAULT', orientation='GEOM', use_depth=True)
                return {'FINISHED'}
            else:
                if self.axis == 'X':
                    if event.ctrl:
                        bpy.context.scene.cursor.location[0] = 0
                        return {'FINISHED'}
                    else:
                        bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, True, True), orient_type='LOCAL', release_confirm=True, cursor_transform=True)
                        return {'FINISHED'}
                if self.axis == 'Y':
                    if event.ctrl:
                        bpy.context.scene.cursor.location[1] = 0
                        return {'FINISHED'}
                    else:
                        bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, False, True), orient_type='LOCAL', release_confirm=True, cursor_transform=True)
                        return {'FINISHED'}
                if self.axis == 'Z':
                    if event.ctrl:
                        bpy.context.scene.cursor.location[2] = 0
                        return {'FINISHED'}
                    else:
                        bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, True, False), orient_type='LOCAL', release_confirm=True, cursor_transform=True)
                        return {'FINISHED'}
        else:
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=self.axis_set, orient_type='LOCAL', release_confirm=True, cursor_transform=True)

        return {'FINISHED'}


class BC_OT_CursorRotate(Operator):
    bl_idname = 'bc.cursor_rotate'
    bl_label = 'Gizmo Rotate'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Rotate

LMB                    - rotate
LMB+shift+ctrl - reset axis
"""

    axis: EnumProperty(
        name='Axis',
        description='Axis',
        items=[
            ('X', 'x', '', '', 0),
            ('Y', 'y', '', '', 1),
            ('Z', 'z', '', '', 2),
            ('ALL', 'All', '', '', 3)],
        default='ALL')

    reset: BoolProperty(
        name='Reset axis',
        description='Reset Axis',
        default=False)

    axis_set = (False, False, False)

    def invoke(self, context, event):
        if self.axis == 'X':
            self.axis_set = (True, False, False)
        elif self.axis == 'Y':
            self.axis_set = (False, True, False)
        elif self.axis == 'Z':
            self.axis_set = (False, False, True)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.shift and event.ctrl:
            if self.axis == 'X':
                bpy.context.scene.cursor.rotation_euler[0] = 0
                return {'FINISHED'}
            if self.axis == 'Y':
                bpy.context.scene.cursor.rotation_euler[1] = 0
                return {'FINISHED'}
            if self.axis == 'Z':
                bpy.context.scene.cursor.rotation_euler[2] = 0
                return {'FINISHED'}

        else:
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=self.axis_set, orient_type='LOCAL', release_confirm=True, cursor_transform=True)
        return {'FINISHED'}


class BC_OT_AddCursorGizmo(Operator):
    bl_idname = 'bc.add_cursor'
    bl_label = 'Gizmo cursor'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Show Cursor Gizmo'

    def execute(self, context):
        bpy.context.window_manager.gizmo_group_type_ensure(BC_WGT_GizmoGroup.bl_idname)
        bpy.context.window_manager.gizmo_group_type_ensure('bc.gridgizmo')
        addon.preference().cursor = True
        return {'FINISHED'}


class BC_OT_RemoveCursorGizmo(Operator):
    bl_idname = 'bc.remove_cursor'
    bl_label = 'Gizmo cursor'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Hide Cursor Gizmo'

    def execute(self, context):
        bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_GizmoGroup.bl_idname)
        bpy.context.window_manager.gizmo_group_type_unlink_delayed('bc.gridgizmo')
        addon.preference().cursor = False
        return {'FINISHED'}


class BC_WGT_GizmoGroup(GizmoGroup):
    bl_idname = 'bc.gizmogroup'
    bl_label = 'Gizmo Group'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'BoxCutter'


    def setup(self, context):

        mpr_x = self.gizmos.new('GIZMO_GT_arrow_3d')
        opx = mpr_x.target_set_operator('bc.cursor_translate')
        opx.axis = 'X'
        opx.snap = False
        mpr_x.use_draw_modal = False
        mpr_x.scale_basis = 1
        mpr_x.color = 1, 0.2, 0.322
        mpr_x.alpha = 0.5
        mpr_x.color_highlight = 1.0, 1.0, 1.0
        mpr_x.alpha_highlight = 1.0

        dial_x = self.gizmos.new(BC_GT_CustomFace.bl_idname)
        rpx = dial_x.target_set_operator('bc.cursor_rotate')
        rpx.axis = 'X'
        dial_x.use_draw_modal = False
        dial_x.scale_basis = 0.6
        dial_x.color = 1, 0.2, 0.322
        dial_x.alpha = 0.5
        dial_x.color_highlight = 1.0, 1.0, 1.0
        dial_x.alpha_highlight = 1.0

        mpr_y = self.gizmos.new('GIZMO_GT_arrow_3d')
        opy = mpr_y.target_set_operator('bc.cursor_translate')
        opy.axis = 'Y'
        opy.snap = False
        mpr_y.use_draw_modal = False
        mpr_y.scale_basis = 1
        mpr_y.color = 0.545, 0.863, 0
        mpr_y.alpha = 0.5
        mpr_y.color_highlight = 1.0, 1.0, 1.0
        mpr_y.alpha_highlight = 1.0

        dial_y = self.gizmos.new(BC_GT_CustomFace.bl_idname)
        rpy = dial_y.target_set_operator('bc.cursor_rotate')
        rpy.axis = 'Y'
        dial_y.use_draw_modal = False
        dial_y.scale_basis = 0.6
        dial_y.color = 0.545, 0.863, 0
        dial_y.alpha = 0.5
        dial_y.color_highlight = 1.0, 1.0, 1.0
        dial_y.alpha_highlight = 1.0

        mpr_z = self.gizmos.new('GIZMO_GT_arrow_3d')
        opz = mpr_z.target_set_operator('bc.cursor_translate')
        opz.axis = 'Z'
        opz.snap = False
        mpr_z.use_draw_modal = False
        mpr_z.scale_basis = 1
        mpr_z.color = 0.157, 0.565, 1
        mpr_z.alpha = 0.5
        mpr_z.color_highlight = 1.0, 1.0, 1.0
        mpr_z.alpha_highlight = 1.0

        dial_z = self.gizmos.new(BC_GT_CustomFace.bl_idname)
        rpz = dial_z.target_set_operator('bc.cursor_rotate')
        rpz.axis = 'Z'
        dial_z.use_draw_modal = False
        dial_z.scale_basis = 0.6
        dial_z.color = 0.157, 0.565, 1
        dial_z.alpha = 0.5
        dial_z.color_highlight = 1.0, 1.0, 1.0
        dial_z.alpha_highlight = 1.0

        mid = self.gizmos.new(BC_GT_CustomCursorCube.bl_idname)
        mpz = mid.target_set_operator('bc.cursor_translate')
        mpz.axis = 'ALL'
        mpz.snap = True
        mid.scale_basis = 0.15
        mid.color = 0.5, 0.5, 0.5
        mid.alpha = 0.5
        mid.color_highlight = 1.0, 1.0, 1.0
        mid.alpha_highlight = 1.0

        self.mpr_z = mpr_z
        self.dial_z = dial_z
        self.mpr_x = mpr_x
        self.dial_x = dial_x
        self.mpr_y = mpr_y
        self.dial_y = dial_y
        self.mid = mid


    def draw_prepare(self, context):

        preference = addon.preference()

        abc = active_tool()
        if abc.idname != 'BoxCutter':
            bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_GizmoGroup.bl_idname)

        mpr_z = self.mpr_z
        dial_z = self.dial_z
        mpr_x = self.mpr_x
        dial_x = self.dial_x
        mpr_y = self.mpr_y
        dial_y = self.dial_y
        mid = self.mid

        if bpy.context.window_manager.bc.running:
            mpr_z.hide = True
            dial_z.hide = True
            mpr_x.hide = True
            dial_x.hide = True
            mpr_y.hide = True
            dial_y.hide = True
            mid.hide = True
        else:
            if preference.surface == 'CURSOR':
                mpr_z.hide = False
                dial_z.hide = False
                mpr_x.hide = False
                dial_x.hide = False
                mpr_y.hide = False
                dial_y.hide = False
                mid.hide = False
            else:
                mpr_z.hide = True
                dial_z.hide = True
                mpr_x.hide = True
                dial_x.hide = True
                mpr_y.hide = True
                dial_y.hide = True
                mid.hide = True

        orig_loc = context.scene.cursor.location
        orig_rot = context.scene.cursor.rotation_euler

        x_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Y')
        x_dial_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'Y')
        y_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'X')
        z_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Z')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_scale_mat = Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1))

        z_matrix_world = orig_loc_mat @ z_rot_mat @ orig_scale_mat
        x_matrix_world = orig_loc_mat @ x_rot_mat @ orig_scale_mat
        x_dial_matrix_world = orig_loc_mat @ x_dial_rot_mat @ orig_scale_mat
        y_matrix_world = orig_loc_mat @ y_rot_mat @ orig_scale_mat
        mid_matrix_world = orig_loc_mat @ orig_rot.to_matrix().to_4x4() @ orig_scale_mat

        mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_y.matrix_basis = y_matrix_world.normalized()

        dial_x.matrix_basis = x_dial_matrix_world.normalized()
        dial_y.matrix_basis = y_matrix_world.normalized()
        dial_z.matrix_basis = z_matrix_world.normalized()

        mid.matrix_basis = mid_matrix_world.normalized()


class BC_GT_CustomCursorCube(Gizmo):
    bl_idname = 'bc.cursoricogizmo'
    bl_target_properties = (
        {'id': 'offset', 'type': 'FLOAT', 'array_length': 1},
    )

    __slots__ = (
        'custom_shape'
    )

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.new_custom_shape('TRIS', icosphere), select_id=select_id)

    def setup(self):
        if not hasattr(self, 'custom_shape'):
            self.custom_shape = self.new_custom_shape('TRIS', icosphere)

    def exit(self, context, cancel):
        context.area.header_text_set(None)


class BC_GT_CustomFace(Gizmo):
    bl_idname = 'bc.cursorfacegizmo'
    bl_target_properties = (
        {'id': 'offset', 'type': 'FLOAT', 'array_length': 1},
    )

    __slots__ = (
        'custom_shape'
    )

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.new_custom_shape('LINE_STRIP', lines), select_id=select_id)

    def setup(self):
        if not hasattr(self, 'custom_shape'):
            self.custom_shape = self.new_custom_shape('LINE_STRIP', lines)

    def exit(self, context, cancel):
        context.area.header_text_set(None)


lines = (
    (-0.876561, 0.478638, 0.0),
    (-0.908473, 0.414886, 0.0),
    (-0.935756, 0.349019, 0.0),
    (-0.958271, 0.281374, 0.0),
    (-0.975902, 0.212294, 0.0),
    (-0.98856, 0.142134, 0.0),
    (-0.996181, 0.071248, 0.0),
    (-1.0, 0, 0.0),
    (-0.996181, -0.071248, 0.0),
    (-0.98856, -0.142134, 0.0),
    (-0.975902, -0.212294, 0.0),
    (-0.958271, -0.281374, 0.0),
    (-0.935756, -0.349019, 0.0),
    (-0.908473, -0.414886, 0.0),
    (-0.876561, -0.478638, 0.0),
)


icosphere = (
    (0.0, 0.0, -1.0),
    (0.42532268166542053, -0.30901139974594116, -0.8506541848182678),
    (-0.16245555877685547, -0.49999526143074036, -0.8506544232368469),
    (0.7236073017120361, -0.5257253050804138, -0.44721952080726624),
    (0.42532268166542053, -0.30901139974594116, -0.8506541848182678),
    (0.8506478667259216, 0.0, -0.5257359147071838),
    (0.0, 0.0, -1.0),
    (-0.16245555877685547, -0.49999526143074036, -0.8506544232368469),
    (-0.525729775428772, 0.0, -0.8506516814231873),
    (0.0, 0.0, -1.0),
    (-0.525729775428772, 0.0, -0.8506516814231873),
    (-0.16245555877685547, 0.49999526143074036, -0.8506544232368469),
    (0.0, 0.0, -1.0),
    (-0.16245555877685547, 0.49999526143074036, -0.8506544232368469),
    (0.42532268166542053, 0.30901139974594116, -0.8506541848182678),
    (0.7236073017120361, -0.5257253050804138, -0.44721952080726624),
    (0.8506478667259216, 0.0, -0.5257359147071838),
    (0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.276388019323349, -0.8506492376327515, -0.4472198486328125),
    (0.26286882162094116, -0.8090116381645203, -0.5257376432418823),
    (0.0, -0.9999999403953552, 0.0),
    (-0.8944262266159058, 0.0, -0.44721561670303345),
    (-0.6881893873214722, -0.49999693036079407, -0.5257362127304077),
    (-0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.276388019323349, 0.8506492376327515, -0.4472198486328125),
    (-0.6881893873214722, 0.49999693036079407, -0.5257362127304077),
    (-0.5877856016159058, 0.8090167045593262, 0.0),
    (0.7236073017120361, 0.5257253050804138, -0.44721952080726624),
    (0.26286882162094116, 0.8090116381645203, -0.5257376432418823),
    (0.5877856016159058, 0.8090167045593262, 0.0),
    (0.7236073017120361, -0.5257253050804138, -0.44721952080726624),
    (0.9510578513145447, -0.30901262164115906, 0.0),
    (0.5877856016159058, -0.8090167045593262, 0.0),
    (-0.276388019323349, -0.8506492376327515, -0.4472198486328125),
    (0.0, -0.9999999403953552, 0.0),
    (-0.5877856016159058, -0.8090167045593262, 0.0),
    (-0.8944262266159058, 0.0, -0.44721561670303345),
    (-0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.9510578513145447, 0.30901262164115906, 0.0),
    (-0.276388019323349, 0.8506492376327515, -0.4472198486328125),
    (-0.5877856016159058, 0.8090167045593262, 0.0),
    (0.0, 0.9999999403953552, 0.0),
    (0.7236073017120361, 0.5257253050804138, -0.44721952080726624),
    (0.5877856016159058, 0.8090167045593262, 0.0),
    (0.9510578513145447, 0.30901262164115906, 0.0),
    (0.276388019323349, -0.8506492376327515, 0.4472198486328125),
    (0.6881893873214722, -0.49999693036079407, 0.5257362127304077),
    (0.16245555877685547, -0.49999526143074036, 0.8506543636322021),
    (-0.7236073017120361, -0.5257253050804138, 0.44721952080726624),
    (-0.26286882162094116, -0.8090116381645203, 0.5257376432418823),
    (-0.42532268166542053, -0.30901139974594116, 0.8506541848182678),
    (-0.7236073017120361, 0.5257253050804138, 0.44721952080726624),
    (-0.8506478667259216, 0.0, 0.5257359147071838),
    (-0.42532268166542053, 0.30901139974594116, 0.8506541848182678),
    (0.276388019323349, 0.8506492376327515, 0.4472198486328125),
    (-0.26286882162094116, 0.8090116381645203, 0.5257376432418823),
    (0.16245555877685547, 0.49999526143074036, 0.8506543636322021),
    (0.8944262266159058, 0.0, 0.44721561670303345),
    (0.6881893873214722, 0.49999693036079407, 0.5257362127304077),
    (0.525729775428772, 0.0, 0.8506516814231873),
    (0.525729775428772, 0.0, 0.8506516814231873),
    (0.16245555877685547, 0.49999526143074036, 0.8506543636322021),
    (0.0, 0.0, 1.0),
    (0.525729775428772, 0.0, 0.8506516814231873),
    (0.6881893873214722, 0.49999693036079407, 0.5257362127304077),
    (0.16245555877685547, 0.49999526143074036, 0.8506543636322021),
    (0.6881893873214722, 0.49999693036079407, 0.5257362127304077),
    (0.276388019323349, 0.8506492376327515, 0.4472198486328125),
    (0.16245555877685547, 0.49999526143074036, 0.8506543636322021),
    (0.16245555877685547, 0.49999526143074036, 0.8506543636322021),
    (-0.42532268166542053, 0.30901139974594116, 0.8506541848182678),
    (0.0, 0.0, 1.0),
    (0.16245555877685547, 0.49999526143074036, 0.8506543636322021),
    (-0.26286882162094116, 0.8090116381645203, 0.5257376432418823),
    (-0.42532268166542053, 0.30901139974594116, 0.8506541848182678),
    (-0.26286882162094116, 0.8090116381645203, 0.5257376432418823),
    (-0.7236073017120361, 0.5257253050804138, 0.44721952080726624),
    (-0.42532268166542053, 0.30901139974594116, 0.8506541848182678),
    (-0.42532268166542053, 0.30901139974594116, 0.8506541848182678),
    (-0.42532268166542053, -0.30901139974594116, 0.8506541848182678),
    (0.0, 0.0, 1.0),
    (-0.42532268166542053, 0.30901139974594116, 0.8506541848182678),
    (-0.8506478667259216, 0.0, 0.5257359147071838),
    (-0.42532268166542053, -0.30901139974594116, 0.8506541848182678),
    (-0.8506478667259216, 0.0, 0.5257359147071838),
    (-0.7236073017120361, -0.5257253050804138, 0.44721952080726624),
    (-0.42532268166542053, -0.30901139974594116, 0.8506541848182678),
    (-0.42532268166542053, -0.30901139974594116, 0.8506541848182678),
    (0.16245555877685547, -0.49999526143074036, 0.8506543636322021),
    (0.0, 0.0, 1.0),
    (-0.42532268166542053, -0.30901139974594116, 0.8506541848182678),
    (-0.26286882162094116, -0.8090116381645203, 0.5257376432418823),
    (0.16245555877685547, -0.49999526143074036, 0.8506543636322021),
    (-0.26286882162094116, -0.8090116381645203, 0.5257376432418823),
    (0.276388019323349, -0.8506492376327515, 0.4472198486328125),
    (0.16245555877685547, -0.49999526143074036, 0.8506543636322021),
    (0.16245555877685547, -0.49999526143074036, 0.8506543636322021),
    (0.525729775428772, 0.0, 0.8506516814231873),
    (0.0, 0.0, 1.0),
    (0.16245555877685547, -0.49999526143074036, 0.8506543636322021),
    (0.6881893873214722, -0.49999693036079407, 0.5257362127304077),
    (0.525729775428772, 0.0, 0.8506516814231873),
    (0.6881893873214722, -0.49999693036079407, 0.5257362127304077),
    (0.8944262266159058, 0.0, 0.44721561670303345),
    (0.525729775428772, 0.0, 0.8506516814231873),
    (0.9510578513145447, 0.30901262164115906, 0.0),
    (0.6881893873214722, 0.49999693036079407, 0.5257362127304077),
    (0.8944262266159058, 0.0, 0.44721561670303345),
    (0.9510578513145447, 0.30901262164115906, 0.0),
    (0.5877856016159058, 0.8090167045593262, 0.0),
    (0.6881893873214722, 0.49999693036079407, 0.5257362127304077),
    (0.5877856016159058, 0.8090167045593262, 0.0),
    (0.276388019323349, 0.8506492376327515, 0.4472198486328125),
    (0.6881893873214722, 0.49999693036079407, 0.5257362127304077),
    (0.0, 0.9999999403953552, 0.0),
    (-0.26286882162094116, 0.8090116381645203, 0.5257376432418823),
    (0.276388019323349, 0.8506492376327515, 0.4472198486328125),
    (0.0, 0.9999999403953552, 0.0),
    (-0.5877856016159058, 0.8090167045593262, 0.0),
    (-0.26286882162094116, 0.8090116381645203, 0.5257376432418823),
    (-0.5877856016159058, 0.8090167045593262, 0.0),
    (-0.7236073017120361, 0.5257253050804138, 0.44721952080726624),
    (-0.26286882162094116, 0.8090116381645203, 0.5257376432418823),
    (-0.9510578513145447, 0.30901262164115906, 0.0),
    (-0.8506478667259216, 0.0, 0.5257359147071838),
    (-0.7236073017120361, 0.5257253050804138, 0.44721952080726624),
    (-0.9510578513145447, 0.30901262164115906, 0.0),
    (-0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.8506478667259216, 0.0, 0.5257359147071838),
    (-0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.7236073017120361, -0.5257253050804138, 0.44721952080726624),
    (-0.8506478667259216, 0.0, 0.5257359147071838),
    (-0.5877856016159058, -0.8090167045593262, 0.0),
    (-0.26286882162094116, -0.8090116381645203, 0.5257376432418823),
    (-0.7236073017120361, -0.5257253050804138, 0.44721952080726624),
    (-0.5877856016159058, -0.8090167045593262, 0.0),
    (0.0, -0.9999999403953552, 0.0),
    (-0.26286882162094116, -0.8090116381645203, 0.5257376432418823),
    (0.0, -0.9999999403953552, 0.0),
    (0.276388019323349, -0.8506492376327515, 0.4472198486328125),
    (-0.26286882162094116, -0.8090116381645203, 0.5257376432418823),
    (0.5877856016159058, -0.8090167045593262, 0.0),
    (0.6881893873214722, -0.49999693036079407, 0.5257362127304077),
    (0.276388019323349, -0.8506492376327515, 0.4472198486328125),
    (0.5877856016159058, -0.8090167045593262, 0.0),
    (0.9510578513145447, -0.30901262164115906, 0.0),
    (0.6881893873214722, -0.49999693036079407, 0.5257362127304077),
    (0.9510578513145447, -0.30901262164115906, 0.0),
    (0.8944262266159058, 0.0, 0.44721561670303345),
    (0.6881893873214722, -0.49999693036079407, 0.5257362127304077),
    (0.5877856016159058, 0.8090167045593262, 0.0),
    (0.0, 0.9999999403953552, 0.0),
    (0.276388019323349, 0.8506492376327515, 0.4472198486328125),
    (0.5877856016159058, 0.8090167045593262, 0.0),
    (0.26286882162094116, 0.8090116381645203, -0.5257376432418823),
    (0.0, 0.9999999403953552, 0.0),
    (0.26286882162094116, 0.8090116381645203, -0.5257376432418823),
    (-0.276388019323349, 0.8506492376327515, -0.4472198486328125),
    (0.0, 0.9999999403953552, 0.0),
    (-0.5877856016159058, 0.8090167045593262, 0.0),
    (-0.9510578513145447, 0.30901262164115906, 0.0),
    (-0.7236073017120361, 0.5257253050804138, 0.44721952080726624),
    (-0.5877856016159058, 0.8090167045593262, 0.0),
    (-0.6881893873214722, 0.49999693036079407, -0.5257362127304077),
    (-0.9510578513145447, 0.30901262164115906, 0.0),
    (-0.6881893873214722, 0.49999693036079407, -0.5257362127304077),
    (-0.8944262266159058, 0.0, -0.44721561670303345),
    (-0.9510578513145447, 0.30901262164115906, 0.0),
    (-0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.5877856016159058, -0.8090167045593262, 0.0),
    (-0.7236073017120361, -0.5257253050804138, 0.44721952080726624),
    (-0.9510578513145447, -0.30901262164115906, 0.0),
    (-0.6881893873214722, -0.49999693036079407, -0.5257362127304077),
    (-0.5877856016159058, -0.8090167045593262, 0.0),
    (-0.6881893873214722, -0.49999693036079407, -0.5257362127304077),
    (-0.276388019323349, -0.8506492376327515, -0.4472198486328125),
    (-0.5877856016159058, -0.8090167045593262, 0.0),
    (0.0, -0.9999999403953552, 0.0),
    (0.5877856016159058, -0.8090167045593262, 0.0),
    (0.276388019323349, -0.8506492376327515, 0.4472198486328125),
    (0.0, -0.9999999403953552, 0.0),
    (0.26286882162094116, -0.8090116381645203, -0.5257376432418823),
    (0.5877856016159058, -0.8090167045593262, 0.0),
    (0.26286882162094116, -0.8090116381645203, -0.5257376432418823),
    (0.7236073017120361, -0.5257253050804138, -0.44721952080726624),
    (0.5877856016159058, -0.8090167045593262, 0.0),
    (0.9510578513145447, -0.30901262164115906, 0.0),
    (0.9510578513145447, 0.30901262164115906, 0.0),
    (0.8944262266159058, 0.0, 0.44721561670303345),
    (0.9510578513145447, -0.30901262164115906, 0.0),
    (0.8506478667259216, 0.0, -0.5257359147071838),
    (0.9510578513145447, 0.30901262164115906, 0.0),
    (0.8506478667259216, 0.0, -0.5257359147071838),
    (0.7236073017120361, 0.5257253050804138, -0.44721952080726624),
    (0.9510578513145447, 0.30901262164115906, 0.0),
    (0.42532268166542053, 0.30901139974594116, -0.8506541848182678),
    (0.26286882162094116, 0.8090116381645203, -0.5257376432418823),
    (0.7236073017120361, 0.5257253050804138, -0.44721952080726624),
    (0.42532268166542053, 0.30901139974594116, -0.8506541848182678),
    (-0.16245555877685547, 0.49999526143074036, -0.8506544232368469),
    (0.26286882162094116, 0.8090116381645203, -0.5257376432418823),
    (-0.16245555877685547, 0.49999526143074036, -0.8506544232368469),
    (-0.276388019323349, 0.8506492376327515, -0.4472198486328125),
    (0.26286882162094116, 0.8090116381645203, -0.5257376432418823),
    (-0.16245555877685547, 0.49999526143074036, -0.8506544232368469),
    (-0.6881893873214722, 0.49999693036079407, -0.5257362127304077),
    (-0.276388019323349, 0.8506492376327515, -0.4472198486328125),
    (-0.16245555877685547, 0.49999526143074036, -0.8506544232368469),
    (-0.525729775428772, 0.0, -0.8506516814231873),
    (-0.6881893873214722, 0.49999693036079407, -0.5257362127304077),
    (-0.525729775428772, 0.0, -0.8506516814231873),
    (-0.8944262266159058, 0.0, -0.44721561670303345),
    (-0.6881893873214722, 0.49999693036079407, -0.5257362127304077),
    (-0.525729775428772, 0.0, -0.8506516814231873),
    (-0.6881893873214722, -0.49999693036079407, -0.5257362127304077),
    (-0.8944262266159058, 0.0, -0.44721561670303345),
    (-0.525729775428772, 0.0, -0.8506516814231873),
    (-0.16245555877685547, -0.49999526143074036, -0.8506544232368469),
    (-0.6881893873214722, -0.49999693036079407, -0.5257362127304077),
    (-0.16245555877685547, -0.49999526143074036, -0.8506544232368469),
    (-0.276388019323349, -0.8506492376327515, -0.4472198486328125),
    (-0.6881893873214722, -0.49999693036079407, -0.5257362127304077),
    (0.8506478667259216, 0.0, -0.5257359147071838),
    (0.42532268166542053, 0.30901139974594116, -0.8506541848182678),
    (0.7236073017120361, 0.5257253050804138, -0.44721952080726624),
    (0.8506478667259216, 0.0, -0.5257359147071838),
    (0.42532268166542053, -0.30901139974594116, -0.8506541848182678),
    (0.42532268166542053, 0.30901139974594116, -0.8506541848182678),
    (0.42532268166542053, -0.30901139974594116, -0.8506541848182678),
    (0.0, 0.0, -1.0),
    (0.42532268166542053, 0.30901139974594116, -0.8506541848182678),
    (-0.16245555877685547, -0.49999526143074036, -0.8506544232368469),
    (0.26286882162094116, -0.8090116381645203, -0.5257376432418823),
    (-0.276388019323349, -0.8506492376327515, -0.4472198486328125),
    (-0.16245555877685547, -0.49999526143074036, -0.8506544232368469),
    (0.42532268166542053, -0.30901139974594116, -0.8506541848182678),
    (0.26286882162094116, -0.8090116381645203, -0.5257376432418823),
    (0.42532268166542053, -0.30901139974594116, -0.8506541848182678),
    (0.7236073017120361, -0.5257253050804138, -0.44721952080726624),
    (0.26286882162094116, -0.8090116381645203, -0.5257376432418823)
)
