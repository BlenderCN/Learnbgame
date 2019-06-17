import bpy
import bpy_extras.view3d_utils
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.props import FloatProperty
from bpy.types import (
    GizmoGroup,
    Operator,
    Gizmo
)
from mathutils import Matrix, Vector
from math import radians
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences
from ... utils.objects import get_modifier_with_type
from .. Gizmos import custom_gizmo_shapes

from bl_ui.space_toolsystem_common import ToolSelectPanelHelper


class HOPS_OT_ArrayGizmo(Operator):
    bl_idname = "hops.array_gizmo"
    bl_label = "Array Gizmo"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Interactive Array Gizmo"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE"}

    def invoke(self, context, event):

        current_tool = ToolSelectPanelHelper._tool_get_active(context, 'VIEW_3D', None)[0][0]
        self.current_tool = current_tool
        if current_tool != "BoxCutter":
            bpy.ops.wm.tool_set_by_id(name="builtin.select", space_type='VIEW_3D')

        if context.space_data.type == 'VIEW_3D':
            wm = context.window_manager
            wm.gizmo_group_type_ensure(HOPS_OT_HopsArrayGizmoGroup.bl_idname)

        get_preferences().Hops_gizmo = True
        if context.space_data.type == 'VIEW_3D':
            get_preferences().Hops_gizmo_mirror = True
            context.area.tag_redraw()

        ob = context.active_object
        array = get_modifier_with_type(ob, "ARRAY")
        if array is not None:
            if array.name == "Array":
                if array.use_relative_offset:

                    dimensions_x = ob.dimensions[0] / (abs(ob.modifiers["Array"].relative_offset_displace[0]) * (array.count - 1) + 1)
                    dimensions_y = ob.dimensions[1] / (abs(ob.modifiers["Array"].relative_offset_displace[1]) * (array.count - 1) + 1)
                    dimensions_z = ob.dimensions[2] / (abs(ob.modifiers["Array"].relative_offset_displace[2]) * (array.count - 1) + 1)

                    ob.hops.array_x = dimensions_x * ob.modifiers["Array"].relative_offset_displace[0]
                    ob.hops.array_y = dimensions_y * ob.modifiers["Array"].relative_offset_displace[1]
                    ob.hops.array_z = dimensions_z * ob.modifiers["Array"].relative_offset_displace[2]

                else:

                    ob.hops.array_x = ob.modifiers["Array"].constant_offset_displace[0]
                    ob.hops.array_y = ob.modifiers["Array"].constant_offset_displace[1]
                    ob.hops.array_z = ob.modifiers["Array"].constant_offset_displace[2]

        # bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "HEADER", "POST_PIXEL")
        context.area.header_text_set("Hardops Array    Add Array Modifier")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if get_preferences().Hops_gizmo is False:
            bpy.ops.wm.tool_set_by_id(name=self.current_tool, space_type='VIEW_3D')
            context.window_manager.gizmo_group_type_unlink_delayed(HOPS_OT_HopsArrayGizmoGroup.bl_idname)
            context.area.header_text_set(text=None)
            # bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "HEADER")
            return {"CANCELLED"}

        ob = context.active_object
        array = get_modifier_with_type(ob, "ARRAY")
        if array is None:
            array = ob.modifiers.new("Array", "ARRAY")
            array.use_constant_offset = False
            array.use_relative_offset = True
            array.count = 2
            array.show_expanded = False
            array.relative_offset_displace[0] = 0

        else:
            count = ob.modifiers["Array"].count
            relative = ob.modifiers["Array"].relative_offset_displace
            constant = ob.modifiers["Array"].constant_offset_displace
            context.area.header_text_set("Hardops Array    Count: {}    Relative: x: {:.3f}  y: {:.3f}  z: {:.3f}    Constant: x: {:.3f}  y: {:.3f}  z: {:.3f} ".format(count, relative[0], relative[1], relative[2], constant[0], constant[1], constant[2]))

        if event.type == 'MOUSEMOVE':
            return {"PASS_THROUGH"}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {"PASS_THROUGH"}

        if event.type == 'LEFTMOUSE':
            return {"PASS_THROUGH"}

        if event.type in ("ESC", "RIGHTMOUSE"):
            bpy.ops.wm.tool_set_by_id(name=self.current_tool, space_type='VIEW_3D')
            context.window_manager.gizmo_group_type_unlink_delayed(HOPS_OT_HopsArrayGizmoGroup.bl_idname)
            # bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "HEADER")
            context.area.header_text_set(text=None)
            context.area.tag_redraw()
            # context.area.tag_redraw()
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def draw_ui(self, context):

        object = context.active_object

        location = object.location
        region = context.region
        rv3d = context.region_data

        x = 2
        y = 2

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()

        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        vertices = (
            (x - 1 * factor, y + 23 * factor), (x - 1 * factor, y + 4 * factor), (x + 44 * factor, y + 23 * factor), (x + 44 * factor, y + 4 * factor),
            (x + 46 * factor, y + 23 * factor), (x + 46 * factor, y + 4 * factor), (x + 220 * factor, y + 23 * factor), (x + 220 * factor, y + 4 * factor),
            (x + 46 * factor, y + 42 * factor), (x + 46 * factor, y + 26 * factor), (x + 220 * factor, y + 42 * factor), (x + 220 * factor, y + 26 * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", get_preferences().Hops_hud_color)
        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        count = object.modifiers["Array"].count
        relative = object.modifiers["Array"].relative_offset_displace
        constant = object.modifiers["Array"].constant_offset_displace

        draw_text(str(count),
                  x + 27 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(relative[0], relative[1], relative[2]),
                  x + 50 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(constant[0], constant[1], constant[2]),
                  x + 50 * factor, y + 28 * factor, size=12, color=get_preferences().Hops_hud_text_color)


class HOPS_OT_HopsArrayGizmoGroup(GizmoGroup):
    bl_idname = "hops.array_gizmogroup2"
    bl_label = "Array Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @staticmethod
    def my_target_operator(context):
        wm = context.window_manager
        op = wm.operators[-1] if wm.operators else None
        if isinstance(op, HOPS_OT_ArrayGizmo):
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
        # Run an operator using the dial gizmo
        ob = context.active_object

        mpr_x = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_y = self.gizmos.new("GIZMO_GT_arrow_3d")
        mpr_z = self.gizmos.new("GIZMO_GT_arrow_3d")
        circle1 = self.gizmos.new(HOPS_GT_ArrayPlusShapeGizmo.bl_idname)
        circle1.target_set_operator("hops.array_plus")
        circle2 = self.gizmos.new(HOPS_GT_ArrayMinusShapeGizmo.bl_idname)
        circle2.target_set_operator("hops.array_minus")
        circle3 = self.gizmos.new(HOPS_GT_ArrayMinusShapeGizmo.bl_idname)
        circle3.target_set_operator("hops.array_minus")

        # mpr_x.matrix_basis = x_matrix_world.normalized()
        mpr_x.line_width = 0.1
        mpr_x.color = 1, 0.2, 0.322
        mpr_x.alpha = 0.5
        mpr_x.scale_basis = 1.3
        mpr_x.color_highlight = 1.0, 1.0, 1.0
        mpr_x.alpha_highlight = 1.0

        # mpr_y.matrix_basis = y_matrix_world.normalized()
        mpr_y.line_width = 0.1
        mpr_y.color = 0.545, 0.863, 0
        mpr_y.alpha = 0.5
        mpr_y.scale_basis = 1.3
        mpr_y.color_highlight = 1.0, 1.0, 1.0
        mpr_y.alpha_highlight = 1.0

        # mpr_z.matrix_basis = z_matrix_world.normalized()
        mpr_z.line_width = 0.1
        mpr_z.color = 0.157, 0.565, 1
        mpr_z.alpha = 0.5
        mpr_z.scale_basis = 1.3
        mpr_z.color_highlight = 1.0, 1.0, 1.0
        mpr_z.alpha_highlight = 1.0

        # circle1.matrix_basis = circle1_matrix.normalized()
        circle1.color = 0.4, 0.4, 0.4
        circle1.alpha = 0.5
        circle1.scale_basis = 0.17
        circle1.color_highlight = 1.0, 1.0, 1.0
        circle1.alpha_highlight = 1.0

        # circle2.matrix_basis = circle2_matrix.normalized()
        circle2.color = 0.4, 0.4, 0.4
        circle2.alpha = 0.5
        circle2.scale_basis = 0.17
        circle2.color_highlight = 1.0, 1.0, 1.0
        circle2.alpha_highlight = 1.0

        # circle3.matrix_basis = circle3_matrix.normalized()
        circle3.color = 0.4, 0.4, 0.4
        circle3.alpha = 0.5
        circle3.scale_basis = 0.17
        circle3.color_highlight = 1.0, 1.0, 1.0
        circle3.alpha_highlight = 1.0
        circle3.hide = True
        circle3.hide_select = True

        self.mpr_z = mpr_z
        self.mpr_x = mpr_x
        self.mpr_y = mpr_y
        self.circle1 = circle1
        self.circle2 = circle2
        self.circle3 = circle3

    def draw_prepare(self, context):
        ob = context.object

        array = get_modifier_with_type(ob, "ARRAY")

        orig_loc, orig_rot, orig_scale = ob.matrix_local.decompose()

        z_rot_mat = orig_rot.to_matrix().to_4x4()
        x_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(90), 4, 'Y')
        y_rot_mat = orig_rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(-90), 4, 'X')

        orig_scale_mat = Matrix.Scale(orig_scale[0], 4, (1, 0, 0)) @ Matrix.Scale(orig_scale[1], 4, (0, 1, 0)) @ Matrix.Scale(orig_scale[2], 4, (0, 0, 1))

        inv = ob.matrix_world.copy()
        inv.invert()

        location = ob.location
        region = context.region
        rv3d = context.region_data

        self.mpr_x.hide = True
        self.mpr_y.hide = True
        self.mpr_z.hide = True

        if array is not None:

            self.mpr_x.hide = False
            self.mpr_y.hide = False
            self.mpr_z.hide = False

            orig_loc_mat = Matrix.Translation(orig_loc)

            if ob.modifiers["Array"].use_relative_offset is True and ob.modifiers["Array"].use_constant_offset is False:

                dimensions_x = ob.dimensions[0] / (abs(ob.modifiers["Array"].relative_offset_displace[0]) * (array.count - 1) + 1)
                dimensions_y = ob.dimensions[1] / (abs(ob.modifiers["Array"].relative_offset_displace[1]) * (array.count - 1) + 1)
                dimensions_z = ob.dimensions[2] / (abs(ob.modifiers["Array"].relative_offset_displace[2]) * (array.count - 1) + 1)

                offset_x = dimensions_x * ob.modifiers["Array"].relative_offset_displace[0] * ob.scale[0]
                offset_y = dimensions_y * ob.modifiers["Array"].relative_offset_displace[1] * ob.scale[1]
                offset_z = dimensions_z * ob.modifiers["Array"].relative_offset_displace[2] * ob.scale[2]

            elif ob.modifiers["Array"].use_relative_offset is False and ob.modifiers["Array"].use_constant_offset is True:

                offset_x = ob.modifiers["Array"].constant_offset_displace[0] * ob.scale[0]
                offset_y = ob.modifiers["Array"].constant_offset_displace[1] * ob.scale[1]
                offset_z = ob.modifiers["Array"].constant_offset_displace[2] * ob.scale[2]

            else:

                offset_x = 0
                offset_y = 0
                offset_z = 0

            location = ob.location + (Vector((offset_x, offset_y, offset_z)) @ inv)

            orig_loc_mat_offset_x = Matrix.Translation(orig_loc + (Vector((0, offset_y, offset_z)) @ inv))
            orig_loc_mat_offset_y = Matrix.Translation(orig_loc + (Vector((offset_x, 0, offset_z)) @ inv))
            orig_loc_mat_offset_z = Matrix.Translation(orig_loc + (Vector((offset_x, offset_y, 0)) @ inv))

            x_matrix_world = orig_loc_mat_offset_x @ x_rot_mat @ orig_scale_mat
            y_matrix_world = orig_loc_mat_offset_y @ y_rot_mat @ orig_scale_mat
            z_matrix_world = orig_loc_mat_offset_z @ z_rot_mat @ orig_scale_mat

            mpr_z = self.mpr_z
            mpr_x = self.mpr_x
            mpr_y = self.mpr_y

            def move_get_cb_x():
                return ob.hops.array_x

            def move_get_cb_y():
                return ob.hops.array_y

            def move_get_cb_z():
                return ob.hops.array_z

            def move_set_cb_x(value):
                if ob.modifiers["Array"].use_relative_offset is True and ob.modifiers["Array"].use_constant_offset is False:
                    ob.hops.array_x = value
                    ob.modifiers["Array"].relative_offset_displace[0] = ob.hops.array_x / dimensions_x
                elif ob.modifiers["Array"].use_relative_offset is False and ob.modifiers["Array"].use_constant_offset is True:
                    ob.hops.array_x = value
                    ob.modifiers["Array"].constant_offset_displace[0] = ob.hops.array_x

            def move_set_cb_y(value):
                if ob.modifiers["Array"].use_relative_offset is True and ob.modifiers["Array"].use_constant_offset is False:
                    ob.hops.array_y = value
                    ob.modifiers["Array"].relative_offset_displace[1] = ob.hops.array_y / dimensions_y
                elif ob.modifiers["Array"].use_relative_offset is False and ob.modifiers["Array"].use_constant_offset is True:
                    ob.hops.array_y = value
                    ob.modifiers["Array"].constant_offset_displace[1] = ob.hops.array_y

            def move_set_cb_z(value):
                if ob.modifiers["Array"].use_relative_offset is True and ob.modifiers["Array"].use_constant_offset is False:
                    ob.hops.array_z = value
                    ob.modifiers["Array"].relative_offset_displace[2] = ob.hops.array_z / dimensions_z
                elif ob.modifiers["Array"].use_relative_offset is False and ob.modifiers["Array"].use_constant_offset is True:
                    ob.hops.array_z = value
                    ob.modifiers["Array"].constant_offset_displace[2] = ob.hops.array_z

            mpr_x.target_set_handler("offset", get=move_get_cb_x, set=move_set_cb_x)
            mpr_y.target_set_handler("offset", get=move_get_cb_y, set=move_set_cb_y)
            mpr_z.target_set_handler("offset", get=move_get_cb_z, set=move_set_cb_z)

            mpr_z.matrix_basis = z_matrix_world.normalized()
            mpr_x.matrix_basis = x_matrix_world.normalized()
            mpr_y.matrix_basis = y_matrix_world.normalized()

        location_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, location)
        circle1_offset = Vector((location_2d.x - 120, location_2d.y - 140))
        circle2_offset = Vector((location_2d.x - 160, location_2d.y - 140))
        circle3_offset = Vector((location_2d.x - 200, location_2d.y - 140))
        circle1_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle1_offset, location)
        circle2_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle2_offset, location)
        circle3_loc = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, circle3_offset, location)
        circle1_matrix = Matrix.Translation(circle1_loc) @ z_rot_mat @ orig_scale_mat
        circle2_matrix = Matrix.Translation(circle2_loc) @ z_rot_mat @ orig_scale_mat
        circle3_matrix = Matrix.Translation(circle3_loc) @ z_rot_mat @ orig_scale_mat
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


class HOPS_GT_ArrayMinusShapeGizmo(Gizmo):
    bl_idname = "VIEW3D_GT_auto_minus"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    __slots__ = (
        "custom_shape",
        "init_mouse_y",
        "init_value",
    )

    def draw(self, context):

        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.new_custom_shape('TRIS', custom_gizmo_shapes.cube), select_id=select_id)

    def setup(self):
        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', custom_gizmo_shapes.minus)

    def invoke(self, context, event):
        self.init_mouse_y = event.mouse_y
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)

    def modal(self, context, event, tweak):
        delta = (event.mouse_y - self.init_mouse_y) / 10.0
        if 'SNAP' in tweak:
            delta = round(delta)
        if 'PRECISE' in tweak:
            delta /= 10.0
        return {'RUNNING_MODAL'}


class HOPS_GT_ArrayPlusShapeGizmo(Gizmo):
    bl_idname = "VIEW3D_GT_auto_plus"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    __slots__ = (
        "custom_shape",
        "init_mouse_y",
        "init_value",
    )

    def draw(self, context):

        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.new_custom_shape('TRIS', custom_gizmo_shapes.cube), select_id=select_id)

    def setup(self):
        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', custom_gizmo_shapes.plus)

    def invoke(self, context, event):
        self.init_mouse_y = event.mouse_y
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)

    def modal(self, context, event, tweak):
        delta = (event.mouse_y - self.init_mouse_y) / 10.0
        if 'SNAP' in tweak:
            delta = round(delta)
        if 'PRECISE' in tweak:
            delta /= 10.0
        return {'RUNNING_MODAL'}


class HOPS_OT_ArrayPlus(Operator):
    bl_idname = "hops.array_plus"
    bl_label = "Add array step"
    bl_description = "+"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = context.object
        array = get_modifier_with_type(ob, "ARRAY")
        if array is None:
            array = ob.modifiers.new("Array", "ARRAY")
            array.use_constant_offset = True
            array.use_relative_offset = False
            array.count = 2
            array.show_expanded = False

        else:
            array.count += 1

        return {'FINISHED'}


class HOPS_OT_ArrayMinus(Operator):
    bl_idname = "hops.array_minus"
    bl_label = "Add array step"
    bl_description = "-"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = context.object
        array = get_modifier_with_type(ob, "ARRAY")
        if array is not None:
            if array.count == 2:
                for m in ob.modifiers:
                    if(m.name == "Array"):
                        ob.modifiers.remove(m)

                ob.hops.array_x = 0
                ob.hops.array_y = 0
                ob.hops.array_z = 0
            else:
                array.count -= 1

        context.area.tag_redraw()
        return {'FINISHED'}
