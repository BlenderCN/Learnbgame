import bpy

from bpy.props import BoolProperty, IntProperty, StringProperty

from .managers import MaterialManager as MM


def initProperties():
  """Register material panel properties for Blender"""
  bpy.types.WindowManager.MPItemId = IntProperty(
    default=0,
    update=MPItemIdUpdate
  )
  bpy.types.WindowManager.radixMatName = StringProperty(
    name="Name",
    default=""
  )
  bpy.types.WindowManager.radixMatFancyName = StringProperty(
    name="FancyName",
    default=""
  )
  bpy.types.WindowManager.radixMatPortalable = BoolProperty(
    name="Portalable",
    default=False
  )
  bpy.types.WindowManager.radixMatKind = StringProperty(
    name="Kind",
    default=""
  )
  bpy.types.WindowManager.radixMatTags = StringProperty(
    name="Tags",
    default=""
  )
  bpy.types.WindowManager.radixMatEdit = BoolProperty(
    default=False
  )


def delProperties():
  """Unregister material panel properties from Blender"""
  del bpy.types.WindowManager.MPItemId
  del bpy.types.WindowManager.radixMatName
  del bpy.types.WindowManager.radixMatFancyName
  del bpy.types.WindowManager.radixMatPortalable
  del bpy.types.WindowManager.radixMatKind
  del bpy.types.WindowManager.radixMatTags
  del bpy.types.WindowManager.radixMatEdit


class Row(bpy.types.PropertyGroup):
  name = StringProperty()
  label = StringProperty()
  description = StringProperty()
  matName = StringProperty()


def MPItemIdUpdate(self, context):
  wm = bpy.context.window_manager

  name = wm.MPMaterials[wm.MPItemId].matName
  material = MM.MATERIALS[name]

  if name != "none":
    if wm.radixMatEdit:
      wm.radixMatName = name
      wm.radixMatFancyName = material["fancyname"]
      wm.radixMatKind = material["kind"]
      wm.radixMatPortalable = material["portalable"]

      if "tags" in material:
        wm.radixMatTags = material["tags"]

    #prefs = bpy.context.user_preferences.addons[__package__].preferences
    #path = os.path.expanduser(prefs.dataDir + "textures/" +  material["texture"])
    #MM.createTexture(path, material["fancyname"])

  #for area in bpy.context.screen.areas:
  #  if area.type in ['PROPERTIES']:
  #    area.tag_redraw()
