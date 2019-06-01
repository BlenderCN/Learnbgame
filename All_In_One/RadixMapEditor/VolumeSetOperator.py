import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .operatorHelpers import resetTriggerSettings, simpleCube, setTrigger
from .managers import ModelManager

class VolumeSetOperator(bpy.types.Operator):
  """Volume set operator"""
  bl_idname = "radix.volume"
  bl_label = "Volume"
  bl_description = "Mark the selection as volume."
  bl_options = {'INTERNAL'}

  material = StringProperty(default="")
  volumeType = StringProperty(default="")

  def execute(self, context):
    objects = bpy.context.selected_objects

    if not (objects and self.material and self.volumeType):
      return {'CANCELLED'}

    for object in objects:
      if object.type == 'MESH':
        if object.radixTypes != "model":
          resetTriggerSettings(object)
          object.radixTypes = "volume"
          object.radixVolumeTypes = self.volumeType

        object.radixMaterial = self.material
      else:
        self.report(
          {'ERROR'}, "Object of type '%s' can't be converted to the volume." % (object.type)
        )
    return {'FINISHED'}
