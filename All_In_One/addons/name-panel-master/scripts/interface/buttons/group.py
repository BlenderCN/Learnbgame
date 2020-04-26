
# group
def Group(self, context, layout, datablock):
  '''
    Group buttons.
  '''

  import bpy
  panel = context.scene.NamePanel
  obj = bpy.data.objects[panel.owner]

  obj_name = obj.name
  column = layout.column(align=True)

  if obj_name in datablock.objects:
    column.context_pointer_set('group', datablock)

    row = column.row(align=True)
    row.prop(datablock, 'name', text='')
    row.operator('object.group_remove', text='', icon='X')
    row.menu('GROUP_MT_specials', icon='DOWNARROW_HLT', text='')

    column.separator()

    split = column.split()

    column = split.column()
    column.prop(datablock, 'layers', text='Dupli Visibility')

    column = split.column()
    column.prop(datablock, 'dupli_offset', text='')
