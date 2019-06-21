
# shapekey
def Shapekey(self, context, layout, owner, datablock):
  '''
    Shapekey buttons.
  '''

  ob = owner
  key = ob.data.shape_keys
  kb = ob.active_shape_key

  enable_edit = ob.mode != 'EDIT'
  enable_edit_value = False

  if ob.show_only_shape_key is False:
    if enable_edit or (ob.type == 'MESH' and ob.use_shape_key_edit_mode):
      enable_edit_value = True

  row = layout.row()

  rows = 2
  if kb:
    rows = 4
  row.template_list('MESH_UL_shape_keys', '', key, 'key_blocks', ob, 'active_shape_key_index', rows=rows)

  column = row.column()

  sub = column.column(align=True)
  sub.operator('object.shape_key_add', icon='ZOOMIN', text='').from_mix = False
  sub.operator('object.shape_key_remove', icon='ZOOMOUT', text='').all = False
  sub.menu('MESH_MT_shape_key_specials', icon='DOWNARROW_HLT', text='')

  if kb:
    column.separator()

    sub = column.column(align=True)
    sub.operator('object.shape_key_move', icon='TRIA_UP', text='').type = 'UP'
    sub.operator('object.shape_key_move', icon='TRIA_DOWN', text='').type = 'DOWN'

    split = layout.split(percentage=0.4)
    row = split.row()
    row.enabled = enable_edit
    row.prop(key, 'use_relative')

    row = split.row()
    row.alignment = 'RIGHT'

    sub = row.row(align=True)
    sub.label()  # XXX, for alignment only
    subsub = sub.row(align=True)
    subsub.active = enable_edit_value
    subsub.prop(ob, 'show_only_shape_key', text='')
    sub.prop(ob, 'use_shape_key_edit_mode', text='')

    sub = row.row()
    if key.use_relative:
      sub.operator('object.shape_key_clear', icon='X', text='')
    else:
      sub.operator('object.shape_key_retime', icon='RECOVER_LAST', text='')

    if key.use_relative:
      if ob.active_shape_key_index != 0:
        row = layout.row()
        row.active = enable_edit_value
        row.prop(kb, 'value')

        split = layout.split()

        column = split.column(align=True)
        column.active = enable_edit_value
        column.label(text='Range:')
        column.prop(kb, 'slider_min', text='Min')
        column.prop(kb, 'slider_max', text='Max')

        column = split.column(align=True)
        column.active = enable_edit_value
        column.label(text='Blend:')
        column.prop_search(kb, 'vertex_group', ob, 'vertex_groups', text='')
        column.prop_search(kb, 'relative_key', key, 'key_blocks', text='')

    else:
      layout.prop(kb, 'interpolation')
      row = layout.column()
      row.active = enable_edit_value
      row.prop(key, 'eval_time')
