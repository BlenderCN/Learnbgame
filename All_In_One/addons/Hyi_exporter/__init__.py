


bl_info = {
    "name": "Hyi format exporter",
    "author": "ゲーニー",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export >Hui format ",
    "description": "Import to Hui",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

from bpy.props import StringProperty
import bpy

class ExportHui(bpy.types.Operator):
    """Export scene to Hui file"""
    bl_idname = "export_scene.hui"
    bl_label = "Export HUI"

    filter_glob: StringProperty(default="*.hui", options={'HIDDEN'})
    filepath: StringProperty(subtype='FILE_PATH')


    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        from .hui import Hui
        try:
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.transforms_clear()
        except:
            pass
        hui = Hui(self)
        hui.getBlenderData(bpy.data)
        hui.writeDataToFile(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(ExportHui.bl_idname, text="Export Hui (.hui)")

def register():
    bpy.utils.register_class(ExportHui)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    #unregister_class(HuiExporter)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
