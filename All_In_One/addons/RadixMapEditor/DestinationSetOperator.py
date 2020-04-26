import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty
from .operatorHelpers import resetTriggerSettings, setDestination

operators = []
idnamePrefix = "radix"

class DestinationSetOperator(bpy.types.Operator):
  """Operator to convert an object to a trigger"""
  bl_idname = 'gpl.set_destination'
  bl_label = 'Destination'
  bl_description = 'Set destination operator'
  bl_options = {'INTERNAL'}

  type = StringProperty(default="")
  destinationName = StringProperty(default="")

  def execute(self, context):
    objects = bpy.context.selected_objects

    if not (objects and self.type):
      return {'CANCELLED'}

    for object in objects:
      if object.type == 'MESH':
        if object.radixTypes != "model":
          setDestination(object, self.destinationName)
        else:
          self.report(
            {'ERROR'}, "Models can't be converted to destination." % (self.type)
          )
      else:
        self.report(
          {'ERROR'},
          "Object of type '%s' can't be converted to destination." % (object.type, self.type)
        )
    return {'FINISHED'}
