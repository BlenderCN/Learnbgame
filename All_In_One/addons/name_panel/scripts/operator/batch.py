
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
from bpy.props import BoolProperty
from bpy.types import Operator
from ..function import batch

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# name
class name(Operator):
  '''
    Batch name datablocks.
  '''
  bl_idname = 'wm.batch_name'
  bl_label = 'Batch Name'
  bl_description = 'Batch name datablocks.'
  bl_options = {'UNDO'}

  # quick batch
  quickBatch = BoolProperty(
    name = 'Quick Batch',
    description = 'Quickly batch name datablocks visible in the name panel.',
    default = False
  )

  # draw
  def draw(self, context):
    '''
      Operator body.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchName

    # filter

    # column
    column = layout.column(align=True)

    # quick batch
    if not self.quickBatch:

      # label
      column.label(text='Filter:')

      # row
      row = column.row(align=True)

      # batch type
      row.prop(option, 'mode', expand=True)

      # column
      column = layout.column(align=True)

      # row 1
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'actions', text='', icon='ACTION')
      row.prop(option, 'greasePencil', text='', icon='GREASEPENCIL')
      row.prop(option, 'objects', text='', icon='OBJECT_DATA')
      row.prop(option, 'groups', text='', icon='GROUP')
      row.prop(option, 'constraints', text='', icon='CONSTRAINT')
      row.prop(option, 'modifiers', text='', icon='MODIFIER')
      row.prop(option, 'objectData', text='', icon='MESH_DATA')
      row.prop(option, 'bones', text='', icon='BONE_DATA')
      row.prop(option, 'boneGroups', text='', icon='GROUP_BONE')
      row.prop(option, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

      # row 2
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'actionGroups', text='', icon='NLA')
      row.prop(option, 'pencilLayers', text='', icon='OOPS')
      row.prop(option, 'vertexGroups', text='', icon='GROUP_VERTEX')
      row.prop(option, 'shapekeys', text='', icon='SHAPEKEY_DATA')
      row.prop(option, 'uvs', text='', icon='GROUP_UVS')
      row.prop(option, 'vertexColors', text='', icon='GROUP_VCOL')
      row.prop(option, 'materials', text='', icon='MATERIAL')
      row.prop(option, 'textures', text='', icon='TEXTURE')
      row.prop(option, 'particleSystems', text='', icon='PARTICLES')
      row.prop(option, 'particleSettings', text='', icon='MOD_PARTICLES')

      # type filters
      column = layout.column()
      column.prop(option, 'objectType', text='')
      column.prop(option, 'constraintType', text='')
      column.prop(option, 'modifierType', text='')

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Game Engine:')

      # row
      row = column.row(align=True)
      row.prop(option, 'sensors', text='Sensors', toggle=True)
      row.prop(option, 'controllers', text='Controllers', toggle=True)
      row.prop(option, 'actuators', text='Actuators', toggle=True)


      # column
      column = layout.column(align=True)

      # label
      column.label(text='Global:')

      # row 1
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'scenes', text='', icon='SCENE_DATA')
      row.prop(option, 'renderLayers', text='', icon='RENDERLAYERS')
      row.prop(option, 'worlds', text='', icon='WORLD')
      row.prop(option, 'libraries', text='', icon='LIBRARY_DATA_DIRECT')
      row.prop(option, 'images', text='', icon='IMAGE_DATA')
      row.prop(option, 'masks', text='', icon='MOD_MASK')
      row.prop(option, 'sequences', text='', icon='SEQUENCE')
      row.prop(option, 'movieClips', text='', icon='CLIP')
      row.prop(option, 'sounds', text='', icon='SOUND')

      # row 2
      row = column.row(align=True)
      row.scale_x = 5
      row.prop(option, 'screens', text='', icon='SPLITSCREEN')
      row.prop(option, 'keyingSets', text='', icon='KEYINGSET')
      row.prop(option, 'palettes', text='', icon='COLOR')
      row.prop(option, 'brushes', text='', icon='BRUSH_DATA')
      row.prop(option, 'texts', text='', icon='TEXT')
      row.prop(option, 'nodes', text='', icon='NODE_SEL')
      row.prop(option, 'nodeLabels', text='', icon='NODE')
      row.prop(option, 'frameNodes', text='', icon='FULLSCREEN')
      row.prop(option, 'nodeGroups', text='', icon='NODETREE')

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Freestyle:')

      # row
      row = column.row(align=True)
      row.scale_x = 1.5
      row.prop(option, 'lineSets', text='', icon='BRUSH_TEXDRAW')
      row.prop(option, 'linestyles', text='', icon='LINE_DATA')
      row.prop(option, 'linestyleModifiers', text='', icon='MODIFIER')
      row.prop(option, 'linestyleModifierType', text='')

      # input fields
      column.separator()
      column.separator()
      column.separator()
      column.separator()

    # quick batch
    else:

      # label
      column.label(text='Ignore:')

      # column
      column = layout.column(align=True)

      split = column.split(align=True)

      split.prop(option, 'ignoreObject', text='', icon='OBJECT_DATA')
      split.prop(option, 'ignoreAction', text='', icon='ACTION')
      split.prop(option, 'ignoreGreasePencil', text='', icon='GREASEPENCIL')
      split.prop(option, 'ignoreGroup', text='', icon='GROUP')
      split.prop(option, 'ignoreConstraint', text='', icon='CONSTRAINT')
      split.prop(option, 'ignoreModifier', text='', icon='MODIFIER')
      split.prop(option, 'ignoreBone', text='', icon='BONE_DATA')
      split.prop(option, 'ignoreBoneGroup', text='', icon='GROUP_BONE')
      split.prop(option, 'ignoreBoneConstraint', text='', icon='CONSTRAINT_BONE')

      split = column.split(align=True)
      split.prop(option, 'ignoreObjectData', text='', icon='MESH_DATA')
      split.prop(option, 'ignoreVertexGroup', text='', icon='GROUP_VERTEX')
      split.prop(option, 'ignoreShapekey', text='', icon='SHAPEKEY_DATA')
      split.prop(option, 'ignoreUV', text='', icon='GROUP_UVS')
      split.prop(option, 'ignoreVertexColor', text='', icon='GROUP_VCOL')
      split.prop(option, 'ignoreMaterial', text='', icon='MATERIAL')
      split.prop(option, 'ignoreTexture', text='', icon='TEXTURE')
      split.prop(option, 'ignoreParticleSystem', text='', icon='PARTICLES')
      split.prop(option, 'ignoreParticleSetting', text='', icon='MOD_PARTICLES')


      # input fields
      column.separator()
      column.separator()
      column.separator()
      column.separator()

    # custom name
    column = layout.column(align=True)
    column.prop(option, 'customName')
    column.separator()
    column.separator()

    # find
    row = column.row(align=True)
    row.prop(option, 'find', icon='VIEWZOOM')

    # cheatsheet
    row.operator('wm.regular_expression_cheatsheet', text='', icon='FILE_TEXT')

    # regex
    row.prop(option, 'regex', text='', icon='SCRIPT')
    column.separator()

    # replace
    column.prop(option, 'replace', icon='FILE_REFRESH')
    column.separator()
    column.separator()

    # prefix
    column.prop(option, 'prefix', icon='LOOP_BACK')
    column.separator()

    # row
    row = column.row(align=True)

    # suffix
    row.prop(option, 'suffix', icon='LOOP_FORWARDS')
    row.prop(option, 'suffixLast', text='', icon='FORWARD')
    column.separator()
    column.separator()
    row = column.row()

    # trim start
    row.label(text='Trim Start:')
    row.prop(option, 'trimStart', text='')
    column.separator()
    row = column.row()

    # trim end
    row.label(text='Trim End:')
    row.prop(option, 'trimEnd', text='')
    column.separator()

    # sort duplicates
    column.separator()

    # row
    row = column.row(align=True)
    row.prop(option, 'sort', text='Sort Duplicates', toggle=True)
    row.prop(option, 'padding', text='Padding')
    row.prop(option, 'start', text='Start at')

    # sub
    sub = row.row(align=True)
    sub.scale_x = 0.1
    sub.prop(option, 'separator', text='')
    row.prop(option, 'sortOnly', text='', icon='LOCKED')
    row.prop(option, 'link', text='', icon='LINKED')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    globalUndo = context.user_preferences.edit.use_global_undo
    context.user_preferences.edit.use_global_undo = False

    # main
    batch.main(context, self.quickBatch)

    context.user_preferences.edit.use_global_undo = globalUndo
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''

    try:

      # size
      size = 320 if addon.preferences['largePopups'] == 0 else 450
    except:

      # size
      size = 320

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
