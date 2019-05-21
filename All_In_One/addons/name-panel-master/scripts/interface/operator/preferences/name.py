
# imports
import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

# name
class name(Operator):
  '''
    Name Panel.
  '''
  bl_idname = 'wm.name_panel_defaults'
  bl_label = 'Name Panel Defaults'
  bl_description = 'Current settings for name panel.'
  bl_options = {'INTERNAL'}

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Operator body.
    '''

    # layout
    layout = self.layout

    # panel
    panel = context.scene.NamePanel

    # column
    column = layout.column(align=True)

    # row
    row = column.row(align=True)

    # scale
    row.scale_y = 1.25

    # icon toggle
    iconToggle = 'RADIOBUT_ON' if panel.filters else 'RADIOBUT_OFF'

    # filters
    row.prop(panel, 'filters', text='Filters', icon=iconToggle, toggle=True)

    # options
    row.prop(panel, 'shortcuts', text='', icon='SETTINGS')

    # # operator menu
    row.menu('VIEW3D_MT_name_panel_specials', text='', icon='COLLAPSEMENU')

    # filters
    if panel.filters:

      # separate
      column.separator()

      # row
      row = column.row(align=True)

      # scale
      row.scale_x = 5 # hack: forces buttons to line up correctly

      # action
      row.prop(panel, 'action', text='', icon='ACTION')

      # grease pencil
      row.prop(panel, 'greasePencil', text='', icon='GREASEPENCIL')

      # groups
      row.prop(panel, 'groups', text='', icon='GROUP')

      # constraints
      row.prop(panel, 'constraints', text='', icon='CONSTRAINT')

      # modifiers
      row.prop(panel, 'modifiers', text='', icon='MODIFIER')

      # bone groups
      row.prop(panel, 'boneGroups', text='', icon='GROUP_BONE')

      # bone constraints
      row.prop(panel, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

      # row
      row = column.row(align=True)

      # scale
      row.scale_x = 5 # hack: forces buttons to line up correctly

      # vertex groups
      row.prop(panel, 'vertexGroups', text='', icon='GROUP_VERTEX')

      # shapekeys
      row.prop(panel, 'shapekeys', text='', icon='SHAPEKEY_DATA')

      # uvs
      row.prop(panel, 'uvs', text='', icon='GROUP_UVS')

      # vertex colors
      row.prop(panel, 'vertexColors', text='', icon='GROUP_VCOL')

      # materials
      row.prop(panel, 'materials', text='', icon='MATERIAL')

      # textures
      row.prop(panel, 'textures', text='', icon='TEXTURE')

      # particles systems
      row.prop(panel, 'particleSystems', text='', icon='PARTICLES')

      # hide find & replace
      if panel.hideFindReplace:

        # separate
        column.separator()

        # row
        row = column.row(align=True)

        # find
        row.prop(panel, 'search', text='', icon='VIEWZOOM')

        # sub
        sub = row.split(align=True)

        # scale x
        sub.scale_x = 0.1

        # regex
        sub.prop(panel, 'regex', text='.*', toggle=True)

        # row
        row = column.row(align=True)

        # replace
        row.prop(context.window_manager.BatchName, 'replace', text='', icon='FILE_REFRESH')

        # sub
        sub = row.split(align=True)

        # scale x
        sub.scale_x = 0.15

        # batch name
        op = sub.operator('wm.batch_name', text='OK')
        op.simple = True
        op.quickBatch = True

        # batch name
        op = row.operator('wm.batch_name', text='', icon='SORTALPHA')
        op.simple = False
        op.quickBatch = True

    # hide find & replace
    if not panel.hideFindReplace:

      # separate
      column.separator()

      # row
      row = column.row(align=True)

      # find
      row.prop(panel, 'search', text='', icon='VIEWZOOM')

      # sub
      sub = row.split(align=True)

      # scale x
      sub.scale_x = 0.1

      # regex
      sub.prop(panel, 'regex', text='.*', toggle=True)

      # row
      row = column.row(align=True)

      # replace
      row.prop(context.window_manager.BatchName, 'replace', text='', icon='FILE_REFRESH')

      # sub
      sub = row.split(align=True)

      # scale x
      sub.scale_x = 0.15

      # batch name
      op = sub.operator('wm.batch_name', text='OK')
      op.simple = True
      op.quickBatch = True

      # batch name
      op = row.operator('wm.batch_name', text='', icon='SORTALPHA')
      op.simple = False
      op.quickBatch = True

    # separate
    column.separator()

    # row
    row = column.row()

    # display names
    row.prop(panel, 'displayNames', icon='OBJECT_DATA')

    # enabled
    if panel.displayNames:

      # separate
      column.separator()

      # row
      row = column.row()

      # mode
      row.prop(panel, 'mode', expand=True)

    # separate
    column.separator()

    # row
    row = column.row()

    # display bones
    row.prop(panel, 'displayBones', icon='BONE_DATA')

    # display bones
    if panel.displayBones:

      # separate
      column.separator()

      # row
      row = column.row()

      # bone mode
      row.prop(panel, 'boneMode', expand=True)

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
    size = 200 if not context.window_manager.BatchShared.largePopups else 400
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
