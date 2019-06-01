import bpy
from bpy.props import IntProperty, EnumProperty
import math
from .. import M3utils as m3
from .. utils.operators import unlink_render_result


axisitems = [("X", "X", ""),
             ("Y", "Y", ""),
             ("Z", "Z", "")]


class DecalRotate(bpy.types.Operator):
    bl_idname = "machin3.decal_rotate"
    bl_label = "MACHIN3: Rotate Decal"
    bl_options = {'REGISTER', 'UNDO'}

    axis = EnumProperty(name="Axis", items=axisitems, default="Z")
    angle = IntProperty(name="Angle", default=0)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        if context.active_object.mode == "OBJECT":
            row = col.row()
            row.prop(self, "axis", expand=True)
            col.prop(self, "angle")

    def execute(self, context):
        decal_rotate(-self.angle, self.axis, context)

        return {'FINISHED'}


def decal_rotate(amountint, axis, context):
    mode = m3.get_mode()
    if context.area.type == "VIEW_3D":
        if mode == "OBJECT":
            pivot = m3.change_pivot('ACTIVE_ELEMENT')

            if axis == "X":
                axis = (1, 0, 0)
                constraint_axis=(True, False, False)
            elif axis == "Y":
                axis = (0, 1, 0)
                constraint_axis=(False, True, False)
            elif axis == "Z":
                axis = (0, 0, 1)
                constraint_axis=(False, False, True)

            bpy.ops.transform.rotate(value=math.radians(amountint), axis=axis, constraint_axis=constraint_axis, constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

            m3.change_pivot(pivot)
        else:
            if amountint == 45:
                amountint = 90
            elif amountint == -45:
                amountint = -90

            m3.unhide_all("MESH")
            m3.select_all("MESH")

            # if this is not set to True by DM and the user has it at False, nothing will be rotated
            bpy.context.scene.tool_settings.use_uv_select_sync = True

            oldcontext = m3.change_context("IMAGE_EDITOR")
            unlink_render_result()
            oldpivot = context.space_data.pivot_point

            x, y = context.area.spaces.active.cursor_location

            context.space_data.pivot_point = 'CURSOR'

            if context.area.spaces.active.image is None:
                u = 256
                v = 256
            else:
                u, v = context.area.spaces.active.image.size

            context.area.spaces.active.cursor_location = u / 2, v / 2

            bpy.ops.transform.rotate(value=math.radians(amountint))

            context.space_data.pivot_point = oldpivot
            context.area.spaces.active.cursor_location = x, y
            bpy.ops.uv.select_all(action='DESELECT')
            m3.change_context(oldcontext)
    elif context.area.type == "IMAGE_EDITOR":
        if amountint == 45:
            amountint = 90
        elif amountint == -45:
            amountint = -90

        unlink_render_result()
        if mode == "OBJECT":
            m3.set_mode("EDIT")
        m3.unhide_all("MESH")
        m3.select_all("MESH")

        # if this is not set to True by DM and the user has it at False, nothing will be rotated
        bpy.context.scene.tool_settings.use_uv_select_sync = True

        oldpivot = context.space_data.pivot_point
        x, y = context.area.spaces.active.cursor_location

        context.space_data.pivot_point = 'CURSOR'

        if context.area.spaces.active.image is None:
            u = 256
            v = 256
        else:
            u, v = context.area.spaces.active.image.size

        context.area.spaces.active.cursor_location = u / 2, v / 2

        bpy.ops.transform.rotate(value=math.radians(amountint))

        context.space_data.pivot_point = oldpivot
        context.area.spaces.active.cursor_location = x, y
        bpy.ops.uv.select_all(action='DESELECT')
