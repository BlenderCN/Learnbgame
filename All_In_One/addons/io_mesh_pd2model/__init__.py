"""
Import/export Payday 2 Model File format files to Blender.

"""


bl_info = {    
    "name": "Payday Unit Import/\"Export\"",
    "author": "I am not a spy..., Zwagoth, PoueT",
    "version": (0, 1),
    "blender": (2, 68, 0),
    "location": "File > Import-Export > Payday model (.model) ",
    "description": "Import-Export Payday MODEL, Import Payday MODEL mesh, UV's, "
                   "materials",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    if "import_pd2model" in locals():
        imp.reload(import_pd2model)
    if "export_pd2model" in locals():
        imp.reload(export_pd2model)
else:
    import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper


class PD2ModelImporter(bpy.types.Operator):
    """Load PD2Model data"""
    bl_idname = "import_mesh.model"
    bl_label = "Import Payday MODEL"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.model;*.object;*.scene", options={'HIDDEN'})

    def execute(self, context):
        from . import import_pd2model
        pd2ModelImport = import_pd2model.Pd2ModelImport()
        pd2ModelImport.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
 
 
class PD2ModelExporter(bpy.types.Operator, ExportHelper):
    """Save PD2Model data"""
    bl_idname = "export_mesh.model"
    bl_label = "Export Payday MODEL"

    #filename_ext = ".model*.object;*.scene"
    filter_glob = StringProperty(default="*.model*.object;*.scene", options={'HIDDEN'})

    apply_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Use transformed mesh data from each object",
            default=True,
            )
    triangulate = BoolProperty(
            name="Triangulate",
            description="Triangulate quads",
            default=True,
            )

    def execute(self, context):
        from . import export_model
        export_model.write()

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(PD2ModelImporter.bl_idname, text="Payday model (.model)")


def menu_export(self, context):
    self.layout.operator(PD2ModelExporter.bl_idname, text="Payday model (.model)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
