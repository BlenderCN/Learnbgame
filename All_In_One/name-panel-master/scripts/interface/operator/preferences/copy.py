
# imports
import bpy
from bpy.types import Operator

# name
class name(Operator):
  '''
    Default settings for the copy name operator.
  '''
  bl_idname = 'wm.copy_name_defaults'
  bl_label = 'Copy Name Defaults'
  bl_description = 'Current settings used for the copy name operator.'
  bl_options = {'INTERNAL'}

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    from ..copy import name
    name.draw(self, context)

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    size = 210 if not context.window_manager.BatchShared.largePopups else 340
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
