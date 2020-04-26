
# uv
def UV(self, context, layout, owner, datablock):
  '''
    UV buttons.
  '''

  ob = owner
  group = ob.vertex_groups.active

  rows = 2
  if group:
    rows = 4

  row = layout.row()
  row.template_list('MESH_UL_vgroups', '', ob, 'vertex_groups', ob.vertex_groups, 'active_index', rows=rows)

  column = row.column(align=True)
  column.operator('object.vertex_group_add', icon='ZOOMIN', text='')
  column.operator('object.vertex_group_remove', icon='ZOOMOUT', text='').all = False
  column.menu('MESH_MT_vertex_group_specials', icon='DOWNARROW_HLT', text='')
  if group:
    column.separator()
    column.operator('object.vertex_group_move', icon='TRIA_UP', text='').direction = 'UP'
    column.operator('object.vertex_group_move', icon='TRIA_DOWN', text='').direction = 'DOWN'

  if ob.vertex_groups and (ob.mode == 'EDIT' or (ob.mode == 'WEIGHT_PAINT' and ob.type == 'MESH' and ob.data.use_paint_mask_vertex)):
    row = layout.row()

    sub = row.row(align=True)
    sub.operator('object.vertex_group_assign', text='Assign')
    sub.operator('object.vertex_group_remove_from', text='Remove')

    sub = row.row(align=True)
    sub.operator('object.vertex_group_select', text='Select')
    sub.operator('object.vertex_group_deselect', text='Deselect')

    layout.prop(context.tool_settings, 'vertex_group_weight', text='Weight')
