import statistics

import bpy

from mathutils import Matrix
from math import radians

from bgl import *

from bpy.types import GizmoGroup, Operator, Gizmo
from bpy.props import EnumProperty, BoolProperty

from .. utility import addon, active_tool, modifier


class BC_OT_Translate(Operator):
    bl_idname = 'bc.translate'
    bl_label = 'Move Translate'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Move

LMB                    - translate
LMB+shift          - Copy objects
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

    def boolean(self, context, obj, cutter):
        mod = obj.modifiers.new(name='Boolean', type='BOOLEAN')
        mod.show_viewport = True
        mod.show_expanded = False
        mod.object = cutter
        mod.operation = 'DIFFERENCE'

    # TODO set option for user to set if he wants to copy modifiers or not when duplicating
    def modal(self, context, event):
        if event.shift:
            if self.axis == 'X':
                if event.ctrl:
                    for obj in context.selected_objects:
                        obj.location[0] = 0
                    return {'FINISHED'}
                else:
                    bpy.ops.object.duplicate_move('INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"constraint_axis":(True, False, False), "release_confirm":True})
                    for obj in context.selected_objects:
                        if obj.bc.target is not None:
                            self.boolean(context, obj.bc.target, obj)
                            modifier.sort(self, obj.bc.target)
                    # bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, True, True), release_confirm=True)
                    return {'FINISHED'}
            if self.axis == 'Y':
                if event.ctrl:
                    for obj in context.selected_objects:
                        obj.location[1] = 0
                    return {'FINISHED'}
                else:
                    bpy.ops.object.duplicate_move('INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"constraint_axis":(False, True, False), "release_confirm":True})
                    for obj in context.selected_objects:
                        if obj.bc.target is not None:
                            self.boolean(context, obj.bc.target, obj)
                            modifier.sort(self, obj.bc.target)
                    # bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, False, True), release_confirm=True)
                    return {'FINISHED'}
            if self.axis == 'Z':
                if event.ctrl:
                    for obj in context.selected_objects:
                        obj.location[2] = 0
                    return {'FINISHED'}
                else:
                    bpy.ops.object.duplicate_move('INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"constraint_axis":(False, False, True), "release_confirm":True})
                    for obj in context.selected_objects:
                        if obj.bc.target is not None:
                            self.boolean(context, obj.bc.target, obj)
                            modifier.sort(self, obj.bc.target)
                    # bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, True, False), release_confirm=True)
                    return {'FINISHED'}

        else:
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=self.axis_set, release_confirm=True)
        return {'FINISHED'}


class BC_OT_Rotate(Operator):
    bl_idname = 'bc.rotate'
    bl_label = 'Move Rotate'
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
                for obj in context.selected_objects:
                    obj.rotation_euler[0] = 0
                return {'FINISHED'}
            if self.axis == 'Y':
                for obj in context.selected_objects:
                    obj.rotation_euler[1] = 0
                return {'FINISHED'}
            if self.axis == 'Z':
                for obj in context.selected_objects:
                    obj.rotation_euler[2] = 0
                return {'FINISHED'}

        else:
            bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=self.axis_set, release_confirm=True)
        return {'FINISHED'}


class BC_OT_Resize(Operator):
    bl_idname = 'bc.resize'
    bl_label = 'Move Resize'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Scale

LMB                    - Scale
LMB+shift          - Sceale on other axis
LMB+shift+ctrl - Reset Scale
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
        if event.shift:
            if self.axis == 'X':
                if event.ctrl:
                    for obj in context.selected_objects:
                        obj.scale[0] = 1
                    return {'FINISHED'}
                else:
                    bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=(False, True, True), release_confirm=True)
                    return {'FINISHED'}
            if self.axis == 'Y':
                if event.ctrl:
                    for obj in context.selected_objects:
                        obj.scale[1] = 1
                    return {'FINISHED'}
                else:
                    bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=(True, False, True), release_confirm=True)
                    return {'FINISHED'}
            if self.axis == 'Z':
                if event.ctrl:
                    for obj in context.selected_objects:
                        obj.scale[2] = 1
                    return {'FINISHED'}
                else:
                    bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=(True, True, False), release_confirm=True)
                    return {'FINISHED'}

        else:
            bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=self.axis_set, release_confirm=True)
        return {'FINISHED'}


class BC_OT_AddTransformGizmo(Operator):
    bl_idname = 'bc.add_transform'
    bl_label = 'Gizmo transform Add'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Show Transform Gizmo'

    def execute(self, context):
        bpy.context.window_manager.gizmo_group_type_ensure(BC_WGT_TransformGizmoGroup.bl_idname)
        addon.preference().transform_gizmo = True
        return {'FINISHED'}


class BC_OT_RemoveTransformGizmo(Operator):
    bl_idname = 'bc.remove_transform'
    bl_label = 'Gizmo transform Remove'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Hide Transform Gizmo'

    def execute(self, context):
        bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_TransformGizmoGroup.bl_idname)
        addon.preference().transform_gizmo = False
        return {'FINISHED'}


class BC_WGT_TransformGizmoGroup(GizmoGroup):
    bl_idname = 'bc.transformgizmogroup'
    bl_label = 'Move Gizmo'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @classmethod
    def poll(cls, context):
        if active_tool().idname == 'BoxCutter':

            if len(context.selected_objects) > 0:
                if getattr(context.active_object, 'type', '') == 'MESH':
                    if getattr(context.active_object, 'mode', '') == 'OBJECT':
                        # bpy.context.window_manager.gizmo_group_type_ensure(BC_WGT_TransformGizmoGroup.bl_idname)
                        return True

        # bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_TransformGizmoGroup.bl_idname)
        return False

    def setup(self, context):

        mpr_x = self.gizmos.new('GIZMO_GT_arrow_3d')
        opx = mpr_x.target_set_operator('bc.translate')
        opx.axis = 'X'
        mpr_x.use_draw_modal = False
        mpr_x.scale_basis = 1.2
        mpr_x.color = 1, 0.2, 0.322
        mpr_x.alpha = 0.5
        mpr_x.color_highlight = 1.0, 1.0, 1.0
        mpr_x.alpha_highlight = 1.0

        scale_x = self.gizmos.new('GIZMO_GT_arrow_3d')
        spx = scale_x.target_set_operator('bc.resize')
        spx.axis = 'X'
        scale_x.use_draw_modal = False
        scale_x.draw_style = 'BOX'
        scale_x.scale_basis = 0.7
        scale_x.color = 1, 0.2, 0.322
        scale_x.alpha = 0.5
        scale_x.color_highlight = 1.0, 1.0, 1.0
        scale_x.alpha_highlight = 1.0

        dial_x = self.gizmos.new(BC_GT_TransformCustomGizmo.bl_idname)
        rpx = dial_x.target_set_operator('bc.rotate')
        rpx.axis = 'X'
        dial_x.use_draw_modal = False
        dial_x.scale_basis = 1
        dial_x.color = 1, 0.2, 0.322
        dial_x.alpha = 0.5
        dial_x.color_highlight = 1.0, 1.0, 1.0
        dial_x.alpha_highlight = 1.0

        mpr_y = self.gizmos.new('GIZMO_GT_arrow_3d')
        opy = mpr_y.target_set_operator('bc.translate')
        opy.axis = 'Y'
        mpr_y.use_draw_modal = False
        mpr_y.scale_basis = 1.2
        mpr_y.color = 0.545, 0.863, 0
        mpr_y.alpha = 0.5
        mpr_y.color_highlight = 1.0, 1.0, 1.0
        mpr_y.alpha_highlight = 1.0

        scale_y = self.gizmos.new('GIZMO_GT_arrow_3d')
        spy = scale_y.target_set_operator('bc.resize')
        spy.axis = 'Y'
        scale_y.use_draw_modal = False
        scale_y.draw_style = 'BOX'
        scale_y.scale_basis = 0.7
        scale_y.color = 0.545, 0.863, 0
        scale_y.alpha = 0.5
        scale_y.color_highlight = 1.0, 1.0, 1.0
        scale_y.alpha_highlight = 1.0

        dial_y = self.gizmos.new(BC_GT_TransformCustomGizmo.bl_idname)
        rpy = dial_y.target_set_operator('bc.rotate')
        rpy.axis = 'Y'
        dial_y.use_draw_modal = False
        dial_y.scale_basis = 0.9
        dial_y.color = 0.545, 0.863, 0
        dial_y.alpha = 0.5
        dial_y.color_highlight = 1.0, 1.0, 1.0
        dial_y.alpha_highlight = 1.0

        mpr_z = self.gizmos.new('GIZMO_GT_arrow_3d')
        opz = mpr_z.target_set_operator('bc.translate')
        opz.axis = 'Z'
        mpr_z.use_draw_modal = False
        mpr_z.scale_basis = 1.2
        mpr_z.color = 0.157, 0.565, 1
        mpr_z.alpha = 0.5
        mpr_z.color_highlight = 1.0, 1.0, 1.0
        mpr_z.alpha_highlight = 1.0

        scale_z = self.gizmos.new('GIZMO_GT_arrow_3d')
        spz = scale_z.target_set_operator('bc.resize')
        spz.axis = 'Z'
        scale_z.use_draw_modal = False
        scale_z.draw_style = 'BOX'
        scale_z.scale_basis = 0.7
        scale_z.color = 0.157, 0.565, 1
        scale_z.alpha = 0.5
        scale_z.color_highlight = 1.0, 1.0, 1.0
        scale_z.alpha_highlight = 1.0

        dial_z = self.gizmos.new(BC_GT_TransformCustomGizmo.bl_idname)
        rpz = dial_z.target_set_operator('bc.rotate')
        rpz.axis = 'Z'
        dial_z.use_draw_modal = False
        dial_z.scale_basis = 1
        dial_z.color = 0.157, 0.565, 1
        dial_z.alpha = 0.5
        dial_z.color_highlight = 1.0, 1.0, 1.0
        dial_z.alpha_highlight = 1.0

        self.mpr_z = mpr_z
        self.scale_z = scale_z
        self.dial_z = dial_z
        self.mpr_x = mpr_x
        self.scale_x = scale_x
        self.dial_x = dial_x
        self.mpr_y = mpr_y
        self.scale_y = scale_y
        self.dial_y = dial_y


    def draw_prepare(self, context):

        abc = active_tool()
        if abc.idname != 'BoxCutter':
            bpy.context.window_manager.gizmo_group_type_unlink_delayed(BC_WGT_TransformGizmoGroup.bl_idname)

        mpr_z = self.mpr_z
        scale_z = self.scale_z
        dial_z = self.dial_z
        mpr_x = self.mpr_x
        scale_x = self.scale_x
        dial_x = self.dial_x
        mpr_y = self.mpr_y
        scale_y = self.scale_y
        dial_y = self.dial_y

        selection = context.selected_objects
        origins_loc = [a.location for a in selection]
        orig_loc = [statistics.median(col) for col in zip(*origins_loc)]
        orig_rot = context.active_object.rotation_euler

        if context.scene.transform_orientation_slots[0].type == 'LOCAL':
            x_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Y')
            x_dial_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'Y')
            y_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'X')
            z_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Z')
            x_scale_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'Y')
            y_scale_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'X')
            z_scale_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-180), 4, 'X')

        else:
            x_rot_mat = Matrix.Rotation(radians(90), 4, 'Y')
            x_dial_rot_mat = Matrix.Rotation(radians(-90), 4, 'Y')
            y_rot_mat = Matrix.Rotation(radians(-90), 4, 'X')
            z_rot_mat = Matrix.Rotation(radians(90), 4, 'Z')
            x_scale_rot_mat = Matrix.Rotation(radians(-90), 4, 'Y')
            y_scale_rot_mat = Matrix.Rotation(radians(90), 4, 'X')
            z_scale_rot_mat = Matrix.Rotation(radians(-180), 4, 'X')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_scale_mat = Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1))

        z_matrix_world = orig_loc_mat @ z_rot_mat @ orig_scale_mat
        x_matrix_world = orig_loc_mat @ x_rot_mat @ orig_scale_mat
        x_dial_matrix_world = orig_loc_mat @ x_dial_rot_mat @ orig_scale_mat
        y_matrix_world = orig_loc_mat @ y_rot_mat @ orig_scale_mat

        x_scale_matrix_world = orig_loc_mat @ x_scale_rot_mat @ orig_scale_mat
        y_scale_matrix_world = orig_loc_mat @ y_scale_rot_mat @ orig_scale_mat
        z_scale_matrix_world = orig_loc_mat @ z_scale_rot_mat @ orig_scale_mat

        mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_y.matrix_basis = y_matrix_world.normalized()

        dial_x.matrix_basis = x_dial_matrix_world.normalized()
        dial_y.matrix_basis = y_matrix_world.normalized()
        dial_z.matrix_basis = z_matrix_world.normalized()

        scale_z.matrix_basis = z_scale_matrix_world.normalized()
        scale_x.matrix_basis = x_scale_matrix_world.normalized()
        scale_y.matrix_basis = y_scale_matrix_world.normalized()


class BC_GT_TransformCustomGizmo(Gizmo):
    bl_idname = 'bc.facegizmo'
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
