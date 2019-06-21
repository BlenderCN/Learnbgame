import bpy
from . import export


class Exporter(bpy.types.Operator):
    bl_label = 'Export to .sls'
    bl_idname = 'export.sls'

    filepath = bpy.props.StringProperty('')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        export.export(self.report, self.filepath)
        self.report({'INFO'}, 'The mesh has correctly been exported !')
        return {'FINISHED'}
