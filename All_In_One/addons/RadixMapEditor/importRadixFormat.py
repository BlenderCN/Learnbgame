import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from .importer import Importer


class ImportRadixFormat(bpy.types.Operator, ImportHelper):
  bl_idname = "radix.import"
  bl_label = "Import Radix XML"
  bl_description = "Import Radix XML file (.xml)"
  bl_options = {'PRESET'}
  filename_ext = ".xml"
  filter_glob = StringProperty(default="*.xml", options={'HIDDEN'})
  deleteWorld = BoolProperty(default=True, name="Erase current scene")

  def execute(self, context):
    importer = Importer(self.filepath, self.deleteWorld)
    importer.execute(context)
    bpy.context.window_manager.importedFilepath = self.filepath
    return {'FINISHED'}
