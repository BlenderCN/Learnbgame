import os

from .managers import MapManager, MaterialManager, ModelManager
from . import MaterialPanel


def updateTriggerXrays(self, context):
  prefs = context.user_preferences.addons[__package__].preferences
  triggerXrays = prefs.triggerXrays
  objects = context.scene.objects

  for object in objects:
    if object.radixTypes == "trigger":
      object.show_x_ray = triggerXrays


def updateDefaultMaterial(self, context):
  prefs = context.user_preferences.addons[__package__].preferences

  if prefs.materials != "none":
    prefs.defaultMaterial = prefs.materials


def updateDataDir(self, context):
  prefs = context.user_preferences.addons[__package__].preferences

  if os.path.isdir(os.path.expanduser(prefs.dataDir)):
    MaterialManager.reload()
    ModelManager.reload()
    MapManager.reload()
    MaterialPanel.initRows()
