# import
import bpy

# action
def Action(self, context, layout, owner, datablock):
  '''
    Action buttons.
  '''

  # template id
  layout.template_ID(owner.animation_data, 'action')
