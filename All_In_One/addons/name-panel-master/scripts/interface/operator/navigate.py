
# imports
import bpy
from bpy.types import Operator
from bpy.props import StringProperty

# previous
class previous(Operator):
  '''
    Return to previous settings context.
  '''
  bl_idname = 'view3d.name_panel_previous'
  bl_label = 'Back'
  bl_description = 'Return to previous settings context.'
  bl_options = {'UNDO', 'INTERNAL'}

  # poll
  @ classmethod
  def poll(cls, context):
    '''
      Ensure operator is being ran in the 3D View.
    '''
    return context.space_data.type == 'VIEW_3D'

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # panel
    panel = context.scene.NamePanel

    # store
    previousOwner = panel.owner
    previousTarget = panel.target
    previousContext = panel.context

    # update
    panel.owner = panel.previousOwner
    panel.target = panel.previousTarget
    panel.context = panel.previousContext

    # previous
    panel.previousOwner = previousOwner
    panel.previousTarget = previousTarget
    panel.previousContext = previousContext

    return {'FINISHED'}

# to object
class toObject(Operator):
  '''
    Switch to object settings context.
  '''
  bl_idname = 'view3d.name_panel_to_object'
  bl_label = 'Object'
  bl_description = 'Switch to object settings context.'
  bl_options = {'UNDO', 'INTERNAL'}

  # poll
  @ classmethod
  def poll(cls, context):
    '''
      Ensure operator is being ran in the 3D View.
    '''
    return context.space_data.type == 'VIEW_3D'

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # panel
    panel = context.scene.NamePanel

    # store
    panel.context = 'OBJECT'

    return {'FINISHED'}

# to data
class toData(Operator):
  '''
    Switch to object data settings context.
  '''
  bl_idname = 'view3d.name_panel_to_data'
  bl_label = 'Data'
  bl_description = 'Switch to object data settings context.'
  bl_options = {'UNDO', 'INTERNAL'}

  # poll
  @ classmethod
  def poll(cls, context):
    '''
      Ensure operator is being ran in the 3D View.
    '''
    return context.space_data.type == 'VIEW_3D'

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # panel
    panel = context.scene.NamePanel

    # store
    panel.context = 'OBJECT_DATA'

    return {'FINISHED'}

# to bone
class toBone(Operator):
  '''
    Switch to bone settings context.
  '''
  bl_idname = 'view3d.name_panel_to_bone'
  bl_label = 'Bone'
  bl_description = 'Switch to bone settings context.'
  bl_options = {'UNDO', 'INTERNAL'}

  # poll
  @ classmethod
  def poll(cls, context):
    '''
      Ensure operator is being ran in the 3D View.
    '''
    return context.space_data.type == 'VIEW_3D'

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # panel
    panel = context.scene.NamePanel

    # store
    panel.context = 'BONE'

    return {'FINISHED'}
