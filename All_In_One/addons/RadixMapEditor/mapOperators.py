import bpy
import os
from subprocess import call

from .Exporter import Exporter
from .managers import MaterialManager


class FixMaterials(bpy.types.Operator):
  bl_idname = "radix.fix_materials"
  bl_label = "Fix materials"
  bl_description = "Assign default material to objects without it."
  bl_options = {'UNDO'}

  def execute(self, context):
    prefs = bpy.context.user_preferences.addons[__package__].preferences
    material = prefs.defaultMaterial
    objects = context.scene.objects

    for object in objects:
      if object.type == 'MESH' and object.radixTypes in {"model", "wall"}:
        if not object.radixMaterial or object.radixMaterial == "none":
          object.radixMaterial = material

    return {'FINISHED'}


class ReloadMaterials(bpy.types.Operator):
  bl_idname = "radix.reload_materials"
  bl_label = "Reload materials"
  bl_description = "Reload Radix materials"

  def execute(self, context):
    MaterialManager.reload()
    return {'FINISHED'}


class FastExport(bpy.types.Operator):
  bl_idname = "radix.fast_export"
  bl_label = "Fast Export"
  bl_description = "Export current map to the imported file"

  def execute(self, context):
    filepath = bpy.context.window_manager.importedFilepath

    if filepath != "none":
      if os.path.isfile(filepath):
        exporter = Exporter(filepath)
        exporter.execute(context)

        self.report({'INFO'}, "Map exported")
      else:
        self.report({'ERROR'}, "Filepath does not exist")
    else:
      self.report({'ERROR'}, "Filepath is empty")

    return {'FINISHED'}


class FixMap(bpy.types.Operator):
  bl_idname = "radix.fix_map"
  bl_label = "Fix map"
  bl_description = "Fix the map before exporting."
  bl_options = {'UNDO'}

  def execute(self, context):
    bpy.context.scene.fixObjects()
    bpy.ops.radix.fix_materials()
    return {'FINISHED'}


class CheckMap(bpy.types.Operator):
  bl_idname = "radix.check_map"
  bl_label = "Check map"
  bl_description = "Check the map for problems."

  def execute(self, context):
    bpy.ops.object.map_check_dialog('INVOKE_DEFAULT')
    return {'FINISHED'}


class RunGame(bpy.types.Operator):
  bl_idname = "radix.run_game"
  bl_label = "Run game"
  bl_description = "Run game with this map"

  def execute(self, context):
    result = context.scene.countObjects()

    if (
      result["camera"] == 0 or
      result["light"] == 0 or
      result["wall"] == 0
    ):
      bpy.ops.object.map_check_dialog('INVOKE_DEFAULT')
    else:
      prefs = bpy.context.user_preferences.addons[__package__].preferences
      filepath = os.path.join(bpy.app.tempdir, "radix_testmap.xml")

      if os.path.isdir(prefs.dataDir):
        if os.path.isfile(prefs.gameExe):
          exporter = Exporter(filepath)
          exporter.execute(context)

          call(
            [prefs.gameExe, "--datadir", prefs.dataDir, "--mapfrompath", filepath],
            env=os.environ
          )
          print(prefs.gameExe, "--datadir", prefs.dataDir, "--mapfrompath", filepath)

          os.remove(filepath)
        else:
          self.report({'ERROR'}, "Game executable does not exist.")
      else:
        self.report({'ERROR'}, "Radix data directory does not exist.")
    return {'FINISHED'}
