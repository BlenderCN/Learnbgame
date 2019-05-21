import bpy

from .managers import AudioManager, MapManager, MaterialManager, ModelManager
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


def setTrigger(object, type, filePath="", loop=False):
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

  if filePath:
    object.radixTriggerFilepath = filePath

def setDestination(object, name):
  prefs = bpy.context.user_preferences.addons[__package__].preferences
  clearRadixProperties(object)

  object.radixTypes = "destination"
  object.radixDestinationName = name
  object.draw_type = 'WIRE'
  object.show_x_ray = prefs.triggerXrays
  object.show_bounds = True
  object.draw_bounds_type = 'CAPSULE'

def clearRadixProperties(object):
  MaterialManager.reset(object)

  if object.radixTypes != "none":
    object.radixTypes = "none"
  if object.radixVolumeTypes != "none":
    object.radixVolumeTypes = "none"
  if object.radixTriggerTypes != "none":
    object.radixTriggerTypes = "none"
  if object.radixTriggerFilepath != "none":
    object.radixTriggerFilepath = "none"
  if object.radixTriggerAudioLoop:
    object.radixTriggerAudioLoop = False
  if object.radixDestinationName != "none":
    object.radixDestinationName = "none"


def itemsMaterial(self, context):
  return [(name, fancyName, tooltip) for name, fancyName, tooltip in types.RADIX_MATERIAL_TYPES]

def itemsDestination(self, context):
  return [(name, fancyName, tooltip) for name, fancyName, tooltip in types.RADIX_DESTINATION_TYPES]

def itemsModel(self, centext):
  return [(file, fancyName, fancyName) for file, fancyName in ModelManager.MODELS.items()]


def itemsMap(self, centext):
  return [(key, name, name) for key, name in MapManager.MAPS.items()]


def itemsAudio(self, centext):
  return [(key, name, name) for key, name in AudioManager.AUDIO.items()]


def simpleCube():
  if ModelManager.create("Cube.obj"):
    object = bpy.context.selected_objects[0]
    object.radixTypes = "none"
    object.dimensions = [2.0, 2.0, 2.0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return True
  return False
