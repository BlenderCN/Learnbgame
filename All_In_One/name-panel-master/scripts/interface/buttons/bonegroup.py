
# bone group
def BoneGroup(self, context, layout, owner, datablock):
  '''
    Bone group buttons.
  '''

  row = layout.row()

  rows = 1
  if owner.pose.bone_groups.active:
    rows = 4
  row.template_list('UI_UL_list', 'bone_groups', owner.pose, 'bone_groups', owner.pose.bone_groups, 'active_index', rows=rows)

  column = row.column(align=True)
  column.active = (owner.proxy is None)
  column.operator('pose.group_add', icon='ZOOMIN', text='')
  column.operator('pose.group_remove', icon='ZOOMOUT', text='')
  column.menu('DATA_PT_bone_group_specials', icon='DOWNARROW_HLT', text='')
  if owner.pose.bone_groups.active:
    column.separator()
    column.operator('pose.group_move', icon='TRIA_UP', text='').direction = 'UP'
    column.operator('pose.group_move', icon='TRIA_DOWN', text='').direction = 'DOWN'

    split = layout.split()
    split.active = (owner.proxy is None)

    column = split.column()
    column.prop(owner.pose.bone_groups.active, 'color_set')
    if owner.pose.bone_groups.active.color_set:
      column = split.column()
      sub = column.row(align=True)
      sub.enabled = owner.pose.bone_groups.active.is_custom_color_set  # only custom colors are editable
      sub.prop(owner.pose.bone_groups.active.colors, 'normal', text='')
      sub.prop(owner.pose.bone_groups.active.colors, 'select', text='')
      sub.prop(owner.pose.bone_groups.active.colors, 'active', text='')

  row = layout.row()
  row.active = (owner.proxy is None)

  sub = row.row(align=True)
  sub.operator('pose.group_assign', text='Assign')
  sub.operator('pose.group_unassign', text='Remove')  # row.operator('pose.bone_group_remove_from', text='Remove')

  sub = row.row(align=True)
  sub.operator('pose.group_select', text='Select')
  sub.operator('pose.group_deselect', text='Deselect')
