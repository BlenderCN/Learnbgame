
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
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty

# make active bone
class vertexGroup(Operator):
  '''
    Selects a vertex group when called.
  '''
  bl_idname = 'object.select_vertex_group'
  bl_label = 'Make Active Bone'
  bl_description = 'Select this vertex group.'
  bl_options = {'REGISTER', 'UNDO'}

  # object
  object  = StringProperty(
    name = 'Object',
    description = 'The object the vertex group is in.',
    default = ''
  )

  # target
  target = StringProperty(
    name = 'Target',
    description = 'The target vertex group that will be selected.',
    default = ''
  )

  # extend
  extend = BoolProperty(
    name = 'Extend Selection',
    description = 'Extend the selection.',
    default = False
  )

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    try:
      if bpy.data.objects[self.object] != context.scene.objects.active:

        # select
        context.scene.objects.active.select = True

        # mode set
        bpy.ops.object.mode_set(mode='OBJECT')

        # active object
        context.scene.objects.active = bpy.data.objects[self.object]
      if not context.object.mode in 'EDIT':

        # mode set
        bpy.ops.object.mode_set(mode='EDIT')

      # bmesh
      mesh = bmesh.from_edit_mesh(context.active_object.data)

      # extend
      if not self.extend:

        # clear vertex
        for vertex in mesh.verts:
          vertex.select = False

        # clear edge
        for edge in mesh.edges:
          edge.select = False

        # clear face
        for face in mesh.faces:
          face.select = False

      # group index
      groupIndex = context.active_object.vertex_groups[self.target].index

      # deform layer
      deformLayer = mesh.verts.layers.deform.active

      # select vertices
      for vertex in mesh.verts:
        deformVertex = vertex[deformLayer]
        if groupIndex in deformVertex:
          vertex.select = True

      # flush selection
      mesh.select_flush(True)

      # update viewport
      context.scene.objects.active = context.scene.objects.active

    except:

      # warning messege
      self.report({'WARNING'}, 'Invalid target.')
    return {'FINISHED'}
