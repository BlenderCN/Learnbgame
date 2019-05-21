import bpy

from .managers import AudioManager, MapManager, MaterialManager, ModelManager, ScreenManager
from . import types


def resetTriggerSettings(object):
  if object.radixTypes == "trigger":
    object.radixTriggerTypes = "none"
    object.draw_type = 'TEXTURED'
    object.show_x_ray = False
    object.show_bounds = False
    object.draw_bounds_type = 'BOX'

    if object.radixTriggerFilepath:
      object.radixTriggerFilepath = ""
    if object.radixTriggerAudioLoop:
      object.radixTriggerAudioLoop = False


# TODO Adapt to new features
def setTrigger(object, type, filePath="", loop=False, removeToogle=False, removeAction=False):
  prefs = bpy.context.user_preferences.addons[__package__].preferences
  clearRadixProperties(object)

  object.radixTypes = "trigger"
  object.radixTriggerTypes = type
  object.draw_type = 'WIRE'
  object.show_x_ray = prefs.triggerXrays
  object.show_bounds = True
  object.draw_bounds_type = 'CAPSULE'

  if loop:
    object.radixTriggerAudioLoop = loop

  if filePath and type in {"teleport", "checkpoint"}:
    object.radixTriggerDestination = filePath
  elif filePath and type == "remove":
    object.radixTriggerRemoveReference = filePath
    object.radixTriggerRemoveToogle = removeToogle
    object.radixTriggerRemoveAction = removeAction
  elif filePath:
    object.radixTriggerFilepath = filePath


def clearRadixProperties(object):
  MaterialManager.reset(object)

  if object.radixTypes != "none":
    object.radixTypes = "none"
  if object.radixVolumeTypes != "none":
    object.radixVolumeTypes = "none"
  if object.radixTriggerTypes != "none":
    object.radixTriggerTypes = "none"
  if object.radixTriggerFilepath:
    object.radixTriggerFilepath = ""
  if object.radixTriggerAudioLoop:
    object.radixTriggerAudioLoop = False


def itemsMaterial(self, context):
  return [(name, fancyName, tooltip) for name, fancyName, tooltip in types.RADIX_MATERIAL_TYPES]


def itemsModel(self, context):
  return [(file, fancyName, fancyName) for file, fancyName in ModelManager.MODELS.items()]


def itemsMap(self, context):
  return [(key, name, name) for key, name in MapManager.MAPS.items()]


def itemsAudio(self, context):
  return [(key, name, name) for key, name in AudioManager.AUDIO.items()]


def itemsScreen(self, context):
  return [(key, name, name) for key, name in ScreenManager.SCREEN.items()]


def itemsDestination(self, context):
  return [(object.radixName, object.radixName, object.radixName) for object in context.scene.objects if object.radixName and object.radixTypes == "destination"]


def itemsWithName(self, context):
  return [(object.radixName, object.radixName, object.radixName) for object in context.scene.objects if object.radixName]


def simpleCube():
  if ModelManager.create("Cube.obj"):
    object = bpy.context.selected_objects[0]
    object.radixTypes = "none"
    object.dimensions = [2.0, 2.0, 2.0]
    bpy.ops.object.transform_apply(scale=True)
    return True
  return False
