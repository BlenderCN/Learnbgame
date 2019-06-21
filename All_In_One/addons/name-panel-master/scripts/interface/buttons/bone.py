
# bone
def Bone(self, context, layout):
  '''
    Bone buttons.
  '''

  layout.prop(context.active_bone, 'name', text='')

  layout.label(text='Relations:')

  split = layout.split()

  column = split.column()
  column.label(text='Layers:')
  column.prop(context.active_bone, 'layers', text='')

  column.separator()

  if context.active_pose_bone:
    column.label(text='Bone Group:')
    column.prop_search(context.active_pose_bone, 'bone_group', context.active_object.pose, 'bone_groups', text='')
    column.label(text='Object Children:')
    column.prop(context.active_bone, 'use_relative_parent')

  column = split.column()
  column.label(text='Parent:')
  if context.active_pose_bone:
      column.prop(context.active_bone, 'parent', text='')
  else:
      column.prop_search(context.active_bone, 'parent', context.active_object.data, 'edit_bones', text='')

  sub = column.column()
  sub.active = (context.active_bone.parent is not None)
  sub.prop(context.active_bone, 'use_connect')
  sub.prop(context.active_bone, 'use_inherit_rotation')
  sub.prop(context.active_bone, 'use_inherit_scale')
  sub = column.column()
  sub.active = (not context.active_bone.parent or not context.active_bone.use_connect)
  sub.prop(context.active_bone, 'use_local_location')

  layout.separator()


  if context.mode == 'POSE':

    layout.label(text='Display:')

    if context.active_bone:
      split = layout.split()

      column = split.column()
      column.prop(context.active_bone, 'hide', text='Hide')
      sub = column.column()
      sub.active = bool(context.active_pose_bone and context.active_pose_bone.custom_shape)
      sub.prop(context.active_bone, 'show_wire', text='Wireframe')

      if context.active_pose_bone:
        column = split.column()

        column.label(text='Custom Shape:')
        column.prop(context.active_pose_bone, 'custom_shape', text='')
        if context.active_pose_bone.custom_shape:
          column.prop(context.active_pose_bone, 'use_custom_shape_bone_size', text='Bone Size')
          column.prop(context.active_pose_bone, 'custom_shape_scale', text='Scale')
          column.prop_search(context.active_pose_bone, 'custom_shape_transform', context.active_object.pose, 'bones', text='At')
    layout.separator()


  try: active = context.active_pose_bone.is_in_ik_chain
  except: active = False
  if context.mode == 'POSE' and active:
    layout.label(text='Inverse Kinematics:')
    row = layout.row()

    split = layout.split(percentage=0.25)
    split.prop(context.active_pose_bone, 'lock_ik_x', text='X')
    split.active = active
    row = split.row()
    row.prop(context.active_pose_bone, 'ik_stiffness_x', text='Stiffness', slider=True)
    row.active = context.active_pose_bone.lock_ik_x is False and active

    split = layout.split(percentage=0.25)
    sub = split.row()

    sub.prop(context.active_pose_bone, 'use_ik_limit_x', text='Limit')
    sub.active = context.active_pose_bone.lock_ik_x is False and active
    sub = split.row(align=True)
    sub.prop(context.active_pose_bone, 'ik_min_x', text='')
    sub.prop(context.active_pose_bone, 'ik_max_x', text='')
    sub.active = context.active_pose_bone.lock_ik_x is False and context.active_pose_bone.use_ik_limit_x and active

    split = layout.split(percentage=0.25)
    split.prop(context.active_pose_bone, 'lock_ik_y', text='Y')
    split.active = active
    row = split.row()
    row.prop(context.active_pose_bone, 'ik_stiffness_y', text='Stiffness', slider=True)
    row.active = context.active_pose_bone.lock_ik_y is False and active

    split = layout.split(percentage=0.25)
    sub = split.row()

    sub.prop(context.active_pose_bone, 'use_ik_limit_y', text='Limit')
    sub.active = context.active_pose_bone.lock_ik_y is False and active

    sub = split.row(align=True)
    sub.prop(context.active_pose_bone, 'ik_min_y', text='')
    sub.prop(context.active_pose_bone, 'ik_max_y', text='')
    sub.active = context.active_pose_bone.lock_ik_y is False and context.active_pose_bone.use_ik_limit_y and active

    split = layout.split(percentage=0.25)
    split.prop(context.active_pose_bone, 'lock_ik_z', text='Z')
    split.active = active
    sub = split.row()
    sub.prop(context.active_pose_bone, 'ik_stiffness_z', text='Stiffness', slider=True)
    sub.active = context.active_pose_bone.lock_ik_z is False and active

    split = layout.split(percentage=0.25)
    sub = split.row()

    sub.prop(context.active_pose_bone, 'use_ik_limit_z', text='Limit')
    sub.active = context.active_pose_bone.lock_ik_z is False and active
    sub = split.row(align=True)
    sub.prop(context.active_pose_bone, 'ik_min_z', text='')
    sub.prop(context.active_pose_bone, 'ik_max_z', text='')
    sub.active = context.active_pose_bone.lock_ik_z is False and context.active_pose_bone.use_ik_limit_z and active

    split = layout.split(percentage=0.25)
    split.label(text='Stretch:')
    sub = split.row()
    sub.prop(context.active_pose_bone, 'ik_stretch', text='', slider=True)
    sub.active = active

    if context.active_object.pose.ik_solver == 'ITASC':
      split = layout.split()
      column = split.column()
      column.prop(context.active_pose_bone, 'use_ik_rotation_control', text='Control Rotation')
      column.active = active
      column = split.column()
      column.prop(context.active_pose_bone, 'ik_rotation_weight', text='Weight', slider=True)
      column.active = active
    layout.separator()



  layout.prop(context.active_bone, 'use_deform', text='Deform:')

  column = layout.column()
  column.active = context.active_bone.use_deform

  split = column.split()

  column = split.column()
  column.label(text='Envelope:')

  sub = column.column(align=True)
  sub.prop(context.active_bone, 'envelope_distance', text='Distance')
  sub.prop(context.active_bone, 'envelope_weight', text='Weight')
  column.prop(context.active_bone, 'use_envelope_multiply', text='Multiply')

  sub = column.column(align=True)
  sub.label(text='Radius:')
  sub.prop(context.active_bone, 'head_radius', text='Head')
  sub.prop(context.active_bone, 'tail_radius', text='Tail')

  column = split.column()
  column.label(text='Curved Bones:')

  sub = column.column(align=True)
  sub.prop(context.active_bone, 'bbone_segments', text='Segments')
  sub.prop(context.active_bone, 'bbone_in', text='Ease In')
  sub.prop(context.active_bone, 'bbone_out', text='Ease Out')
