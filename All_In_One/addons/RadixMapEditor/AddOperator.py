import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .operatorHelpers import resetTriggerSettings, simpleCube, setTrigger
from .managers import ModelManager

operators = []
idnamePrefix = "radix"


class AddOperator(bpy.types.Operator):
  """Add operator"""
  bl_idname = 'gpl.add'
  bl_label = 'Add'
  bl_description = 'Add operator'
  bl_options = {'INTERNAL'}

  action = None
  kwargs = None

  def execute(self, context):
    if self.action:
      if isinstance(self.action, str):
        self.action = getattr(getattr(bpy.ops, idnamePrefix), self.action)

      if simpleCube():
        if self.kwargs:
          if isinstance(self.kwargs, dict):
            self.action(**self.kwargs)
          elif isinstance(self.kwargs, list):
            self.action(*self.kwargs)
        else:
          self.action()
        return {'FINISHED'}
    return {'CANCELLED'}
