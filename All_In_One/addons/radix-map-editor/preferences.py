import os
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, EnumProperty, StringProperty

from .operatorHelpers import itemsMaterial
from .preferencesHelper import updateTriggerXrays, updateDefaultMaterial, updateDataDir
from .managers import MaterialManager as MM


class Preferences(AddonPreferences):
  bl_idname = __package__

  triggerXrays = BoolProperty(
    name="Use X-Rays for triggers",
    description="Enable X-rays for triggers.",
    default=True,
    update=updateTriggerXrays
  )
  dataDir = StringProperty(
    name="Set up Radix data directory",
    default=os.path.expanduser("~/.glportal/data/"),
    subtype='DIR_PATH',
    update=updateDataDir
  )
  gameExe = StringProperty(
    name="Set up game executable",
    default=os.path.expanduser("/usr/bin/glportal"),
    subtype='FILE_PATH'
  )
  defaultMaterial = StringProperty(
    default="metal/tiles00x3"
  )
  materials = EnumProperty(
    name="Default material",
    items=itemsMaterial,
    update=updateDefaultMaterial
  )

  def draw(self, context):
    layout = self.layout

    layout.prop(self, "triggerXrays")

    if len(MM.MATERIALS) > 1:
      if self.defaultMaterial in MM.MATERIALS:
        self.materials = self.defaultMaterial
      else:
        layout.label(text="Default material is not on the list.", icon='ERROR')
    else:
      layout.label(text="Material list is empty", icon='ERROR')
    layout.prop(self, "materials")

    layout.prop(self, "dataDir")
    if not os.path.isdir(os.path.expanduser(self.dataDir)):
      layout.label(text="Current data directory does not exist", icon='ERROR')

    layout.prop(self, "gameExe")
    if not os.path.isfile(os.path.expanduser(self.gameExe)):
      layout.label(text="Current game executable does not exist", icon='ERROR')
