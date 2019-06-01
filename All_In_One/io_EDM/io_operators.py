import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator, OperatorFileListElement
from bpy.props import ( StringProperty,
                        BoolProperty,
                        CollectionProperty,
                        EnumProperty,
                        FloatProperty,
                      )
import os

import logging
logger = logging.getLogger(__name__)

from .reader import read_file
from .writer import write_file

class ImportEDM(Operator, ImportHelper):
  bl_idname = "import_mesh.edm"
  bl_label = "Import EDM"
  filename_ext = ".edm"

  filter_glob = StringProperty(
          default="*.edm",
          options={'HIDDEN'},
          )
  files = CollectionProperty(
          name="File Path",
          type=OperatorFileListElement,
          )
  directory = StringProperty(
          subtype='DIR_PATH',
          )

  shadeless = BoolProperty(name="Shadeless",
      description="Import materials as shadeless (no lights required in blender)",
      default=False)

  def execute(self, context):
    # Get a list of files
    paths = [os.path.join(self.directory, name.name) for name in self.files]
    if not paths:
      paths.append(self.filepath)

    if len(paths) > 1:
      self.report("ERROR", "Importer cannot handle more than one input file currently")
      return "CANCELLED"
    
    # Import the file
    logger.warning("Reading EDM file {}".format(paths[0]))
    
    read_file(paths[0], options={"shadeless": self.shadeless})
    return {'FINISHED'}


class ExportEDM(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_mesh.edm"
    bl_label = "Export EDM"
    filename_ext = ".edm"

    filter_glob = StringProperty(
            default="*.edm",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    apply_modifiers = BoolProperty(name="Apply Modifiers",
      description="Should object modifiers be applied before export?",
      default=True)

    # type = EnumProperty(
    #         name="Example Enum",
    #         description="Choose between two items",
    #         items=(('OPT_A', "First Option", "Description one"),
    #                ('OPT_B', "Second Option", "Description two")),
    #         default='OPT_A',
    #         )

    def execute(self, context):
        write_file(self.filepath, options={"apply_modifiers": self.apply_modifiers})
        return {'FINISHED'}


def menu_export(self, context):
  self.layout.operator(ExportEDM.bl_idname, text="DCS World (.edm)")

def menu_import(self, context):
  self.layout.operator(ImportEDM.bl_idname, text="DCS World (.edm)")

def register():
  bpy.utils.register_class(ImportEDM)
  bpy.utils.register_class(ExportEDM)
  
  bpy.types.INFO_MT_file_import.append(menu_import)
  bpy.types.INFO_MT_file_export.append(menu_export)

def unregister():
  bpy.types.INFO_MT_file_export.remove(menu_export)
  bpy.types.INFO_MT_file_import.remove(menu_import)

  bpy.utils.unregister_class(ImportEDM)
  bpy.utils.unregister_class(ExportEDM)
