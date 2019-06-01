
# imports
import bpy

# object data
def ObjectData(self, context, layout, datablock):
  '''
    Object data buttons.
  '''

  if datablock.type != 'EMPTY':

    # template id
    layout.template_ID(datablock, 'data')

  else:

    if datablock.empty_draw_type == 'IMAGE':

      layout.template_ID(datablock, 'data', open='image.open', unlink='object.unlink_data')


  # armature
  if datablock.type == 'ARMATURE':


    layout.label(text='Skeleton:')

    layout.prop(datablock.data, 'pose_position', expand=True)

    column = layout.column()
    column.label(text='Layers:')
    column.prop(datablock.data, 'layers', text='')
    column.label(text='Protected Layers:')
    column.prop(datablock.data, 'layers_protected', text='')

    if context.scene.render.engine == 'BLENDER_GAME':
      column = layout.column()
      column.label(text='Deform:')
      column.prop(datablock.data, 'deform_method', expand=True)
    layout.separator()


    layout.label('Display:')

    layout = self.layout

    layout.prop(datablock.data, 'draw_type', expand=True)

    split = layout.split()

    column = split.column()
    column.prop(datablock.data, 'show_names', text='Names')
    column.prop(datablock.data, 'show_axes', text='Axes')
    column.prop(datablock.data, 'show_bone_custom_shapes', text='Shapes')

    column = split.column()
    column.prop(datablock.data, 'show_group_colors', text='Colors')
    column.prop(datablock, 'show_x_ray', text='X-Ray')
    column.prop(datablock.data, 'use_deform_delay', text='Delay Refresh')

    if datablock.pose:

      layout.separator()

      layout.label('Inverse Kinematics:')

      layout.prop(datablock.pose, 'ik_solver')

      if datablock.pose.ik_param:

        layout.prop(datablock.pose.ik_param, 'mode', expand=True)

        if datablock.pose.ik_param.mode == 'SIMULATION':
          layout.label(text='Reiteration:')
          layout.prop(datablock.pose.ik_param, 'reiteration_method', expand=True)

        row = layout.row()
        row.active = not datablock.pose.ik_param.mode == 'SIMULATION' or datablock.pose.ik_param.reiteration_method != 'NEVER'
        row.prop(datablock.pose.ik_param, 'precision')
        row.prop(datablock.pose.ik_param, 'iterations')

        if datablock.pose.ik_param.mode == 'SIMULATION':
          layout.prop(datablock.pose.ik_param, 'use_auto_step')
          row = layout.row()
          if datablock.pose.ik_param.use_auto_step:
            row.prop(datablock.pose.ik_param, 'step_min', text='Min')
            row.prop(datablock.pose.ik_param, 'step_max', text='Max')
          else:
            row.prop(datablock.pose.ik_param, 'step_count')

        layout.prop(datablock.pose.ik_param, 'solver')
        if datablock.pose.ik_param.mode == 'SIMULATION':
          layout.prop(datablock.pose.ik_param, 'feedback')
          layout.prop(datablock.pose.ik_param, 'velocity_max')
        if datablock.pose.ik_param.solver == 'DLS':
          row = layout.row()
          row.prop(datablock.pose.ik_param, 'damping_max', text='Damp', slider=True)
          row.prop(datablock.pose.ik_param, 'damping_epsilon', text='Eps', slider=True)

  # curve
  if datablock.type in {'CURVE', 'SURFACE', 'FONT'}:

    # label
    layout.label(text='Shape:')

    if datablock.type == 'CURVE':
      row = layout.row()
      row.prop(datablock.data, 'dimensions', expand=True)

    split = layout.split()

    column = split.column()
    column.label(text='Resolution:')
    sub = column.column(align=True)
    sub.prop(datablock.data, 'resolution_u', text='Preview U')
    sub.prop(datablock.data, 'render_resolution_u', text='Render U')
    if datablock.type == 'CURVE':
      column.label(text='Twisting:')
      column.prop(datablock.data, 'twist_mode', text='')
      column.prop(datablock.data, 'twist_smooth', text='Smooth')
    elif datablock.type == 'FONT':
      column.label(text='Display:')
      column.prop(datablock.data, 'use_fast_edit', text='Fast Editing')

    column = split.column()

    if datablock.type == 'SURFACE':
      sub = column.column()
      sub.label(text='')
      sub = column.column(align=True)
      sub.prop(datablock.data, 'resolution_v', text='Preview V')
      sub.prop(datablock.data, 'render_resolution_v', text='Render V')

    if datablock.type in {'CURVE', 'FONT'}:
      column.label(text='Fill:')
      sub = column.column()
      sub.active = (datablock.data.dimensions == '2D' or (datablock.data.bevel_object is None and datablock.data.dimensions == '3D'))
      sub.prop(datablock.data, 'fill_mode', text='')
      column.prop(datablock.data, 'use_fill_deform')

    if datablock.type == 'CURVE':
      column.label(text='Path / Curve-Deform:')
      sub = column.column()
      subsub = sub.row()
      subsub.prop(datablock.data, 'use_radius')
      subsub.prop(datablock.data, 'use_stretch')
      sub.prop(datablock.data, 'use_deform_bounds')
    layout.separator()

    layout.label(text='Texture Space')
    row = layout.row()
    row.prop(datablock.data, 'use_auto_texspace')
    row.prop(datablock.data, 'use_uv_as_generated')

    row = layout.row()
    row.column().prop(datablock.data, 'texspace_location', text='Location')
    row.column().prop(datablock.data, 'texspace_size', text='Size')

    layout.operator('curve.match_texture_space')
    layout.separator()

    # isnt surface
    if datablock.type != 'SURFACE':

      layout.label(text='Geometry:')

      split = layout.split()

      column = split.column()
      column.label(text='Modification:')
      column.prop(datablock.data, 'offset')
      column.prop(datablock.data, 'extrude')
      column.label(text='Taper Object:')
      column.prop(datablock.data, 'taper_object', text='')

      column = split.column()
      column.label(text='Bevel:')
      column.prop(datablock.data, 'bevel_depth', text='Depth')
      column.prop(datablock.data, 'bevel_resolution', text='Resolution')
      column.label(text='Bevel Object:')
      column.prop(datablock.data, 'bevel_object', text='')

      if datablock.type != 'FONT':
        column = layout.column(align=True)
        row = column.row()
        row.label(text='Bevel Factor:')

        column = layout.column()
        column.active = (
          (datablock.data.bevel_depth > 0.0) or
          (datablock.data.extrude > 0.0) or
          (datablock.data.bevel_object is not None)
        )
        row = column.row(align=True)
        row.prop(datablock.data, 'bevel_factor_mapping_start', text='')
        row.prop(datablock.data, 'bevel_factor_start', text='Start')
        row = column.row(align=True)
        row.prop(datablock.data, 'bevel_factor_mapping_end', text='')
        row.prop(datablock.data, 'bevel_factor_end', text='End')

        row = layout.row()
        sub = row.row()
        sub.active = datablock.data.taper_object is not None
        sub.prop(datablock.data, 'use_map_taper')
        sub = row.row()
        sub.active = datablock.data.bevel_object is not None
        sub.prop(datablock.data, 'use_fill_caps')
      layout.separator()

    # is curve
    if datablock.type == 'CURVE':

      layout.prop(datablock.data, 'use_path', text='Path Animation:')

      column = layout.column()
      column.active = datablock.data.use_path
      column.prop(datablock.data, 'path_duration', text='Frames')
      column.prop(datablock.data, 'eval_time')

      # these are for paths only
      row = column.row()
      row.prop(datablock.data, 'use_path_follow')
      layout.separator()


    # isnt font and datablock.data.splines.active
    if datablock.type != 'FONT' and datablock.data.splines.active:

      layout.label(text='Active Spline:')
      split = layout.split()

      if datablock.data.splines.active.type == 'POLY':
        # These settings are below but its easier to have
        # polys set aside since they use so few settings
        row = layout.row()
        row.label(text='Cyclic:')
        row.prop(datablock.data.splines.active, 'use_cyclic_u', text='U')

        layout.prop(datablock.data.splines.active, 'use_smooth')
      else:
        column = split.column()
        column.label(text='Cyclic:')
        if datablock.data.splines.active.type == 'NURBS':
          column.label(text='Bezier:')
          column.label(text='Endpoint:')
          column.label(text='Order:')

        column.label(text='Resolution:')

        column = split.column()
        column.prop(datablock.data.splines.active, 'use_cyclic_u', text='U')

        if datablock.data.splines.active.type == 'NURBS':
          sub = column.column()
          # sub.active = (not datablock.data.splines.active.use_cyclic_u)
          sub.prop(datablock.data.splines.active, 'use_bezier_u', text='U')
          sub.prop(datablock.data.splines.active, 'use_endpoint_u', text='U')

          sub = column.column()
          sub.prop(datablock.data.splines.active, 'order_u', text='U')
        column.prop(datablock.data.splines.active, 'resolution_u', text='U')

        if datablock.type == 'SURFACE':
          column = split.column()
          column.prop(datablock.data.splines.active, 'use_cyclic_v', text='V')

          # its a surface, assume its a nurbs
          sub = column.column()
          sub.active = (not datablock.data.splines.active.use_cyclic_v)
          sub.prop(datablock.data.splines.active, 'use_bezier_v', text='V')
          sub.prop(datablock.data.splines.active, 'use_endpoint_v', text='V')
          sub = column.column()
          sub.prop(datablock.data.splines.active, 'order_v', text='V')
          sub.prop(datablock.data.splines.active, 'resolution_v', text='V')

        if datablock.data.splines.active.type == 'BEZIER':
          column = layout.column()
          column.label(text='Interpolation:')

          sub = column.column()
          sub.active = (datablock.data.dimensions == '3D')
          sub.prop(datablock.data.splines.active, 'tilt_interpolation', text='Tilt')

          column.prop(datablock.data.splines.active, 'radius_interpolation', text='Radius')

        layout.prop(datablock.data.splines.active, 'use_smooth')
      layout.separator()


    # is font
    if datablock.type == 'FONT':


      layout.label(text='Font:')
      row = layout.split(percentage=0.25)
      row.label(text='Regular')
      row.template_ID(datablock.data, 'font', open='font.open', unlink='font.unlink')
      row = layout.split(percentage=0.25)
      row.label(text='Bold')
      row.template_ID(datablock.data, 'font_bold', open='font.open', unlink='font.unlink')
      row = layout.split(percentage=0.25)
      row.label(text='Italic')
      row.template_ID(datablock.data, 'font_italic', open='font.open', unlink='font.unlink')
      row = layout.split(percentage=0.25)
      row.label(text='Bold & Italic')
      row.template_ID(datablock.data, 'font_bold_italic', open='font.open', unlink='font.unlink')

      split = layout.split()

      column = split.column()
      column.prop(datablock.data, 'size', text='Size')
      column = split.column()
      column.prop(datablock.data, 'shear')

      split = layout.split()

      column = split.column()
      column.label(text='Object Font:')
      column.prop(datablock.data, 'family', text='')

      column = split.column()
      column.label(text='Text on Curve:')
      column.prop(datablock.data, 'follow_curve', text='')

      split = layout.split()

      column = split.column()
      sub = column.column(align=True)
      sub.label(text='Underline:')
      sub.prop(datablock.data, 'underline_position', text='Position')
      sub.prop(datablock.data, 'underline_height', text='Thickness')

      column = split.column()
      column.label(text='datablock.data.edit_formatacter:')
      column.prop(datablock.data.edit_format, 'use_bold')
      column.prop(datablock.data.edit_format, 'use_italic')
      column.prop(datablock.data.edit_format, 'use_underline')

      row = layout.row()
      row.prop(datablock.data, 'small_caps_scale', text='Small Caps')
      row.prop(datablock.data.edit_format, 'use_small_caps')
      layout.separator()


      layout.label(text='Paragraph:')

      layout.label(text='Align:')
      layout.prop(datablock.data, 'align', expand=True)

      split = layout.split()

      column = split.column(align=True)
      column.label(text='Spacing:')
      column.prop(datablock.data, 'space_character', text='Letter')
      column.prop(datablock.data, 'space_word', text='Word')
      column.prop(datablock.data, 'space_line', text='Line')

      column = split.column(align=True)
      column.label(text='Offset:')
      column.prop(datablock.data, 'offset_x', text='X')
      column.prop(datablock.data, 'offset_y', text='Y')
      layout.separator()


      layout.label(text='Text Boxes:')

      split = layout.split()
      column = split.column()
      column.operator('font.textbox_add', icon='ZOOMIN')
      column = split.column()

      for i, tbox in enumerate(datablock.data.text_boxes):

        box = layout.box()

        row = box.row()

        split = row.split()

        column = split.column(align=True)

        column.label(text='Dimensions:')
        column.prop(tbox, 'width', text='Width')
        column.prop(tbox, 'height', text='Height')

        column = split.column(align=True)

        column.label(text='Offset:')
        column.prop(tbox, 'x', text='X')
        column.prop(tbox, 'y', text='Y')

        row.operator('font.textbox_remove', text='', icon='X', emboss=False).index = i


  # camera
  if datablock.type == 'CAMERA':

    layout.label(text='Lens:')

    cam = datablock.data

    layout.prop(cam, 'type', expand=True)

    split = layout.split()

    column = split.column()
    if cam.type == 'PERSP':
      row = column.row()
      if cam.lens_unit == 'MILLIMETERS':
        row.prop(cam, 'lens')
      elif cam.lens_unit == 'FOV':
        row.prop(cam, 'angle')
      row.prop(cam, 'lens_unit', text='')

    elif cam.type == 'ORTHO':
      column.prop(cam, 'ortho_scale')

    elif cam.type == 'PANO':
      engine = context.scene.render.engine
      if engine == 'CYCLES':
        ccam = cam.cycles
        column.prop(ccam, 'panorama_type', text='Type')
        if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
          column.prop(ccam, 'fisheye_fov')
        elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
          row = layout.row()
          row.prop(ccam, 'fisheye_lens', text='Lens')
          row.prop(ccam, 'fisheye_fov')
        elif ccam.panorama_type == 'EQUIRECTANGULAR':
          row = layout.row()
          sub = row.column(align=True)
          sub.prop(ccam, 'latitude_min')
          sub.prop(ccam, 'latitude_max')
          sub = row.column(align=True)
          sub.prop(ccam, 'longitude_min')
          sub.prop(ccam, 'longitude_max')
      elif engine == 'BLENDER_RENDER':
        row = column.row()
        if cam.lens_unit == 'MILLIMETERS':
          row.prop(cam, 'lens')
        elif cam.lens_unit == 'FOV':
          row.prop(cam, 'angle')
        row.prop(cam, 'lens_unit', text='')

    split = layout.split()

    column = split.column(align=True)
    column.label(text='Shift:')
    column.prop(cam, 'shift_x', text='X')
    column.prop(cam, 'shift_y', text='Y')

    column = split.column(align=True)
    column.label(text='Clipping:')
    column.prop(cam, 'clip_start', text='Start')
    column.prop(cam, 'clip_end', text='End')

    layout.separator()


    if context.scene.render.use_multiview and context.scene.render.views_format == 'STEREO_3D':

      layout.label(text='Stereoscopy:')
      st = datablock.data.stereo

      column = layout.column()
      column.row().prop(st, 'convergence_mode', expand=True)

      sub = column.column()
      sub.active = st.convergence_mode != 'PARALLEL'
      sub.prop(st, 'convergence_distance')

      column.prop(st, 'interocular_distance')

      column.label(text='Pivot:')
      column.row().prop(st, 'pivot', expand=True)

      layout.separator()


    layout.label(text='Camera:')

    cam = datablock.data

    row = layout.row(align=True)

    row.menu('CAMERA_MT_presets', text=bpy.types.CAMERA_MT_presets.bl_label)
    row.operator('camera.preset_add', text='', icon='ZOOMIN')
    row.operator('camera.preset_add', text='', icon='ZOOMOUT').remove_active = True

    layout.label(text='Sensor:')

    split = layout.split()

    column = split.column(align=True)
    if cam.sensor_fit == 'AUTO':
      column.prop(cam, 'sensor_width', text='Size')
    else:
      sub = column.column(align=True)
      sub.active = cam.sensor_fit == 'HORIZONTAL'
      sub.prop(cam, 'sensor_width', text='Width')
      sub = column.column(align=True)
      sub.active = cam.sensor_fit == 'VERTICAL'
      sub.prop(cam, 'sensor_height', text='Height')

    column = split.column(align=True)
    column.prop(cam, 'sensor_fit', text='')

  # empty
  if datablock.type == 'EMPTY':

    layout.label(text='Empty:')

    layout.prop(datablock, 'empty_draw_type', text='Display')

    if datablock.empty_draw_type == 'IMAGE':
      layout.template_image(datablock, 'data', datablock.image_user, compact=True)

      row = layout.row(align=True)
      row = layout.row(align=True)

      layout.prop(datablock, 'color', text='Transparency', index=3, slider=True)
      row = layout.row(align=True)
      row.prop(datablock, 'empty_image_offset', text='Offset X', index=0)
      row.prop(datablock, 'empty_image_offset', text='Offset Y', index=1)

    layout.prop(datablock, 'empty_draw_size', text='Size')


  # lattice
  if datablock.type == 'LATTICE':

    layout.label(text='Lattice:')

    lat = datablock.data

    row = layout.row()
    row.prop(lat, 'points_u')
    row.prop(lat, 'interpolation_type_u', text='')

    row = layout.row()
    row.prop(lat, 'points_v')
    row.prop(lat, 'interpolation_type_v', text='')

    row = layout.row()
    row.prop(lat, 'points_w')
    row.prop(lat, 'interpolation_type_w', text='')

    row = layout.row()
    row.prop(lat, 'use_outside')
    row.prop_search(lat, 'vertex_group', context.object, 'vertex_groups', text='')


  # mball
  if datablock.type == 'META':
    layout.label(text='Metaball:')

    mball = datablock.data

    split = layout.split()

    column = split.column()
    column.label(text='Resolution:')
    sub = column.column(align=True)
    sub.prop(mball, 'resolution', text='View')
    sub.prop(mball, 'render_resolution', text='Render')

    column = split.column()
    column.label(text='Settings:')
    column.prop(mball, 'threshold', text='Threshold')

    layout.label(text='Update:')
    layout.prop(mball, 'update_method', expand=True)


    layout.separator()
    layout.label(text='Texture Space:')

    mball = datablock.data

    layout.prop(mball, 'use_auto_texspace')

    row = layout.row()
    row.column().prop(mball, 'texspace_location', text='Location')
    row.column().prop(mball, 'texspace_size', text='Size')


    if datablock.data.elements.active:
      layout.separator()
      layout.label(text='Active Element:')

      metaelem = datablock.data.elements.active

      layout.prop(metaelem, 'type')

      split = layout.split()

      column = split.column(align=True)
      column.label(text='Settings:')
      column.prop(metaelem, 'stiffness', text='Stiffness')
      column.prop(metaelem, 'use_negative', text='Negative')
      column.prop(metaelem, 'hide', text='Hide')

      column = split.column(align=True)

      if metaelem.type in {'CUBE', 'ELLIPSOID'}:
        column.label(text='Size:')
        column.prop(metaelem, 'size_x', text='X')
        column.prop(metaelem, 'size_y', text='Y')
        column.prop(metaelem, 'size_z', text='Z')

      elif metaelem.type == 'TUBE':
        column.label(text='Size:')
        column.prop(metaelem, 'size_x', text='X')

      elif metaelem.type == 'PLANE':
        column.label(text='Size:')
        column.prop(metaelem, 'size_x', text='X')
        column.prop(metaelem, 'size_y', text='Y')

  # mesh
  if datablock.type == 'MESH':
    layout.label(text='Normals')

    mesh = datablock.data

    split = layout.split()

    column = split.column()
    column.prop(mesh, 'use_auto_smooth')
    sub = column.column()
    sub.active = mesh.use_auto_smooth and not mesh.has_custom_normals
    sub.prop(mesh, 'auto_smooth_angle', text='Angle')

    split.prop(mesh, 'show_double_sided')


    layout.separator()
    layout.label(text='Texture Space:')

    mesh = datablock.data

    layout.prop(mesh, 'texture_mesh')

    layout.separator()

    layout.prop(mesh, 'use_auto_texspace')
    row = layout.row()
    row.column().prop(mesh, 'texspace_location', text='Location')
    row.column().prop(mesh, 'texspace_size', text='Size')


    layout.separator()
    layout.label(text='Geometry Data:')
    obj = datablock
    me = datablock.data
    column = layout.column()

    column.operator('mesh.customdata_mask_clear', icon='X')
    column.operator('mesh.customdata_skin_clear', icon='X')

    if me.has_custom_normals:
      column.operator('mesh.customdata_custom_splitnormals_clear', icon='X')
    else:
      column.operator('mesh.customdata_custom_splitnormals_add', icon='ZOOMIN')

    column = layout.column()

    column.enabled = (obj.mode != 'EDIT')
    column.prop(me, 'use_customdata_vertex_bevel')
    column.prop(me, 'use_customdata_edge_bevel')
    column.prop(me, 'use_customdata_edge_crease')

  # speaker
  if datablock.type == 'SPEAKER':
    if context.scene.render.engine in {'CYCLES', 'BLENDER_RENDER'}:
      layout.label(text='Sound:')

      speaker = datablock.data

      split = layout.split(percentage=0.75)

      split.template_ID(speaker, 'sound', open='sound.open_mono')
      split.prop(speaker, 'muted')

      row = layout.row()
      row.prop(speaker, 'volume')
      row.prop(speaker, 'pitch')


      layout.separator()
      layout.label(text='Distance:')

      speaker = datablock.data

      split = layout.split()

      column = split.column()
      column.label('Volume:')
      column.prop(speaker, 'volume_min', text='Minimum')
      column.prop(speaker, 'volume_max', text='Maximum')
      column.prop(speaker, 'attenuation')

      column = split.column()
      column.label('Distance:')
      column.prop(speaker, 'distance_max', text='Maximum')
      column.prop(speaker, 'distance_reference', text='Reference')


      layout.separator()
      layout.label(text='Cone:')

      speaker = datablock.data

      split = layout.split()

      column = split.column()
      column.label('Angle:')
      column.prop(speaker, 'cone_angle_outer', text='Outer')
      column.prop(speaker, 'cone_angle_inner', text='Inner')

      column = split.column()
      column.label('Volume:')
      column.prop(speaker, 'cone_volume_outer', text='Outer')
