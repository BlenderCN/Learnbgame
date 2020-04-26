import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty

"""List of available engine types"""
RADIX_TYPES = [
  ("none", "None", "No special property"),
  ("wall", "Wall", "Wall"),
  ("volume", "Volume", "Volume"),
  ("trigger", "Trigger", "Trigger"),
  ("model", "Model", "Model"),
  ("destination", "Destination", "Destination"),
  ("spawn", "Spawn", "Spawn")
]
"""List of available volume types"""
RADIX_VOLUME_TYPES = [
  ("none", "None", "No special property"),
  ("acid", "Acid Pool", "A pool full of acid, hurts..")
]
"""List of available trigger types"""
RADIX_TRIGGER_TYPES = [
  ("none", "None", "No special property"),
  ("win", "Win", "Area triggers win"),
  ("map", "Map", "Area triggers new map"),
  ("audio", "Audio", "Area triggers new audio"),
  ("death", "Death", "Area triggers death"),
  ("radiation", "Radiation", "Area triggers radiation"),
  ("teleport", "Teleport", "Area triggers teleport"),
  ("screen", "Screen", "Area triggers screen"),
  ("checkpoint", "Checkpoint", "Area marks checkpoint"),
  ("remove", "Remove", "Area triggers remove")
]
"""List of available materials"""
RADIX_MATERIAL_TYPES = [
  ("none", "None", "No material")
]


def onUpdateRadixTypes(self, context):
  """Update object name based on object's game function"""
  objects = context.selected_objects
  for object in objects:
    type = object.radixTypes
    name = type

    if type == "trigger":
      name = name + "." + object.radixTriggerTypes
    elif type == "volume":
      name = name + "." + object.radixVolumeTypes
    elif type == "model":
      name = name + "." + object.radixModel
    else:
      name = name + "." + object.radixMaterial

    if object.radixName:
      name = name + "." + object.radixName

    if object.radixTypes != "none":
      object.name = name


def setProperties():
  """Register properties for Blender"""
  bpy.types.Object.radixTypes = EnumProperty(
    items=RADIX_TYPES,
    name="Type",
    description="Radix type",
    default="none",
    update=onUpdateRadixTypes
  )
  bpy.types.Object.radixVolumeTypes = EnumProperty(
    items=RADIX_VOLUME_TYPES,
    name="Volume Type",
    default="none",
    update=onUpdateRadixTypes
  )
  bpy.types.Object.radixTriggerTypes = EnumProperty(
    items=RADIX_TRIGGER_TYPES,
    name="Trigger Type",
    default="none",
    update=onUpdateRadixTypes
  )
  bpy.types.Object.radixTriggerFilepath = StringProperty(
    name="Filepath",
    description="Relative path to the file for trigger",
    default=""
  )
  bpy.types.Object.radixTriggerAudioLoop = BoolProperty(
    name="Enable loop",
    description="Play audio file in loop",
    default=False
  )
  bpy.types.Object.radixTriggerDestination = StringProperty(
    name="Destination",
    description="Name of the destination",
    default=""
  )
  bpy.types.Object.radixTriggerRemoveToogle = BoolProperty(
    name="Toogle",
    description="Toogle the action",
    default=False
  )
  bpy.types.Object.radixTriggerRemoveAction = BoolProperty(
    name="Acion",
    description="Require action key",
    default=False
  )
  bpy.types.Object.radixTriggerRemoveReference = StringProperty(
    name="Reference",
    description="Name of the object to remove",
    default=""
  )
  bpy.types.Object.radixModel = StringProperty(
    name="Model",
    description="Relative path to the model",
    default="",
    update=onUpdateRadixTypes
  )
  bpy.types.WindowManager.importedFilepath = StringProperty(
    name="Imported filepath",
    default=""
  )
  bpy.types.Object.radixName = StringProperty(
    name="Name",
    description="Object name used by Radix engine as identifier",
    default="",
    update=onUpdateRadixTypes
  )


def delProperties():
  """Unregister properties from Blender"""
  del bpy.types.Object.radixTypes
  del bpy.types.Object.radixVolumeTypes
  del bpy.types.Object.radixTriggerTypes
  del bpy.types.Object.radixTriggerFilepath
  del bpy.types.Object.radixTriggerAudioLoop
  del bpy.types.Object.radixModel
  del bpy.types.WindowManager.importedFilepath
  del bpy.types.Object.radixMaterial  # Defined in managers/MaterialManager.py
  del bpy.types.Object.radixName
  del bpy.types.Object.radixTriggerDestination
