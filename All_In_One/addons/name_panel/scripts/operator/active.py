
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

# object
class object(Operator):
  '''
    Assigns an active object when called.
  '''
  bl_idname = 'view3d.active_object'
  bl_label = 'Make Active Object'
  bl_description = 'Makes this selected object the active object.'
  bl_options = {'REGISTER', 'UNDO'}

  # target
  target = StringProperty(
    name = 'Target',
    description = 'The target object that will become the active object.',
    default = ''
  )

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view and there must be an active object.
    '''
    return context.space_data.type in 'VIEW_3D' and context.active_object

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    try:

      # select
      bpy.data.objects[context.active_object.name].select = True

      # mode set
      bpy.ops.object.mode_set(mode='OBJECT')

      # target
      context.scene.objects.active = bpy.data.objects[self.target]
    except:

      # warning messege
      self.report({'WARNING'}, 'Invalid target.')
    return {'FINISHED'}

# bone
class bone(Operator):
  '''
    Assigns an active bone when called.
  '''
  bl_idname = 'view3d.active_bone'
  bl_label = 'Make Active Bone'
  bl_description = 'Makes this selected bone the active bone.'
  bl_options = {'REGISTER', 'UNDO'}

  # target
  target = StringProperty(
    name = 'Target',
    description = 'The target bone that will become the active object.',
    default = ''
  )

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view and there must be an active bone.
    '''
    return context.space_data.type in 'VIEW_3D' and context.active_bone or context.active_pose_bone

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    try:

      # edit mode
      if context.object.mode in 'EDIT':

        # select
        context.active_object.data.edit_bones.active.select = True

        # select head
        context.active_object.data.edit_bones.active.select_head = True

        # select tail
        context.active_object.data.edit_bones.active.select_tail = True

        # active bone
        context.scene.objects[context.active_object.name].data.edit_bones.active = bpy.data.armatures[context.active_object.data.name].edit_bones[self.target]

        # select head
        context.active_object.data.edit_bones.active.select_head = True

        # select tail
        context.active_object.data.edit_bones.active.select_tail = True

      # pose mode
      else:

        # select
        context.active_object.data.bones.active.select = True

        # target
        context.scene.objects[context.active_object.name].data.bones.active = bpy.data.armatures[context.active_object.data.name].bones[self.target]
    except:

      # warning messege
      self.report({'WARNING'}, 'Invalid target.')
    return {'FINISHED'}
