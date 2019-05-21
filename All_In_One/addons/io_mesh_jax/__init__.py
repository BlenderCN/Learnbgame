import bpy

bl_info = {
    "name": "Jax WebGL Exporter",
    "description": "Exports models which can be loaded into Jax",
    "author": "Colin MacKenzie IV",
    "version": (1,0),
    "blender": (2, 5, 7),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export Jax meshes",
    "warning": "",
    "wiki_url": "http://github.com/sinisterchipmunk/jax-blender-models/wiki",
    "tracker_url": "http://github.com/sinisterchipmunk/jax-blender-models/issues",
    "category": "Import-Export"
}

import bpy

if "bpy" in locals():
  import imp
  if "common_jax" in locals():
    imp.reload(jax)
  if "export_jax" in locals():
    imp.reload(export_jax)

from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

FILENAME_EXT = ".json"

class ExportJax(bpy.types.Operator, ExportHelper):
  '''Export selected object for Jax.'''

  bl_idname = "export.jax"
  bl_label = "Export Jax"

  filename_ext = FILENAME_EXT

  vertices          = BoolProperty(name = "Vertices",       description = "Export vertices",            default = True)
  normals           = BoolProperty(name = "Normals",        description = "Export normals",             default = True)
  colors            = BoolProperty(name = "Colors",         description = "Export vertex colors",       default = True)
  texture_coords    = BoolProperty(name = "Texture Coords", description = "Export texture coordinates", default = True)
  scale             = FloatProperty(name = "Scale", description = "Scale vertices", min = 0.01, max = 1000.0, soft_min = 0.01, soft_max = 1000.0, default = 1.0)
  flip_yz           = BoolProperty(name = "Flip YZ", description = "Flip Y/Z axes", default = True)
  # materials         = BoolProperty(name = "Materials",      description = "Export materials",           default = True)
  # export_scene      = BoolProperty(name = "Scene", description = "Export scene", default = False)
  # lights            = BoolProperty(name = "Lights", description = "Export default scene lights", default = False)
  # cameras           = BoolProperty(name = "Cameras", description = "Export default scene cameras", default = False)

  def invoke(self, context, event):
    return ExportHelper.invoke(self, context, event)

  @classmethod
  def poll(cls, context):
    return context.active_object != None

  def execute(self, context):
    print("Selected: " + context.active_object.name)
    if not self.properties.filepath:
      raise Exception("filename not set")

    # save_settings_export(self.properties)
    if context.scene.objects.active:
      bpy.ops.object.mode_set(mode='OBJECT')

    import io_mesh_jax.export_jax
    return io_mesh_jax.export_jax.export_object_to_file(self, context, self.properties)

  def draw(self, context):
    layout = self.layout
    
    row = layout.row()
    row.label(text="Geometry:")

    row = layout.row()
    row.prop(self.properties, "vertices")
    row.prop(self.properties, "normals")
    row = layout.row()
    row.prop(self.properties, "colors")
    row.prop(self.properties, "texture_coords")
    layout.separator()

    row = layout.row()
    row.label(text="Options:")

    row = layout.row()
    row.prop(self.properties, "flip_yz")
    row.prop(self.properties, "scale")

    # row = layout.row()
    # row.prop(self.properties, "export_scene")
    # row.prop(self.properties, "materials")
    # 
    # row = layout.row()
    # row.prop(self.properties, "lights")
    # row.prop(self.properties, "cameras")
    # layout.separator()


def menu_func_export(self, context):
  default_path = bpy.data.filepath.replace(".blend", FILENAME_EXT)
  self.layout.operator(ExportJax.bl_idname, text=("Jax (%s)" % FILENAME_EXT)).filepath = default_path

def menu_func_import(self, context):
  self.layout.operator(ImportJax.bl_idname, text=("Jax (%s)" % FILENAME_EXT))

def register():
  bpy.utils.register_module(__name__)
  bpy.types.INFO_MT_file_export.append(menu_func_export)
  bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
  bpy.utils.unregister_module(__name__)
  bpy.types.INFO_MT_file_export.remove(menu_func_export)
  bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
  register()
