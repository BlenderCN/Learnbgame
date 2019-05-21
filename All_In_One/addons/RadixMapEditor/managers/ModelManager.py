import bpy
import os

MODELS = {}
BLACKLIST = [
  "GUIElement.obj",
  "Plane.obj",
  "Portal.obj",
  "PortalStencil.obj"
]

def reload():
  MODELS.clear()
  preload()

def preload():
  global MODELS
  meshes = os.path.browse(directory="meshes", extension="obj", blacklist=BLACKLIST)

  if meshes:
    MODELS = meshes
    return True

  return False

def create(file="", materialName=""):
  if not file:
    print("Model file is empty.")
    return False

  if file in MODELS:
    prefs = bpy.context.user_preferences.addons[__package__.rpartition(".")[0]].preferences
    dataDir = os.path.expanduser(prefs.dataDir)
    path = os.path.join(dataDir, "meshes", file)

    if os.path.isfile(path):
      bpy.ops.import_scene.obj(filepath=path)

      object = bpy.context.selected_objects[0]
      if object:
        object.location = bpy.context.scene.cursor_location
        object.radixTypes = "model"
        object.radixModel = file

        bpy.context.scene.objects.active = object
        bpy.ops.object.transform_apply(rotation=True)

        if materialName:
          object.radixMaterial = materialName
        else:
          object.radixMaterial = prefs.defaultMaterial
      return True
    return False

  print("Model '", file, "' does not exist.")
  return False
