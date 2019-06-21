import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty


RADIX_TYPES = [
  ("none", "None", "No special property"),
  ("wall", "Wall", "Wall"),
  ("volume", "Volume", "Volume"),
  ("trigger", "Trigger", "Trigger"),
  ("model", "Model", "Model"),
  ("destination", "Destination", "Destination")
]
RADIX_VOLUME_TYPES = [
  ("none", "None", "No special property"),
  ("acid", "Acid Pool", "A pool full of acid, hurts..")
]
RADIX_TRIGGER_TYPES = [
  ("none", "None", "No special property"),
  ("win", "Win", "Area triggers win"),
  ("map", "Map", "Area triggers new map"),
  ("audio", "Audio", "Area triggers new audio"),
  ("death", "Death", "Area triggers death"),
  ("radiation", "Radiation", "Area triggers radiation"),
  ("teleport", "Teleport", "Area triggers teleportation")
]
RADIX_MATERIAL_TYPES = [
  ("none", "None", "No material")
]
RADIX_DESTINATION_TYPES = [
  ("none", "None", "No destination")
]

def onUpdateRadixTypes(self, context):
  """Update object name based on object's game function"""
  objects = context.selected_objects
  for object in objects:
    type = object.radixTypes
    name = type

    if type == "trigger":
      name = type + "." + object.radixTriggerTypes
    elif type == "volume":
      name = type + "." + object.radixVolumeTypes
    elif type == "model":
      name = type + "." + object.radixModel
    else:
      name = type + "." + object.radixMaterial

    if object.radixTypes != "none":
      object.name = name


def setProperties():
  """Register radix specific properties to objects"""
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
    default="none"
  )
  bpy.types.Object.radixTriggerAudioLoop = BoolProperty(
    name="Enable loop",
    description="Play audio file in loop",
    default=False
  )
  bpy.types.Object.radixModel = StringProperty(
    name="Model",
    description="Relative path to the model",
    default="none",
    update=onUpdateRadixTypes
  )
  bpy.types.Object.radixDestinationName = StringProperty(
    name="Destination Name",
    default="none"
  )
  bpy.types.WindowManager.importedFilepath = StringProperty(
    name="Imported filepath",
    default="none"
  )

def delProperties():
  """Unregister radix properties from objects"""
  del bpy.types.Object.radixTypes
  del bpy.types.Object.radixVolumeTypes
  del bpy.types.Object.radixTriggerTypes
  del bpy.types.Object.radixTriggerFilepath
  del bpy.types.Object.radixTriggerAudioLoop
  del bpy.types.Object.radixModel
  del bpy.types.WindowManager.importedFilepath
  del bpy.types.Object.radixMaterial
  del bpy.types.Object.radixDestinationName
