"""
rna

Contains extensions to the blender data model
"""

import bpy

_edm_matTypes = (
  ("def_material", "Default", "Default"),
  ("glass_material","Glass", "Glass"), 
  ("self_illum_material","Self-illuminated", "Self-illuminated"), 
  ("transparent_self_illum_material","Transparent Self-illuminated", "Transparent Self-illuminated"), 
  ("additive_self_illum_material", "additive_self_illum_material", "additive_self_illum_material"),
  ("bano_material", "bano_material", "bano_material"),
  ("building_material", "building_material", "building_material"),
  ("chrome_material", "chrome_material", "chrome_material"),
  ("color_material", "color_material", "color_material"),
  ("fake_omni_lights", "fake_omni_lights", "fake_omni_lights"),
  ("fake_spot_lights", "fake_spot_lights", "fake_spot_lights"),
  ("forest_material", "forest_material", "forest_material"),
  ("lines_material", "lines_material", "lines_material"),
  ("mirror_material", "mirror_material", "mirror_material"),
  ("fake_als_lights", "fake_als_lights", "fake_als_lights")
)

_edm_blendTypes = (
  ("0", "None", "None"),
  ("1", "Blend", "Blend"),
  ("2", "Alpha Test", "Alpha Test"),
  ("3", "Sum. Blending", "Sum. Blending"),
  # (4. "Z Written Blending", "Z Written Blending"),
)


def _updateIsRenderable(self, context):
  if self.is_renderable and self.is_collision_shell:
    self.is_collision_shell = False

def _updateIsCollision(self, context):
  if self.is_renderable and self.is_collision_shell:
    self.is_renderable = False

def _updateIsConnector(self, context):
  if self.is_connector and self.is_lod_root:
    self.is_lod_root = False

def _updateIsLOD(self, context):
  if self.is_connector and self.is_lod_root:
    self.is_connector = False

class EDMObjectSettings(bpy.types.PropertyGroup):
  # Only for empty objects: Is this a connector
  is_connector = bpy.props.BoolProperty(
      default=False, 
      name="Is Connector?", 
      description="Is this empty a connector object?",
      update=_updateIsConnector)
  is_lod_root = bpy.props.BoolProperty(
      default=False, 
      name="Is LOD Root?", 
      description="Does this object control child LOD visibility?",
      update=_updateIsLOD)
  is_renderable = bpy.props.BoolProperty(
      default=True, 
      name="Renderable", 
      description="Can this object's mesh be rendered",
      update=_updateIsRenderable)
  is_collision_shell = bpy.props.BoolProperty(
      default=False, 
      name="Collision Shell", 
      description="Is this mesh used for collision calculations?",
      update=_updateIsCollision)
  damage_argument = bpy.props.IntProperty(
      default=-1, 
      name="Damage Argument", 
      description="The damage argument affecting this object")
  # LOD Control
  lod_min_distance = bpy.props.FloatProperty(
    default=0, min=0, soft_max=10000, step=10, unit="LENGTH",
    name="LOD Min Distance",
    description="The minimum distance this object should be visible")
  lod_max_distance = bpy.props.FloatProperty(
    default=10000, min=0, soft_max=10000, step=10, unit="LENGTH",
    name="LOD Max Distance",
    description="The maximum distance this object should be visible")
  nouse_lod_distance = bpy.props.BoolProperty(
    default=True,
    name="No Max",
    description="Should there be no maximum view distance?")


def updateSceneArgument(self, context):
  print(self, context)
  print("Updating scene argument")

def register():
  bpy.utils.register_class(EDMObjectSettings)
  bpy.types.Object.edm = bpy.props.PointerProperty(type=EDMObjectSettings)
  bpy.types.Action.argument = bpy.props.IntProperty(name="Argument", default=-1, min=-1)
  bpy.types.Material.edm_material = bpy.props.EnumProperty(
      items=_edm_matTypes, default="def_material", name="Base Material",
      description="The internal EDM material to use as a basis")
  bpy.types.Material.edm_blending = bpy.props.EnumProperty(
      items=_edm_blendTypes, default="0", name="Opacity mode",
      description="The method to use for calculating material opacity/alpha blending")

  bpy.types.Scene.active_edm_argument = bpy.props.IntProperty(name="Active Argument", default=-1, min=-1, update=updateSceneArgument)


def unregister():
  del bpy.types.Scene.active_edm_argument
  del bpy.types.Material.edm_blending
  del bpy.types.Material.edm_material
  del bpy.types.Action.argument
  del bpy.types.Object.edm
  bpy.utils.unregister_class(EDMObjectSettings)

