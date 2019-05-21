import bpy
from blendmotion.core.animation import export_animation, LOOP_TYPES
from blendmotion.error import error_and_log, OperatorError

class ExportAnimationOperator(bpy.types.Operator):
    bl_idname = "bm.export_animation"
    bl_label = "Export Animation"

    filepath = bpy.props.StringProperty(name='file_path', subtype='FILE_PATH')
    loop_type = bpy.props.EnumProperty(name='loop_type', items=[(t, t, t) for t in LOOP_TYPES])

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            export_animation(obj, self.filepath, self.loop_type)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(ExportAnimationOperator)

def unregister():
    bpy.utils.unregister_class(ExportAnimationOperator)
