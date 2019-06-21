import bpy
from bpy.props import StringProperty, BoolProperty
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper


class CallDecalOperator(bpy.types.Operator):
    bl_idname = "machin3.call_decal_operator"
    bl_label = "MACHIN3: Call DECALmachine Operator"
    bl_options = {'REGISTER', 'UNDO'}

    idname: StringProperty()
    isinvoke: BoolProperty()

    def invoke(self, context, event):
        current_tool = ToolSelectPanelHelper._tool_get_active(context, 'VIEW_3D', None)[0][0]

        if current_tool == 'BoxCutter':
            return {'PASS_THROUGH'}

        else:
            op = getattr(bpy.ops.machin3, self.idname, None)

            if op:
                if self.isinvoke:
                    op('INVOKE_DEFAULT')

                else:
                    op()

        return {'FINISHED'}
