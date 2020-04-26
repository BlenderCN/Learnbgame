import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .operatorHelpers import resetTriggerSettings, simpleCube, setTrigger
from .managers import ModelManager

operators = []
idnamePrefix = "radix"

class SearchOperator(bpy.types.Operator):
  bl_idname = "radix.search"
  bl_label = "Add search"
  bl_description = 'Search operator'
  bl_property = "items"
  bl_options = {'INTERNAL'}

  action = None
  kwargs = None
  items = EnumProperty(items=[("none", "none", "none")])

  def execute(self, context):
    if self.items and self.items != "none":
      if self.action:
        if isinstance(self.action, str):
          self.action = getattr(getattr(bpy.ops, idnamePrefix), self.action)

        if self.kwargs and isinstance(self.kwargs, dict):
          args = self.kwargs.copy()
          args[self.kwargs["items"]] = self.items
          del args["items"]

          self.action(**args)
        else:
          self.action(self.items)
        return {'FINISHED'}
    return {'CANCELLED'}

  def invoke(self, context, event):
    context.window_manager.invoke_search_popup(self)
    return {'FINISHED'}
