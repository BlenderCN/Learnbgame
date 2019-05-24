#!BPY
bl_info = {
  "name":         "Radix Map Editor",
  "author":       "Henry Hirsch, Julian Thijssen, Juraj Oravec",
  "blender":      (2, 6, 3),
  "version":      (1, 0, 0),
  "location":     "File > Import-Export",
  "description":  "Module for loading, editing and saving Radix maps.",
  "category": "Learnbgame",
  "tracker_url":  "https://github.com/SGOrava/radix-map-editor/issues"
}

if "bpy" not in locals():
  from . import types
  from . import MenuFileImportExport
  from . import operatorsList
  from . import operators
  from . import mapOperators
  from . import preferences
  from . import mapHelpers
  from . import radixMenuAdd
  from . import updateTextures
  from . import lightsOperators
  from . import Exporter
  from . import importer
  from . import operatorHelpers
  from . import preferencesHelper
  from . import MPTypes
  from . import MaterialPanel
  from .utils import directory
  from .managers import MaterialManager
  from .managers import ModelManager
  from .managers import MapManager
  from .managers import AudioManager
  from .managers import ScreenManager
  from . import CreationPanel
  from . import SidePanel
  from . import ObjectPanel
else:
  import importlib

  importlib.reload(types)
  importlib.reload(MenuFileImportExport)
  importlib.reload(operatorsList)
  importlib.reload(operators)
  importlib.reload(mapOperators)
  importlib.reload(preferences)
  importlib.reload(mapHelpers)
  importlib.reload(radixMenuAdd)
  importlib.reload(updateTextures)
  importlib.reload(lightsOperators)
  importlib.reload(Exporter)
  importlib.reload(importer)
  importlib.reload(operatorHelpers)
  importlib.reload(preferencesHelper)
  importlib.reload(directory)
  importlib.reload(MaterialManager)
  importlib.reload(ModelManager)
  importlib.reload(MPTypes)
  importlib.reload(MaterialPanel)
  importlib.reload(MapManager)
  importlib.reload(AudioManager)
  importlib.reload(ScreenManager)
  importlib.reload(CreationPanel)
  importlib.reload(SidePanel)
  importlib.reload(ObjectPanel)

import bpy
import os


def menu_func_export(self, context):
  self.layout.operator("radix.export", text="Radix Map (.xml)")


def menu_func_import(self, context):
  self.layout.operator("radix.import", text="Radix Map (.xml)")


def register():
  bpy.utils.register_module(__name__)

  types.setProperties()
  MPTypes.initProperties()

  bpy.types.INFO_MT_file_export.append(menu_func_export)
  bpy.types.INFO_MT_file_import.append(menu_func_import)
  bpy.types.INFO_MT_add.prepend(radixMenuAdd.radix_add_menu)
  bpy.app.handlers.scene_update_post.append(updateTextures.sceneUpdater)
  bpy.types.WindowManager.MPMaterials = bpy.props.CollectionProperty(type=MPTypes.Row)

  bpy.types.Scene.countObjects = mapHelpers.countObjects
  bpy.types.Scene.fixObjects = mapHelpers.fixObjects
  bpy.types.Object.isOverObject = mapHelpers.isOverObject
  bpy.types.Object.updateTexture = updateTextures.updateTexture

  os.path.browse = directory.browse

  MaterialManager.preload()
  ModelManager.preload()
  MapManager.preload()
  AudioManager.preload()
  ScreenManager.preload()
  MaterialPanel.initRows()

  operators.addOperators()


def unregister():
  bpy.utils.unregister_module(__name__)

  operators.removeOperators()

  MaterialManager.radixMaterialReset()
  MaterialManager.MATERIALS.clear()
  ModelManager.MODELS.clear()
  types.delProperties()
  MPTypes.delProperties()
  MapManager.MAPS.clear()
  AudioManager.AUDIO.clear()
  ScreenManager.SCREEN.clear()

  bpy.types.INFO_MT_file_export.remove(menu_func_import)
  bpy.types.INFO_MT_file_export.remove(menu_func_export)
  bpy.types.INFO_MT_add.remove(radixMenuAdd.radix_add_menu)
  bpy.app.handlers.scene_update_post.remove(updateTextures.sceneUpdater)

  del bpy.types.Scene.countObjects
  del bpy.types.Scene.fixObjects
  del bpy.types.Object.isOverObject
  del bpy.types.Object.updateTexture

  del os.path.browse

  del bpy.types.WindowManager.MPMaterials


if __name__ == "__main__":
  register()
