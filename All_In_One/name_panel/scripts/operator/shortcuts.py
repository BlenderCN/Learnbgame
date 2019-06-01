
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# imports
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..interface.shortcuts.constraints import ConstraintButtons
from ..interface.shortcuts.modifiers import ModifierButtons

# constraints
class constraint(ConstraintButtons, Operator):
  '''
    This is operator is used to create the required modal panel.
  '''
  bl_idname = 'view3d.constraint_settings'
  bl_label = 'Constraint'
  bl_description = 'Adjust the options for this constraint. (Experimental)'
  bl_options = {'REGISTER', 'UNDO'}

  # object
  object = StringProperty(
    name = 'Object',
    description = 'The object that the constraint is attached to.',
    default = ''
  )

  # bone
  bone = StringProperty(
    name = 'Bone',
    description = 'The bone that the constraint is attached to.'
  )

  # target
  target = StringProperty(
    name = 'Target',
    description = 'The constraint you wish to edit the settings of.',
    default = ''
  )

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the constraint options.
    '''

    # layout
    layout = self.layout

    # column
    column = layout.column()

    # # object
    # column.prop(self, 'object')
    #
    # if context.mode in 'POSE':
    #   # bone
    #   column.prop(self, 'bone')
    #
    # # target
    # column.prop(self, 'target')
    #
    # # separator
    # column.separator()

    # label
    column.label(text=self.target + ':')

    # constraint
    if not bpy.data.objects[self.object].type in 'ARMATURE':
      ConstraintButtons.main(ConstraintButtons, context, layout, bpy.data.objects[self.object].constraints[self.target])

    else:
      ConstraintButtons.main(ConstraintButtons, context, layout, bpy.data.objects[self.object].pose.bones[self.bone].constraints[self.target])

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
    context.window_manager.invoke_popup(self, width=350)
    return {'RUNNING_MODAL'}

# modifier modal
class modifier(ModifierButtons, Operator):
  '''
    This is operator is used to create the required modal panel.
  '''
  bl_idname = 'view3d.modifier_settings'
  bl_label = 'Modifier'
  bl_description = 'Adjust the options for this modifier. (Experimental)'
  bl_options = {'REGISTER', 'UNDO'}

  # object
  object = StringProperty(
    name = 'Object',
    description = 'The object that the modifier is attached to.',
    default = ''
  )

  # target
  target = StringProperty(
    name = 'Target',
    description = 'The modifier you wish to edit the settings of.',
    default = ''
  )

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the modifier options.
    '''

    # layout
    layout = self.layout

    # column
    column = layout.column()

    # # object
    # column.prop(self, 'object')
    #
    # # target
    # column.prop(self, 'target')
    #
    # # separator
    # column.separator()

    # label
    column.label(text=self.target + ':')

    # modifier
    ModifierButtons.main(ModifierButtons, context, layout, bpy.data.objects[self.object].modifiers[self.target], bpy.data.objects[self.object])

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
    context.window_manager.invoke_popup(self, width=350)
    return {'RUNNING_MODAL'}
