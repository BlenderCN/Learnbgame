import bpy

from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools
from bpy.props import FloatProperty
from bpy.types import (
    GizmoGroup,
    Operator
)
from mathutils import Matrix, Vector
from math import radians
from ... preferences import get_preferences


class HopsArrayGizmoGroup(GizmoGroup):
    bl_idname = "hops.array_gizmogroup"
    bl_label = "Array Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

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
        # Run an operator using the dial gizmo
        ob = context.active_object
        mpr_z = self.gizmos.new("GIZMO_GT_arrow_3d")

        mpr_x = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_x2 = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_x3 = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_x3.target_set_operator("hops.gizmo_array_x")

        mpr_y = self.gizmos.new("GIZMO_GT_arrow_3d")

        orig_loc, orig_rot, orig_scale = ob.matrix_basis.decompose()

        z_rot_mat = orig_rot.to_matrix().to_4x4()
        x_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Y')
        y_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'X')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_loc_mat_offset = Matrix.Translation(orig_loc + Vector((0, 0, 2)))

        orig_scale_mat = Matrix.Scale(orig_scale[0], 4, (1, 0, 0)) @ Matrix.Scale(orig_scale[1], 4, (0, 1, 0)) @ Matrix.Scale(orig_scale[2], 4, (0, 0, 1))

        z_matrix_world = orig_loc_mat @ z_rot_mat @ orig_scale_mat
        x_matrix_world = orig_loc_mat @ x_rot_mat @ orig_scale_mat
        x_matrix_world2 = orig_loc_mat_offset @ z_rot_mat @ orig_scale_mat

        y_matrix_world = orig_loc_mat @ y_rot_mat @ orig_scale_mat

        mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_z.line_width = 0.1
        # mpr_z.draw_style = 'BOX'
        mpr_z.color = 0.157, 0.565, 1
        mpr_z.alpha = 0.5
        mpr_z.scale_basis = 1.3

        mpr_z.color_highlight = 1.0, 1.0, 1.0
        mpr_z.alpha_highlight = 1.0

        mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_x.line_width = 0.1
        # mpr_x.draw_style = 'BOX'
        mpr_x.color = 1, 0.2, 0.322
        mpr_x.alpha = 0.5
        mpr_x.scale_basis = 1.3

        mpr_x2.matrix_basis = x_matrix_world.normalized()
        mpr_x2.line_width = 0.0
        mpr_x2.draw_style = 'BOX'
        mpr_x2.color = 1, 0.2, 0.322
        mpr_x2.alpha = 0.5
        mpr_x2.scale_basis = 0.8

        mpr_x3.matrix_basis = x_matrix_world.normalized()
        # mpr_x3.matrix_offset = x_matrix_world2.normalized()
        mpr_x3.line_width = 0
        mpr_x3.draw_style = 'BOX'
        mpr_x3.color = 1, 0.2, 0.322
        mpr_x3.alpha = 0.5
        mpr_x3.scale_basis = 1.8
        # mpr_x3.hide = True

        mpr_x.color_highlight = 1.0, 1.0, 1.0
        mpr_x.alpha_highlight = 1.0

        mpr_y.matrix_basis = y_matrix_world.normalized()
        mpr_y.line_width = 0.1
        # mpr_y.draw_style = 'BOX'
        mpr_y.color = 0.545, 0.863, 0
        mpr_y.alpha = 0.5
        mpr_y.scale_basis = 1.3

        mpr_y.color_highlight = 1.0, 1.0, 1.0
        mpr_y.alpha_highlight = 1.0

        self.mpr_z = mpr_z
        self.mpr_x = mpr_x
        self.mpr_x2 = mpr_x2
        self.mpr_x3 = mpr_x3
        self.mpr_y = mpr_y


    def draw_prepare(self, context):
        ob = context.object

        orig_loc, orig_rot, orig_scale = ob.matrix_basis.decompose()

        z_rot_mat = orig_rot.to_matrix().to_4x4()
        x_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Y')
        y_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'X')

        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_loc_mat_offset = Matrix.Translation(orig_loc + Vector((0, 0, 2)))

        orig_scale_mat = Matrix.Scale(orig_scale[0], 4, (1, 0, 0)) @ Matrix.Scale(orig_scale[1], 4, (0, 1, 0)) @ Matrix.Scale(orig_scale[2], 4, (0, 0, 1))

        z_matrix_world = orig_loc_mat @ z_rot_mat @ orig_scale_mat
        x_matrix_world = orig_loc_mat @ x_rot_mat @ orig_scale_mat
        x_matrix_world2 = orig_loc_mat_offset @ z_rot_mat @ orig_scale_mat

        y_matrix_world = orig_loc_mat @ y_rot_mat @ orig_scale_mat

        mpr_z = self.mpr_z
        mpr_x = self.mpr_x
        mpr_x2 = self.mpr_x2
        mpr_x3 = self.mpr_x3
        mpr_y = self.mpr_y

        def move_get_cb_x():
            return ob.hops.array_x

        def move_get_cb_x3():
            return ob.hops.array_x

        def move_set_cb_x(value):
            ob.hops.array_x = value
            ob.modifiers["Array"].constant_offset_displace[0] = ob.hops.array_x

        def move_get_cb_y():
            return ob.hops.array_y

        def move_set_cb_y(value):
            ob.hops.array_y = value
            ob.modifiers["Array"].constant_offset_displace[1] = ob.hops.array_y

        def move_get_cb_z():
            return ob.hops.array_z

        def move_set_cb_z(value):
            ob.hops.array_z = value
            ob.modifiers["Array"].constant_offset_displace[2] = ob.hops.array_z

        mpr_x.target_set_handler("offset", get=move_get_cb_x, set=move_set_cb_x)
        mpr_x2.target_set_handler("offset", get=move_get_cb_x, set=move_set_cb_x)
        mpr_x3.target_set_handler("offset", get=move_get_cb_x3, set=move_set_cb_x)
        mpr_y.target_set_handler("offset", get=move_get_cb_y, set=move_set_cb_y)
        mpr_z.target_set_handler("offset", get=move_get_cb_z, set=move_set_cb_z)

        mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_x2.matrix_basis = x_matrix_world.normalized()
        mpr_x3.matrix_basis = x_matrix_world.normalized()
        mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_y.matrix_basis = y_matrix_world.normalized()


class HopsArrayExecuteXmGizmo(Operator):
    bl_idname = "hops.gizmo_array_x"
    bl_label = "Array X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = context.active_object

        array_modifier = None
        for modifier in ob.modifiers:
            if modifier.type == "ARRAY":
                array_modifier = modifier
                modifier.use_constant_offset = True
                modifier.use_relative_offset = False
                modifier.count = modifier.count + 1

        if array_modifier is None:
            array_modifier = ob.modifiers.new("Array", "ARRAY")
            array_modifier.use_constant_offset = True
            array_modifier.use_relative_offset = False

        return {'FINISHED'}

    def modifiers_by_name(self, obj):
        return [x for x in obj.modifiers if x.type in {"ARRAY"}]