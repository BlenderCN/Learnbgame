
# imports
import bpy
from bpy.types import Operator
from ...function import copy

# name
class name(Operator):
  '''
    Transfer names from some types of datablocks to others.
  '''
  bl_idname = 'view3d.copy_name'
  bl_label = 'Copy Name'
  bl_description = 'Copy names from some types of datablocks to others.'
  bl_options = {'UNDO'}

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.window_manager.CopyName

    # row
    row = layout.row(align=True)

    # mode
    row.prop(option, 'mode', expand=True)

    # reset settings
    op = row.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
    op.panel = False
    op.auto = False
    op.names = False
    op.name = False
    op.copy = True

    # column
    column = layout.column(align=True)

    # source
    column.label(text='Copy:', icon='COPYDOWN')
    column = layout.column(align=True)
    column.prop(option, 'source', expand=True)
    column = layout.column(align=True)

    # targets
    column.label(text='Paste:', icon='PASTEDOWN')
    column = layout.column(align=True)
    split = column.split(align=True)
    split.prop(option, 'objects', text='', icon='OBJECT_DATA')
    split.prop(option, 'objectData', text='', icon='MESH_DATA')
    split.prop(option, 'materials', text='', icon='MATERIAL')
    split.prop(option, 'textures', text='', icon='TEXTURE')
    split.prop(option, 'particleSystems', text='', icon='PARTICLES')
    split.prop(option, 'particleSettings', text='', icon='MOD_PARTICLES')

    # use active object
    column = layout.column()
    column.prop(option, 'useActiveObject')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # copy
    copy.main(context)
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    size = 210 if not context.window_manager.BatchShared.largePopups else 340
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
