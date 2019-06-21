if "bpy" in locals():
    import imp
    imp.reload(export_json)
else:
    from . import export_json

import bpy
import math
import mathutils
import json

from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

bl_info = {
  "name":         "JSON Model Format",
  "author":       "Nicholas Kostelnik",
  "blender":      (2,7,1),
  "version":      (0,0,1),
  "location":     "File > Import-Export",
  "description":  "Export custom JSON format",
  "category": "Learnbgame",
}

class ExportJSON(bpy.types.Operator, ExportHelper):
  bl_idname       = "export_json.fmt";
  bl_label        = "JSON Exporter";
  bl_options      = {'PRESET'};

  filename_ext    = ".json";


  def execute(self, context):
    export_json.do_export(self.filepath)
    return {'FINISHED'};

def menu_func(self, context):
  self.layout.operator(ExportJSON.bl_idname, text="JSON Format(.json)");

def register():
  bpy.utils.register_module(__name__);
  bpy.types.INFO_MT_file_export.append(menu_func);

def unregister():
  bpy.utils.unregister_module(__name__)
  bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
  register()
