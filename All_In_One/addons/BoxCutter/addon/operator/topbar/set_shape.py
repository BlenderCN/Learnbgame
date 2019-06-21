import bpy

from bpy.types import Operator


class BC_OT_box(Operator):
    bl_idname = 'bc.box'
    bl_label = 'Box'
    bl_description = 'Set the shape to box'


    def execute(self, context):
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                tool.operator_properties('bc.draw_shape').shape_type = 'BOX'

                context.workspace.tools.update()
                break

        return {'FINISHED'}


class BC_OT_circle(Operator):
    bl_idname = 'bc.circle'
    bl_label = 'Circle'
    bl_description = 'Set the shape to circle'


    def execute(self, context):
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                tool.operator_properties('bc.draw_shape').shape_type = 'CIRCLE'

                context.workspace.tools.update()
                break

        return {'FINISHED'}


class BC_OT_ngon(Operator):
    bl_idname = 'bc.ngon'
    bl_label = 'Ngon'
    bl_description = 'Set the shape to ngon'


    def execute(self, context):
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                tool.operator_properties('bc.draw_shape').shape_type = 'NGON'

                context.workspace.tools.update()
                break

        return {'FINISHED'}


class BC_OT_custom(Operator):
    bl_idname = 'bc.custom'
    bl_label = 'Custom'
    bl_description = 'Set the shape to custom'


    def execute(self, context):
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                tool.operator_properties('bc.draw_shape').shape_type = 'CUSTOM'

                context.workspace.tools.update()
                break

        return {'FINISHED'}
