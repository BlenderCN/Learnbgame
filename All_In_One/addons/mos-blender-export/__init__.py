import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
import os
from .mos import level, entities
from bpy.utils import register_class
from bpy.utils import unregister_class

bl_info = {
    "name":         "Mos export",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 80, 0),
    "version":      (0, 1, 0),
    "location":     "File > Import-Export",
    "description":  "Export Mos formats",
    "category": "Learnbgame",
}


class ExportLevelFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.level"
    bl_label = "Export MOS level"
    bl_options = {'PRESET'}
    filename_ext = ".level"

    def execute(self, context):
        level.write(self.report, os.path.dirname(self.filepath), self.filepath, context.scene)
        return {'FINISHED'}


class ExportEntitiesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_entities.entity"
    bl_label = "Export MOS entities/assets"
    bl_options = {'PRESET'}
    filename_ext = "."
    use_filter_folder = False
    use_filter = True
    filter_glob = StringProperty(
        default="",
        options={'HIDDEN'},
    )

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects]
        directory = os.path.dirname(self.filepath)
        entities.write(self.report, directory, blender_objects)

        return {'FINISHED'}


def export_level_menu_func(self, context):
    self.layout.operator(ExportLevelFormat.bl_idname, text=ExportLevelFormat.bl_label[7:] + " (%s)" % ExportLevelFormat.filename_ext)


def export_entities_menu_func(self, context):
    self.layout.operator(ExportEntitiesFormat.bl_idname, text=ExportEntitiesFormat.bl_label[7:] + " (%s)" % ExportEntitiesFormat.filename_ext)


classes = (ExportLevelFormat, ExportEntitiesFormat)


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(export_level_menu_func)
    bpy.types.TOPBAR_MT_file_export.append(export_entities_menu_func)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(export_level_menu_func)
    bpy.types.TOPBAR_MT_file_export.remove(export_entities_menu_func)

    for cls in classes:
        unregister_class(cls)


if __name__ == "__main__":
    register()

