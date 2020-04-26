
# imports
import bpy
from bpy.types import Operator

# name
class name(Operator):
  '''
    Default settings for the auto name operator.
  '''
  bl_idname = 'wm.auto_name_defaults'
  bl_label = 'Auto Name Defaults'
  bl_description = 'Current settings for the auto name operator.'
  bl_options = {'INTERNAL'}

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    from ..auto import name
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
    size = 330 if not context.window_manager.BatchShared.largePopups else 460
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
