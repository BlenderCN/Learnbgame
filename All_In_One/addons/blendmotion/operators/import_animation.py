import bpy
from blendmotion.core.animation import import_animation
from blendmotion.error import error_and_log, OperatorError

class ImportAnimationOperator(bpy.types.Operator):
    bl_idname = "bm.import_animation"
    bl_label = "Import Animation"

    filepath = bpy.props.StringProperty(name='file_path', subtype='FILE_PATH')

    def execute(self, context):
        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            import_animation(obj, self.filepath)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(ImportAnimationOperator)

def unregister():
    bpy.utils.unregister_class(ImportAnimationOperator)
