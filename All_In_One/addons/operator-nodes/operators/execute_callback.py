import bpy
from bpy.props import *
from .. callback import execute_callback

class ExecuteCallbackOperator(bpy.types.Operator):
    bl_idname = "en.execute_callback"
    bl_label = "Execute Callback"

    callback: StringProperty()

    def execute(self, context):
        execute_callback(self.callback)
        return {"FINISHED"}