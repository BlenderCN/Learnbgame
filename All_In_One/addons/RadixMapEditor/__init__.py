#!BPY
bl_info = {
  "name":         "Radix Map Editor",
  "author":       "Henry Hirsch, Julian Thijssen, Juraj Oravec",
  "blender":      (2, 6, 3),
  "version":      (1, 0, 0),
  "location":     "File > Import-Export",
  "description":  "Module for loading, editing and saving Radix maps.",
  "category": "Learnbgame",
  "tracker_url":  "https://github.com/GlPortal/map-editor/issues"
}

import os

pathToThisFile = os.path.realpath(__file__)
directory = os.path.dirname(pathToThisFile)

fileHandle = open(directory + '/environment.py')
environmentBootstrapCode = fileHandle.read()
fileHandle.close()
exec(environmentBootstrapCode)

import bpy
blender = bpy
from .RadixMenu import RadixMenu

def addMenuItems():
  menu = RadixMenu()
  types = blender.types
  types.INFO_MT_file_export.append(menu.getExportMenuOperator)
  types.INFO_MT_file_import.append(menu.getImportMenuOperator)
  types.INFO_MT_add.prepend(menu.addMainMenu)

def removeMenuItems():
  menu = RadixMenu()
  types = blender.types
  types.INFO_MT_file_import.remove(menu.getImportMenuOperator)
  types.INFO_MT_file_export.remove(menu.getexportMenuOperator)
  types.INFO_MT_add.remove(menu.addMainMenu)

def register():
  blender.utils.register_module(__name__)

  types.setProperties()
  MPTypes.initProperties()
  addMenuItems()
  blender.app.handlers.scene_update_post.append(updateTextures.sceneUpdater)
  blender.types.WindowManager.MPMaterials = bpy.props.CollectionProperty(type=MPTypes.Row)
  blenderScene = blender.types.Scene
  blenderScene.countObjects = mapHelpers.countObjects
  blenderScene.fixObjects = mapHelpers.fixObjects
  blenderObject = blender.types.Object
  blenderObject.isOverObject = mapHelpers.isOverObject
  blenderObject.updateTexture = updateTextures.updateTexture
  os.path.browse = directory.browse

  MaterialManager.preload()
  ModelManager.preload()
  MapManager.preload()
  AudioManager.preload()
  MaterialPanel.initRows()

  OperatorManager.addOperators()


def unregister():
  blender.utils.unregister_module(__name__)

  OperatorManager.removeOperators()

  MaterialManager.radixMaterialReset()
  MaterialManager.MATERIALS.clear()
  ModelManager.MODELS.clear()
  types.delProperties()
  MPTypes.delProperties()

  removeMenuItems()
  blender.app.handlers.scene_update_post.remove(updateTextures.sceneUpdater)

  del blender.types.Scene.countObjects
  del blender.types.Scene.fixObjects
  del blender.types.Object.isOverObject
  del blender.types.Object.updateTexture

  del os.path.browse

  del blender.types.WindowManager.MPMaterials


if __name__ == "__main__":
  register()
