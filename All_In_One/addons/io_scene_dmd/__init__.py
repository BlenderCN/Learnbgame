#-------------------------------------------------------------------------------
#
#       Дополнение для работы с моделями DMD для ZDSimulator
#       (c) РГУПС, ВЖД 18/07/2018
#       Разработал: Притыкин Д.Е.
#
#-------------------------------------------------------------------------------

bl_info = {
    "name": "Importer/Exporter DGLEngine DMD models",
    "category": "Learnbgame",
    "author": "Dmitry Pritykin",
    "version": (0, 2, 0),
    "blender": (2, 79, 0)
}

import bpy

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DMDImporter(bpy.types.Operator):
    """DMD models importer"""
    bl_idname = "import_scene.dmd"
    bl_label = "DGLEngine DMD model (*.dmd)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH')

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def execute(self, context):
        from .DMDimport import Importer
        dmd_loader = Importer()
        dmd_loader.load(self.filepath)

        return {'FINISHED'}

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DMDExporter(bpy.types.Operator):
    """DMD models exporter"""
    bl_idname = "export_scene.dmd"
    bl_label = "DGLEngine DMD model (*.dmd)"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".dmd"
    filter_glob = bpy.props.StringProperty(
        default = "*.dmd",
        options = {'HIDDEN'},
    )

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def execute(self, context):

        # Check object mode of editor
        if bpy.context.mode != 'OBJECT':
            print("Please switch to Object Mode.")

            def draw_context(self, context):
                self.layout.label("Please switch to Object Mode.")

            bpy.context.window_manager.popup_menu(draw_context, title="Export DMD", icon='ERROR')
            return {'FINISHED'}

        path = self.filepath
        print("Export model to file: " + path)

        from . import DMDexport
        exporter = DMDexport.Exporter()

        exporter.exportModel(path)

        return {'FINISHED'}

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def invoke(self, context, event):
        self.filepath = "undefined" + self.filename_ext
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def menu_import(self, context):
    self.layout.operator(DMDImporter.bl_idname, text=DMDImporter.bl_label)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def menu_export(self, context):
    self.layout.operator(DMDExporter.bl_idname, text=DMDExporter.bl_label)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def register():
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.utils.register_class(DMDImporter)

    bpy.types.INFO_MT_file_export.append(menu_export)
    bpy.utils.register_class(DMDExporter)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.utils.unregister_class(DMDImporter)

    bpy.types.INFO_MT_file_export.remove(menu_export)
    bpy.utils.unregister_class(DMDExporter)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    register()
