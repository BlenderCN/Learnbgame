import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty
from .operatorHelpers import resetTriggerSettings, setTrigger

operators = []
idnamePrefix = "radix"

class TriggerSetOperator(bpy.types.Operator):
  """Operator to convert an object to a trigger"""
  bl_idname = 'gpl.trigger_set'
  bl_label = 'Trigger'
  bl_description = 'Set trigger operator'
  bl_options = {'INTERNAL'}

  type = StringProperty(default="")
  filePath = StringProperty(default="")
  loop = BoolProperty(default=False)

  def execute(self, context):
    objects = bpy.context.selected_objects

    if not (objects and self.type):
      return {'CANCELLED'}

    for object in objects:
      if object.type == 'MESH':
        if object.radixTypes != "model":
          setTrigger(object, self.type, self.filePath, self.loop)
        else:
          self.report(
            {'ERROR'}, "Models can't be converted to the %s trigger." % (self.type)
          )
      else:
        self.report(
          {'ERROR'},
          "Object of type '%s' can't be converted to the %s trigger." % (object.type, self.type)
        )
    return {'FINISHED'}
