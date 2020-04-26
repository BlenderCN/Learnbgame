import bpy
import gpu
import mathutils
import math
from bgl import *
from bpy.props import EnumProperty
from bpy.types import (
    Gizmo,
    GizmoGroup,
    Operator
)
from mathutils import Matrix, Vector
from math import radians
from .. misc.mirrormirror import operation
from ... preferences import get_preferences
import bpy_extras.view3d_utils
from gpu_extras.batch import batch_for_shader
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... utils.space_2d import inside_polygon
from .. Gizmos import custom_gizmo_shapes


class HOPS_OT_MirrorExecuteXGizmo(Operator):
    bl_idname = "hops.mirror_execute_x_gizmo"
    bl_label = "Mirror selected via -X axis"
    bl_description = "Mirror via -X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self._operation = "MIRROR_X"
        if get_preferences().Hops_mirror_modal_revert:
            get_preferences().Hops_mirror_direction = "-"
            self.direction = "NEGATIVE_X"
        else:
            get_preferences().Hops_mirror_direction = "+"
            self.direction = "POSITIVE_X"
        self.used_axis = "X"

        if get_preferences().Hops_mirror_modal_use_cursor:
            self.x, self.y, self.z = bpy.context.scene.cursor_location
        else:
            self.x, self.y, self.z = bpy.context.object.location
        self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
        vec = Vector((1, 0, 0))
        mat = Matrix.Rotation(self.zx, 4, "X")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zy, 4, "Y")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zz, 4, "Z")
        vec.rotate(mat)
        self.nx = vec[0]
        self.ny = vec[1]
        self.nz = vec[2]

        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        get_preferences().Hops_gizmo_mirror_on = False
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteXmGizmo(Operator):
    bl_idname = "hops.mirror_execute_xm_gizmo"
    bl_label = "Mirror selected via X axis"
    bl_description = "Mirror via X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self._operation = "MIRROR_X"
        if get_preferences().Hops_mirror_modal_revert:
            get_preferences().Hops_mirror_direction = "+"
            self.direction = "POSITIVE_X"
        else:
            get_preferences().Hops_mirror_direction = "-"
            self.direction = "NEGATIVE_X"
        self.used_axis = "X"

        if get_preferences().Hops_mirror_modal_use_cursor:
            self.x, self.y, self.z = bpy.context.scene.cursor_location
        else:
            self.x, self.y, self.z = bpy.context.object.location
        self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
        vec = Vector((1, 0, 0))
        mat = Matrix.Rotation(self.zx, 4, "X")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zy, 4, "Y")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zz, 4, "Z")
        vec.rotate(mat)
        self.nx = vec[0]
        self.ny = vec[1]
        self.nz = vec[2]

        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        get_preferences().Hops_gizmo_mirror_on = False
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteYGizmo(Operator):
    bl_idname = "hops.mirror_execute_y_gizmo"
    bl_label = "Mirror selected via -Y axis"
    bl_description = "Mirror via -Y"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self._operation = "MIRROR_Y"
        if get_preferences().Hops_mirror_modal_revert:
            get_preferences().Hops_mirror_direction = "-"
            self.direction = "NEGATIVE_Y"
        else:
            get_preferences().Hops_mirror_direction = "+"
            self.direction = "POSITIVE_Y"
        self.used_axis = "Y"

        if get_preferences().Hops_mirror_modal_use_cursor:
            self.x, self.y, self.z = bpy.context.scene.cursor_location
        else:
            self.x, self.y, self.z = bpy.context.object.location
        self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
        vec = Vector((0, 1, 0))
        mat = Matrix.Rotation(self.zx, 4, "X")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zy, 4, "Y")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zz, 4, "Z")
        vec.rotate(mat)
        self.nx = vec[0]
        self.ny = vec[1]
        self.nz = vec[2]

        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        get_preferences().Hops_gizmo_mirror_on = False
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteYmGizmo(Operator):
    bl_idname = "hops.mirror_execute_ym_gizmo"
    bl_label = "Mirror selected via Y axis"
    bl_description = "Mirror via Y"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self._operation = "MIRROR_Y"
        if get_preferences().Hops_mirror_modal_revert:
            get_preferences().Hops_mirror_direction = "+"
            self.direction = "POSITIVE_Y"
        else:
            get_preferences().Hops_mirror_direction = "-"
            self.direction = "NEGATIVE_Y"
        self.used_axis = "Y"

        if get_preferences().Hops_mirror_modal_use_cursor:
            self.x, self.y, self.z = bpy.context.scene.cursor_location
        else:
            self.x, self.y, self.z = bpy.context.object.location
        self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
        vec = Vector((0, 1, 0))
        mat = Matrix.Rotation(self.zx, 4, "X")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zy, 4, "Y")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zz, 4, "Z")
        vec.rotate(mat)
        self.nx = vec[0]
        self.ny = vec[1]
        self.nz = vec[2]

        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        get_preferences().Hops_gizmo_mirror_on = False
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteZGizmo(Operator):
    bl_idname = "hops.mirror_execute_z_gizmo"
    bl_label = "Mirror selected via -Z axis"
    bl_description = "Mirror via -Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self._operation = "MIRROR_Z"
        if get_preferences().Hops_mirror_modal_revert:
            get_preferences().Hops_mirror_direction = "-"
            self.direction = "NEGATIVE_Z"
        else:
            get_preferences().Hops_mirror_direction = "+"
            self.direction = "POSITIVE_Z"
        self.used_axis = "Z"

        if get_preferences().Hops_mirror_modal_use_cursor:
            self.x, self.y, self.z = bpy.context.scene.cursor_location
        else:
            self.x, self.y, self.z = bpy.context.object.location
        self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
        vec = Vector((0, 0, 1))
        mat = Matrix.Rotation(self.zx, 4, "X")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zy, 4, "Y")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zz, 4, "Z")
        vec.rotate(mat)
        self.nx = vec[0]
        self.ny = vec[1]
        self.nz = vec[2]

        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        get_preferences().Hops_gizmo_mirror_on = False
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteZmGizmo(Operator):
    bl_idname = "hops.mirror_execute_zm_gizmo"
    bl_label = "Mirror selected via Z axis"
    bl_description = "Mirror via Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self._operation = "MIRROR_Z"
        if get_preferences().Hops_mirror_modal_revert:
            get_preferences().Hops_mirror_direction = "+"
            self.direction = "POSITIVE_Z"
        else:
            get_preferences().Hops_mirror_direction = "-"
            self.direction = "NEGATIVE_Z"
        self.used_axis = "Z"

        if get_preferences().Hops_mirror_modal_use_cursor:
            self.x, self.y, self.z = bpy.context.scene.cursor_location
        else:
            self.x, self.y, self.z = bpy.context.object.location
        self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
        vec = Vector((0, 0, 1))
        mat = Matrix.Rotation(self.zx, 4, "X")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zy, 4, "Y")
        vec.rotate(mat)
        mat = Matrix.Rotation(self.zz, 4, "Z")
        vec.rotate(mat)
        self.nx = vec[0]
        self.ny = vec[1]
        self.nz = vec[2]

        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        get_preferences().Hops_gizmo_mirror_on = False
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteOption1Gizmo(Operator):
    bl_idname = "hops.mirror_execute_option_1"
    bl_label = "Modifier"
    bl_description = "Symmetry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        if len(selected) == 1:
            get_preferences().Hops_mirror_modes = "SYMMETRY"
        else:
            get_preferences().Hops_mirror_modes_multi = "SYMMETRY"
        context.area.tag_redraw()
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteOption2Gizmo(Operator):
    bl_idname = "hops.mirror_execute_option_2"
    bl_label = "Bisect"
    bl_description = "Bisect"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        get_preferences().Hops_mirror_modes = "BISECT"
        context.area.tag_redraw()
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteOption4Gizmo(Operator):
    bl_idname = "hops.mirror_execute_option_4"
    bl_label = "Bisect"
    bl_description = "Mirror via active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        get_preferences().Hops_mirror_modes_multi = "VIA_ACTIVE"
        context.area.tag_redraw()
        return {'FINISHED'}


class HOPS_OT_MirrorExecuteOption3Gizmo(Operator):
    bl_idname = "hops.mirror_execute_option_3"
    bl_label = "Modifier"
    bl_description = "Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        get_preferences().Hops_mirror_modes = "MODIFIER"
        context.area.tag_redraw()
        return {'FINISHED'}


class HOPS_OT_MirrorRemoveGizmo(Operator):
    bl_idname = "hops.mirror_remove_gizmo"
    bl_label = "Mirror Gizmo Remove"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE"}

    def execute(self, context):
        wm = context.window_manager
        get_preferences().Hops_gizmo_mirror = False
        context.area.tag_redraw()
        bpy.types.WindowManager.gizmo_group_type_remove("Hops_mirror_gizmo")
        # bpy.types.WindowManager.Hops_mirror_gizmo

        return {'FINISHED'}


class HOPS_OT_MirrorGizmo(Operator):
    bl_idname = "hops.mirror_gizmo"
    bl_label = "Mirror Gizmo"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Modal Mirror"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE"}

    def invoke(self, context, event):

        if context.space_data.type == 'VIEW_3D':
            wm = context.window_manager
            wm.gizmo_group_type_ensure(HOPS_OT_MirrorGizmoGroup.bl_idname)

        #  bpy.ops.scene.update()
        # context.area.tag_redraw()
        get_preferences().Hops_gizmo_mirror_on = True
        if context.space_data.type == 'VIEW_3D':
            get_preferences().Hops_gizmo_mirror = True
            context.area.tag_redraw()

        # args = (context, )
        # self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if get_preferences().Hops_gizmo_mirror_on is False:
            context.window_manager.gizmo_group_type_unlink_delayed(HOPS_OT_MirrorGizmoGroup.bl_idname)
            return {"CANCELLED"}

        if event.type == 'MOUSEMOVE':
            return {"PASS_THROUGH"}

        if event.type == 'MIDDLEMOUSE':
            return {"PASS_THROUGH"}

        if event.type == 'LEFTMOUSE':
            if event.value is "PESES":
                context.area.tag_redraw()
                return {"PASS_THROUGH"}

        if event.type in ("ESC", "RIGHTMOUSE"):
            # get_preferences().Hops_gizmo_mirror = False
            # bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            context.window_manager.gizmo_group_type_unlink_delayed(HOPS_OT_MirrorGizmoGroup.bl_idname)
            # context.area.tag_redraw()
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def draw(self, context):

        object = bpy.context.active_object
        region = context.region
        rv3d = context.region_data

        location = object.location

        x, y = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, location)

        set_drawing_dpi(get_dpi())
        factor = 1

        self.box1 = [(x - 170 * factor, y - 90 * factor), (x - 170 * factor, y - 110 * factor), (x - 150 * factor, y - 90 * factor), (x - 150 * factor, y - 110 * factor)]
        indices = ((0, 1, 2), (1, 2, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": self.box1}, indices=indices)

        shader.bind()
        if get_preferences().Hops_mirror_modes == "SYMMETRY":
            shader.uniform_float("color", (0.17, 0.17, 0.17, 1))
        else:
            shader.uniform_float("color", (0.17, 0.3, 0.7, 1))

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)


class HOPS_OT_MirrorGizmoGroup(GizmoGroup):
    bl_idname = "hops.mirror_gizmogroup"
    bl_label = "Mirror Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @staticmethod
    def my_target_operator(context):
        wm = context.window_manager
        op = wm.operators[-1] if wm.operators else None
        if isinstance(op, HOPS_OT_MirrorGizmo):
            return op
        return None

    @staticmethod
    def my_view_orientation(context):
        rv3d = context.space_data.region_3d
        view_inv = rv3d.view_matrix.to_3x3()
        return view_inv.normalized()

    @classmethod
    def poll(cls, context):
        ob = context.object
        return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE"}

    def setup(self, context):
        selected = context.selected_objects
        if len(selected) == 1:
            self.multiselection = False
        else:
            self.multiselection = True

        # Run an operator using the dial gizmo
        ob = context.active_object
        mpr_z = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_z.target_set_operator("hops.mirror_execute_zm_gizmo")
        # props.constraint_axis = True, False, True
        # props.constraint_orientation = 'LOCAL'
        # props.release_confirm = True

        mpr_z2 = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_z2.target_set_operator("hops.mirror_execute_z_gizmo")

        mpr_x = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_x.target_set_operator("hops.mirror_execute_xm_gizmo")

        mpr_x2 = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_x2.target_set_operator("hops.mirror_execute_x_gizmo")

        mpr_y = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_y.target_set_operator("hops.mirror_execute_y_gizmo")

        mpr_y2 = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_y2.target_set_operator("hops.mirror_execute_ym_gizmo")

        circle1 = self.gizmos.new(HOPS_GT_MirrorCustomShapeGizmo.bl_idname)
        circle1.target_set_operator("hops.mirror_execute_option_1")

        circle2 = self.gizmos.new(HOPS_GT_MirrorCustomShapeGizmo.bl_idname)
        circle2.target_set_operator("hops.mirror_execute_option_2")

        circle3 = self.gizmos.new(HOPS_GT_MirrorCustomShapeGizmo.bl_idname)
        circle3.target_set_operator("hops.mirror_execute_option_3")

        orig_loc, orig_rot, orig_scale = ob.matrix_basis.decompose()
        # view_loc, view_rot, view_scale = self.my_view_orientation(context).decompose()

        # print(view_rot)



        z_rot_mat = orig_rot.to_matrix().to_4x4()
        z2_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-180), 4, 'X')
        x_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Y')
        x2_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'Y')
        y_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'X')
        y2_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'X')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_scale_mat = Matrix.Scale(orig_scale[0], 4, (1, 0, 0)) @ Matrix.Scale(orig_scale[1], 4, (0, 1, 0)) @ Matrix.Scale(orig_scale[2], 4, (0, 0, 1))

        z_matrix_world = orig_loc_mat @ z_rot_mat @ orig_scale_mat
        z2_matrix_world = orig_loc_mat @ z2_rot_mat @ orig_scale_mat
        x_matrix_world = orig_loc_mat @ x_rot_mat @ orig_scale_mat
        x2_matrix_world = orig_loc_mat @ x2_rot_mat @ orig_scale_mat
        y_matrix_world = orig_loc_mat @ y_rot_mat @ orig_scale_mat
        y2_matrix_world = orig_loc_mat @ y2_rot_mat @ orig_scale_mat

        location = ob.location
        region = context.region
        rv3d = context.region_data
        location_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, location)

        circle1_offset = Vector((location_2d.x - 140, location_2d.y - 160))
        circle2_offset = Vector((location_2d.x - 180, location_2d.y - 160))
        circle3_offset = Vector((location_2d.x - 220, location_2d.y - 160))
        circle1_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle1_offset, location)
        circle2_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle2_offset, location)
        circle3_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle3_offset, location)
        circle1_matrix = Matrix.Translation(circle1_loc) @ z_rot_mat @ orig_scale_mat
        circle2_matrix = Matrix.Translation(circle2_loc) @ z_rot_mat @ orig_scale_mat
        circle3_matrix = Matrix.Translation(circle3_loc) @ z_rot_mat @ orig_scale_mat


        circle1.matrix_basis = circle1_matrix.normalized()
        if get_preferences().Hops_mirror_modes == "MODIFIER":
            circle1.color = 0.157, 0.565, 1
        else:
            circle1.color = 0.4, 0.4, 0.4
        circle1.alpha = 0.5
        circle1.scale_basis = 0.22

        circle1.color_highlight = 1.0, 1.0, 1.0
        circle1.alpha_highlight = 1.0


        circle2.matrix_basis = circle2_matrix.normalized()
        if get_preferences().Hops_mirror_modes == "BISECT":
            circle2.color = 0.157, 0.565, 1
        else:
            circle2.color = 0.4, 0.4, 0.4
        circle2.alpha = 0.5
        circle2.scale_basis = 0.22

        circle2.color_highlight = 1.0, 1.0, 1.0
        circle2.alpha_highlight = 1.0

        circle3.matrix_basis = circle3_matrix.normalized()
        if get_preferences().Hops_mirror_modes == "SYMMETRY":
            circle3.color = 0.157, 0.565, 1
        else:
            circle3.color = 0.4, 0.4, 0.4
        circle3.alpha = 0.5
        circle3.scale_basis = 0.22

        circle3.color_highlight = 1.0, 1.0, 1.0
        circle3.alpha_highlight = 1.0

        mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_z.line_width = 0.1
        mpr_z.draw_style = 'BOX'
        mpr_z.color = 0.157, 0.565, 1
        mpr_z.alpha = 0.5
        mpr_z.scale_basis = 2.2

        mpr_z.color_highlight = 1.0, 1.0, 1.0
        mpr_z.alpha_highlight = 1.0

        mpr_z2.matrix_basis = z2_matrix_world.normalized()
        mpr_z2.line_width = 0.1
        mpr_z2.draw_style = 'BOX'
        mpr_z2.color = 0.157, 0.565, 1
        mpr_z2.alpha = 0.5
        mpr_z2.scale_basis = 2.2

        mpr_z2.color_highlight = 1.0, 1.0, 1.0
        mpr_z2.alpha_highlight = 1.0

        mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_x.line_width = 0.1
        mpr_x.draw_style = 'BOX'
        mpr_x.color = 1, 0.2, 0.322
        mpr_x.alpha = 0.5
        mpr_x.scale_basis = 2.2

        mpr_x.color_highlight = 1.0, 1.0, 1.0
        mpr_x.alpha_highlight = 1.0

        mpr_x2.matrix_basis = x2_matrix_world.normalized()
        mpr_x2.line_width = 0.1
        mpr_x2.draw_style = 'BOX'
        mpr_x2.color = 1, 0.2, 0.322
        mpr_x2.alpha = 0.5
        mpr_x2.scale_basis = 2.2

        mpr_x2.color_highlight = 1.0, 1.0, 1.0
        mpr_x2.alpha_highlight = 1.0

        mpr_y.matrix_basis = y_matrix_world.normalized()
        mpr_y.line_width = 0.1
        mpr_y.draw_style = 'BOX'
        mpr_y.color = 0.545, 0.863, 0
        mpr_y.alpha = 0.5
        mpr_y.scale_basis = 2.2

        mpr_y.color_highlight = 1.0, 1.0, 1.0
        mpr_y.alpha_highlight = 1.0

        mpr_y2.matrix_basis = y2_matrix_world.normalized()
        mpr_y2.line_width = 0.1
        mpr_y2.draw_style = 'BOX'
        mpr_y2.color = 0.545, 0.863, 0
        mpr_y2.alpha = 0.5
        mpr_y2.scale_basis = 2.2

        mpr_y2.color_highlight = 1.0, 1.0, 1.0
        mpr_y2.alpha_highlight = 1.0

        self.mpr_z = mpr_z
        self.mpr_z2 = mpr_z2
        self.mpr_x = mpr_x
        self.mpr_x2 = mpr_x2
        self.mpr_y = mpr_y
        self.mpr_y2 = mpr_y2
        self.circle1 = circle1
        self.circle2 = circle2
        self.circle3 = circle3



    def draw_prepare(self, context):
        selected = context.selected_objects
        if len(selected) == 1:
            self.multiselection = False
        else:
            self.multiselection = True

        ob = context.active_object

        orig_loc, orig_rot, orig_scale = ob.matrix_basis.decompose()
        # view_loc, view_rot, view_scale = self.my_view_orientation(context).decompose()

        z_rot_mat = orig_rot.to_matrix().to_4x4()
        z2_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-180), 4, 'X')
        x_rot_mat = orig_rot.to_matrix().to_4x4() @Matrix.Rotation(radians(90), 4, 'Y')
        x2_rot_mat = orig_rot.to_matrix().to_4x4() @Matrix.Rotation(radians(-90), 4, 'Y')
        y_rot_mat = orig_rot.to_matrix().to_4x4() @Matrix.Rotation(radians(90), 4, 'X')
        y2_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'X')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_scale_mat = Matrix.Scale(orig_scale[0], 4, (1, 0, 0)) @ Matrix.Scale(orig_scale[1], 4, (0, 1, 0)) @ Matrix.Scale(orig_scale[2], 4, (0, 0, 1))

        z_matrix_world = orig_loc_mat @ z_rot_mat @ orig_scale_mat
        z2_matrix_world = orig_loc_mat @ z2_rot_mat @ orig_scale_mat
        x_matrix_world = orig_loc_mat @ x_rot_mat @ orig_scale_mat
        x2_matrix_world = orig_loc_mat @ x2_rot_mat @ orig_scale_mat
        y_matrix_world = orig_loc_mat @ y_rot_mat @ orig_scale_mat
        y2_matrix_world = orig_loc_mat @ y2_rot_mat @ orig_scale_mat

        location = ob.location
        region = context.region
        rv3d = context.region_data

        location_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, location)
        circle1_offset = Vector((location_2d.x - 140, location_2d.y - 160))
        circle2_offset = Vector((location_2d.x - 180, location_2d.y - 160))
        circle3_offset = Vector((location_2d.x - 220, location_2d.y - 160))
        circle1_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle1_offset, location)
        circle2_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle2_offset, location)
        circle3_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle3_offset, location)
        circle1_matrix = Matrix.Translation(circle1_loc) @ z_rot_mat @ orig_scale_mat
        circle2_matrix = Matrix.Translation(circle2_loc) @ z_rot_mat @ orig_scale_mat
        circle3_matrix = Matrix.Translation(circle3_loc) @ z_rot_mat @ orig_scale_mat

        mpr_z = self.mpr_z
        mpr_z2 = self.mpr_z2
        mpr_x = self.mpr_x
        mpr_x2 = self.mpr_x2
        mpr_y = self.mpr_y
        mpr_y2 = self.mpr_y2
        circle1 = self.circle1
        circle2 = self.circle2
        circle3 = self.circle3

        view_inv = self.my_view_orientation(context)

        rv3d = context.space_data.region_3d
        view_inv = rv3d.view_matrix.to_3x3()
        # view y axis
        plane_no = view_inv[1].normalized()

        op = self.my_target_operator(context)
        co = circle1_loc
        no = Vector(plane_no).normalized()

        circle1.matrix_basis = circle1_matrix.normalized()
        self.view_inv = view_inv
        self.rotate_axis = view_inv[2].xyz
        self.rotate_up = view_inv[1].xyz

        no_z = self.rotate_axis
        no_y = (no - (no.project(no_z))).normalized()
        no_x = self.rotate_axis.cross(no_y)

        matrix = circle1.matrix_basis
        matrix.identity()
        matrix.col[0].xyz = no_x
        matrix.col[1].xyz = no_y
        matrix.col[2].xyz = no_z
        matrix.col[3].xyz = co

        co = circle2_loc

        circle2.matrix_basis = circle2_matrix.normalized()
        self.view_inv = view_inv
        self.rotate_axis = view_inv[2].xyz
        self.rotate_up = view_inv[1].xyz

        no_z = self.rotate_axis
        no_y = (no - (no.project(no_z))).normalized()
        no_x = self.rotate_axis.cross(no_y)

        matrix = circle2.matrix_basis
        matrix.identity()
        matrix.col[0].xyz = no_x
        matrix.col[1].xyz = no_y
        matrix.col[2].xyz = no_z
        matrix.col[3].xyz = co

        circle3.matrix_basis = circle3_matrix.normalized()
        self.view_inv = view_inv
        self.rotate_axis = view_inv[2].xyz
        self.rotate_up = view_inv[1].xyz

        co = circle3_loc

        no_z = self.rotate_axis
        no_y = (no - (no.project(no_z))).normalized()
        no_x = self.rotate_axis.cross(no_y)

        matrix = circle3.matrix_basis
        matrix.identity()
        matrix.col[0].xyz = no_x
        matrix.col[1].xyz = no_y
        matrix.col[2].xyz = no_z
        matrix.col[3].xyz = co

        if self.multiselection is True:
            if get_preferences().Hops_mirror_modes_multi == "SYMMETRY":
                circle1.color = 0.545, 0.863, 0
            else:
                circle1.color = 0.4, 0.4, 0.4
        else:
            if get_preferences().Hops_mirror_modes == "SYMMETRY":
                circle1.color = 0.157, 0.565, 1
            else:
                circle1.color = 0.4, 0.4, 0.4

        if self.multiselection is True:
            if get_preferences().Hops_mirror_modes_multi == "VIA_ACTIVE":
                circle2.target_set_operator("hops.mirror_execute_option_4")
                circle2.color = 0.545, 0.863, 0
            else:
                circle2.color = 0.4, 0.4, 0.4
        else:
            if get_preferences().Hops_mirror_modes == "BISECT":
                circle2.target_set_operator("hops.mirror_execute_option_2")
                circle2.color = 0.157, 0.565, 1
            else:
                circle2.color = 0.4, 0.4, 0.4

        if self.multiselection is True:
            circle3.hide = True
        else:
            circle3.hide = False
        if get_preferences().Hops_mirror_modes == "MODIFIER":
            circle3.color = 0.157, 0.565, 1
        else:
            circle3.color = 0.4, 0.4, 0.4

        mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_z2.matrix_basis = z2_matrix_world.normalized()
        mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_x2.matrix_basis = x2_matrix_world.normalized()
        mpr_y.matrix_basis = y_matrix_world.normalized()
        mpr_y2.matrix_basis = y2_matrix_world.normalized()




class HOPS_GT_MirrorCustomShapeGizmo(Gizmo):
    bl_idname = "VIEW3D_GT_auto_facemap"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    __slots__ = (
        "custom_shape",
        "init_mouse_y",
        "init_value",
    )

##    def _update_offset_matrix(self):
##        # offset behind the light
##        print("_update_offset_matrix")
##        self.matrix_offset.col[3][2] = self.target_get_value("offset") / -10.0

    def draw(self, context):
##        self._update_offset_matrix()
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
##        self._update_offset_matrix()
        self.draw_custom_shape(self.new_custom_shape('TRIS', custom_gizmo_shapes.cube), select_id=select_id)

    def setup(self):
        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', custom_gizmo_shapes.cube)

    def invoke(self, context, event):
        self.init_mouse_y = event.mouse_y
##        self.init_value = self.target_get_value("offset")
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)
##        if cancel:
##            self.target_set_value("offset", self.init_value)

    def modal(self, context, event, tweak):
        delta = (event.mouse_y - self.init_mouse_y) / 10.0
        if 'SNAP' in tweak:
            delta = round(delta)
        if 'PRECISE' in tweak:
            delta /= 10.0
##        value = self.init_value + delta
##        self.target_set_value("offset", value)
##        context.area.header_text_set("My Gizmo: %.4f" % value)
        return {'RUNNING_MODAL'}

##class MyCustomShapeWidgetGroup(GizmoGroup):
##    bl_idname = "OBJECT_GGT_light_test"
##    bl_label = "Test Light Widget"
##    bl_space_type = 'VIEW_3D'
##    bl_region_type = 'WINDOW'
##    bl_options = {'3D', 'PERSISTENT'}
##
##    @classmethod
##    def poll(cls, context):
##        ob = context.object
##        return (ob and ob.type == 'LIGHT')
##
##    def setup(self, context):
##        # Assign the 'offset' target property to the light energy.
##        ob = context.object
##        mpr = self.gizmos.new(MyCustomShapeWidget.bl_idname)
##        mpr.target_set_prop("offset", ob.data, "energy")
##
##        mpr.color = 1.0, 0.5, 1.0
##        mpr.alpha = 0.5
##
##        mpr.color_highlight = 1.0, 1.0, 1.0
##        mpr.alpha_highlight = 0.5
##
##        # units are large, so shrink to something more reasonable.
##        mpr.scale_basis = 0.1
##        mpr.use_draw_modal = True
##
##        self.energy_widget = mpr
##
##    def refresh(self, context):
##        ob = context.object
##        mpr = self.energy_widget
##        mpr.matrix_basis = ob.matrix_world.normalized()

