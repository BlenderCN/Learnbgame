from bpy.props import StringProperty, BoolProperty, EnumProperty

from .operatorHelpers import itemsMaterial, itemsModel, itemsAudio, itemsMap, itemsDestination, \
  itemsScreen, itemsWithName
from .managers import ModelManager, MaterialManager


"""List of dynamically created operators"""
operatorList = [
  # Triggers
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetAudio",
    "properties": {
      "bl_idname": "trigger_set_audio",
      "bl_label": "Set Audio Trigger",
      "bl_description": "Mark the selection as audio trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="audio", options={'HIDDEN'}),
      "loop": BoolProperty(default=False, options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetMap",
    "properties": {
      "bl_idname": "trigger_set_map",
      "bl_label": "Set Map Trigger",
      "bl_description": "Mark the selection as map trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="map", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetTeleport",
    "properties": {
      "bl_idname": "trigger_set_teleport",
      "bl_label": "Set Teleport Trigger",
      "bl_description": "Mark the selection as teleport trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="teleport", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetCheckpoint",
    "properties": {
      "bl_idname": "trigger_set_checkpoint",
      "bl_label": "Set Checkpoint Trigger",
      "bl_description": "Mark the selection as checkpoint trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="checkpoint", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetScreen",
    "properties": {
      "bl_idname": "trigger_set_screen",
      "bl_label": "Set Screen Trigger",
      "bl_description": "Mark the selection as screen trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="screen", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetRemove",
    "properties": {
      "bl_idname": "trigger_set_remove",
      "bl_label": "Set Remove Trigger",
      "bl_description": "Mark the selection as remove trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="remove", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'}),
      "removeAction": BoolProperty(default=False, options={'HIDDEN'}),
      "removeToogle": BoolProperty(default=False, options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetWin",
    "properties": {
      "bl_idname": "trigger_set_win",
      "bl_label": "Set Win Trigger",
      "bl_description": "Mark the selection as win trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="win", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetDeath",
    "properties": {
      "bl_idname": "trigger_set_death",
      "bl_label": "Set Death Trigger",
      "bl_description": "Mark the selection as death trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="death", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "TriggerSetBase",
    "className": "TriggerSetRadiation",
    "properties": {
      "bl_idname": "trigger_set_radiation",
      "bl_label": "Set Radiation Trigger",
      "bl_description": "Mark the selection as radiation trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "type": StringProperty(default="radiation", options={'HIDDEN'}),
      "filePath": StringProperty(default="", options={'HIDDEN'})
    }
  },
  {
    "base": "SearchBase",
    "className": "TriggerSearchAudio",
    "properties": {
      "bl_idname": "trigger_search_audio",
      "bl_label": "Search Audio Trigger",
      "bl_description": "Set audio trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsAudio, options={'HIDDEN'}),
      "action": "trigger_set_audio",
      "kwargs": {
        "items": "filePath"
      }
    }
  },
  {
    "base": "SearchBase",
    "className": "TriggerSearchMap",
    "properties": {
      "bl_idname": "trigger_search_map",
      "bl_label": "Search Map Trigger",
      "bl_description": "Set map trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsMap, options={'HIDDEN'}),
      "action": "trigger_set_map",
      "kwargs": {
        "items": "filePath"
      }
    }
  },
  {
    "base": "SearchBase",
    "className": "TriggerSearchTeleport",
    "properties": {
      "bl_idname": "trigger_search_teleport",
      "bl_label": "Search Teleport Trigger",
      "bl_description": "Set teleport trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsDestination, options={'HIDDEN'}),
      "action": "trigger_set_teleport",
      "kwargs": {
        "items": "filePath"
      }
    }
  },
  {
    "base": "SearchBase",
    "className": "TriggerSearchCheckpoint",
    "properties": {
      "bl_idname": "trigger_search_checkpoint",
      "bl_label": "Search Checkpoint Trigger",
      "bl_description": "Set checkpoint trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsDestination, options={'HIDDEN'}),
      "action": "trigger_set_checkpoint",
      "kwargs": {
        "items": "filePath"
      }
    }
  },
  {
    "base": "SearchBase",
    "className": "TriggerSearchScreen",
    "properties": {
      "bl_idname": "trigger_search_screen",
      "bl_label": "Search Screen Trigger",
      "bl_description": "Set screen trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsScreen, options={'HIDDEN'}),
      "action": "trigger_set_screen",
      "kwargs": {
        "items": "filePath"
      }
    }
  },
  {
    "base": "SearchBase",
    "className": "TriggerSearchRemove",
    "properties": {
      "bl_idname": "trigger_search_remove",
      "bl_label": "Search Remove Trigger",
      "bl_description": "Set remove trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsWithName, options={'HIDDEN'}),
      "action": "trigger_set_remove",
      "kwargs": {
        "items": "filePath"
      }
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddAudio",
    "properties": {
      "bl_idname": "trigger_add_audio",
      "bl_label": "Add Audio Trigger",
      "bl_description": "Add audio trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_search_audio",
      "kwargs": ['INVOKE_DEFAULT']
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddMap",
    "properties": {
      "bl_idname": "trigger_add_map",
      "bl_label": "Add Map Trigger",
      "bl_description": "Add map trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_search_map",
      "kwargs": ['INVOKE_DEFAULT']
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddTeleport",
    "properties": {
      "bl_idname": "trigger_add_teleport",
      "bl_label": "Add Teleport Trigger",
      "bl_description": "Add teleport trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_search_teleport",
      "kwargs": ['INVOKE_DEFAULT']
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddCheckpoint",
    "properties": {
      "bl_idname": "trigger_add_checkpoint",
      "bl_label": "Add Checkpoint Trigger",
      "bl_description": "Add checkpoint trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_search_checkpoint",
      "kwargs": ['INVOKE_DEFAULT']
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddScreen",
    "properties": {
      "bl_idname": "trigger_add_screen",
      "bl_label": "Add Screen Trigger",
      "bl_description": "Add screen trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_search_screen",
      "kwargs": ['INVOKE_DEFAULT']
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddRemove",
    "properties": {
      "bl_idname": "trigger_add_remove",
      "bl_label": "Add Remove Trigger",
      "bl_description": "Add remove trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_search_remove",
      "kwargs": ['INVOKE_DEFAULT']
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddWin",
    "properties": {
      "bl_idname": "trigger_add_win",
      "bl_label": "Add Win Trigger",
      "bl_description": "Add win trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_set_win",
      "kwargs": {}
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddDeath",
    "properties": {
      "bl_idname": "trigger_add_death",
      "bl_label": "Add Death Trigger",
      "bl_description": "Add death trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_set_death",
      "kwargs": {}
    }
  },
  {
    "base": "AddBase",
    "className": "TriggerAddRadiation",
    "properties": {
      "bl_idname": "trigger_add_radiation",
      "bl_label": "Add Radiation Trigger",
      "bl_description": "Add radiation trigger.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "trigger_set_radiation",
      "kwargs": {}
    }
  },
  # Walls
  {
    "base": "WallSetBase",
    "className": "WallSetMetal",
    "properties": {
      "bl_idname": "wall_set_metal",
      "bl_label": "Set Metal Wall",
      "bl_description": "Mark the selection as metal wall.",
      "bl_options": {'REGISTER', 'UNDO'},
      "material": StringProperty(default="metal/tiles00x3", options={'HIDDEN'})
    }
  },
  {
    "base": "WallSetBase",
    "className": "WallSetPortalable",
    "properties": {
      "bl_idname": "wall_set_portalable",
      "bl_label": "Set Portalable Wall",
      "bl_description": "Mark the selection as portalable wall.",
      "bl_options": {'REGISTER', 'UNDO'},
      "material": StringProperty(default="concrete/wall00", options={'HIDDEN'})
    }
  },
  {
    "base": "AddBase",
    "className": "WallAddMetal",
    "properties": {
      "bl_idname": "wall_add_metal",
      "bl_label": "Add Metal Wall",
      "bl_description": "Add metal wall.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "wall_set_metal",
      "kwargs": {}
    }
  },
  {
    "base": "AddBase",
    "className": "WallAddPortalable",
    "properties": {
      "bl_idname": "wall_add_portalable",
      "bl_label": "Add Portalable Wall",
      "bl_description": "Add portalable wall.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "wall_set_portalable",
      "kwargs": {}
    }
  },
  # Volumes
  {
    "base": "VolumeSetBase",
    "className": "VolumeSetAcid",
    "properties": {
      "bl_idname": "volume_set_acid",
      "bl_label": "Set Volume of Acid",
      "bl_description": "Mark the selection as volume of acid.",
      "bl_options": {'REGISTER', 'UNDO'},
      "material": StringProperty(default="fluid/acid00", options={'HIDDEN'}),
      "volumeType": "acid"
    }
  },
  {
    "base": "AddBase",
    "className": "VolumeAddAcid",
    "properties": {
      "bl_idname": "volume_add_acid",
      "bl_label": "Add Volume of Acid",
      "bl_description": "Add volume of acid.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "volume_set_acid",
      "kwargs": {}
    }
  },
  # Cameras
  {
    "base": "CameraSetBase",
    "className": "CameraSetDestination",
    "properties": {
      "bl_idname": "camera_set_destination",
      "bl_label": "Set Destination",
      "bl_description": "Mark selected cameras as destination.",
      "bl_options": {'REGISTER', 'UNDO'},
      "radixType": "destination"
    }
  },
  {
    "base": "CameraSetBase",
    "className": "CameraSetSpawn",
    "properties": {
      "bl_idname": "camera_set_spawn",
      "bl_label": "Set Spawn",
      "bl_description": "Mark selected cameras as spawn.",
      "bl_options": {'REGISTER', 'UNDO'},
      "radixType": "spawn"
    }
  },
  {
    "base": "CameraAddBase",
    "className": "CameraAddDestination",
    "properties": {
      "bl_idname": "camera_add_destination",
      "bl_label": "Add Destination",
      "bl_description": "Add destination.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "camera_set_destination",
      "kwargs": {}
    }
  },
  {
    "base": "CameraAddBase",
    "className": "CameraAddSpawn",
    "properties": {
      "bl_idname": "camera_add_spawn",
      "bl_label": "Add Spawn",
      "bl_description": "Add spawn.",
      "bl_options": {'REGISTER', 'UNDO'},
      "action": "camera_set_spawn",
      "kwargs": {}
    }
  },
  # Managers
  {
    "base": "SearchBase",
    "className": "ManagerSearchAddModel",
    "properties": {
      "bl_idname": "manager_search_add_model",
      "bl_label": "Add Model",
      "bl_description": "Add model from list.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsModel, options={'HIDDEN'}),
      "action": ModelManager.create,
      "kwargs": {
        "items": "file"
      }
    }
  },
  {
    "base": "SearchBase",
    "className": "ManagerSearchSetMaterial",
    "properties": {
      "bl_idname": "manager_search_set_material",
      "bl_label": "Set material",
      "bl_description": "Search and set material to selected objects.",
      "bl_options": {'REGISTER', 'UNDO'},
      "bl_property": "items",
      "items": EnumProperty(items=itemsMaterial, options={'HIDDEN'}),
      "action": MaterialManager.setRadixMaterial,
      "kwargs": {
        "items": "material"
      }
    }
  }
]
