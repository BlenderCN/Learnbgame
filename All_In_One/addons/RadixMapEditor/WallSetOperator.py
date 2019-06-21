import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .operatorHelpers import resetTriggerSettings, simpleCube, setTrigger
from .managers import ModelManager

operators = []
idnamePrefix = "radix"

class WallSetOperator(bpy.types.Operator):
  """Wall set operator"""
  bl_idname = "radix.wall"
  bl_label = "Wall"
  bl_description = "Mark the selection as wall."
  bl_options = {'INTERNAL'}

  material = StringProperty(default="")

  def execute(self, context):
    objects = bpy.context.selected_objects

    if not (objects and self.material):
      return {'CANCELLED'}

    for object in objects:
      if object.type == 'MESH':
        if object.radixTypes != "model":
          resetTriggerSettings(object)
          object.radixTypes = "wall"

        object.radixMaterial = self.material
      else:
        self.report(
          {'ERROR'}, "Object of type '%s' can't be converted to the wall." % (object.type)
        )
    return {'FINISHED'}
