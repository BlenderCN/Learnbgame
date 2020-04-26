
# object
def Object(self, context, layout, datablock):
    '''
        Object buttons.
    '''

    layout.template_ID(context.scene.objects, 'active')

    layout.label('Relations:')

    split = layout.split()

    column = split.column()
    column.prop(datablock, 'layers')
    column.separator()
    column.prop(datablock, 'pass_index')

    column = split.column()
    column.label(text='Parent:')
    column.prop(datablock, 'parent', text='')

    sub = column.column()
    sub.prop(datablock, 'parent_type', text='')
    parent = datablock.parent
    if parent and datablock.parent_type == 'BONE' and parent.type == 'ARMATURE':
        sub.prop_search(datablock, 'parent_bone', parent.data, 'bones', text='')
    sub.active = (parent is not None)
    layout.separator()


    layout.label('Display:')

    split = layout.split()

    column = split.column()
    column.prop(datablock, 'show_name', text='Name')
    column.prop(datablock, 'show_axis', text='Axis')
    # Makes no sense for cameras, armatures, etc.!
    # but these settings do apply to dupli instances
    if datablock.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'} or datablock.dupli_type != 'NONE':
        column.prop(datablock, 'show_wire', text='Wire')
    if datablock.type == 'MESH' or datablock.dupli_type != 'NONE':
        column.prop(datablock, 'show_all_edges')

    column = split.column()
    row = column.row()
    row.prop(datablock, 'show_bounds', text='Bounds')
    sub = row.row()
    sub.active = datablock.show_bounds
    sub.prop(datablock, 'draw_bounds_type', text='')

    if datablock.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
        column.prop(datablock, 'show_texture_space', text='Texture Space')
    column.prop(datablock, 'show_x_ray', text='X-Ray')
    if datablock.type == 'MESH' or (datablock.type == 'EMPTY' and datablock.empty_draw_type == 'IMAGE'):
        column.prop(datablock, 'show_transparent', text='Transparency')

    split = layout.split()

    column = split.column()
    if datablock.type in {'CAMERA', 'EMPTY'}:
        # wire objects only use the max. draw type for duplis
        column.active = datablock.dupli_type != 'NONE'
        column.label(text='Maximum Dupli Draw Type:')
    else:
            column.label(text='Maximum Draw Type:')
    column.prop(datablock, 'draw_type', text='')

    column = split.column()
    if (datablock.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}) or (datablock.type == 'EMPTY' and datablock.empty_draw_type == 'IMAGE'):
        # Only useful with object having faces/materials...
        column.label(text='Object Color:')
        column.prop(datablock, 'color', text='')

    layout.separator()


    layout.label('Duplication:')

    layout.prop(datablock, 'dupli_type', expand=True)

    if datablock.dupli_type == 'FRAMES':
            split = layout.split()

            column = split.column(align=True)
            column.prop(datablock, 'dupli_frames_start', text='Start')
            column.prop(datablock, 'dupli_frames_end', text='End')

            column = split.column(align=True)
            column.prop(datablock, 'dupli_frames_on', text='On')
            column.prop(datablock, 'dupli_frames_off', text='Off')

            layout.prop(datablock, 'use_dupli_frames_speed', text='Speed')

    elif datablock.dupli_type == 'VERTS':
            layout.prop(datablock, 'use_dupli_vertices_rotation', text='Rotation')

    elif datablock.dupli_type == 'FACES':
            row = layout.row()
            row.prop(datablock, 'use_dupli_faces_scale', text='Scale')
            sub = row.row()
            sub.active = datablock.use_dupli_faces_scale
            sub.prop(datablock, 'dupli_faces_scale', text='Inherit Scale')

    elif datablock.dupli_type == 'GROUP':
            layout.prop(datablock, 'dupli_group', text='Group')

    layout.separator()


    layout.label('Relations Extras:')

    split = layout.split()

    if context.scene.render.engine != 'BLENDER_GAME':
        column = split.column()
        column.label(text='Tracking Axes:')
        column.prop(datablock, 'track_axis', text='Axis')
        column.prop(datablock, 'up_axis', text='Up Axis')

    column = split.column()
    column.prop(datablock, 'use_slow_parent')
    row = column.row()
    row.active = ((datablock.parent is not None) and (datablock.use_slow_parent))
    row.prop(datablock, 'slow_parent_offset', text='Offset')

    layout.prop(datablock, 'use_extra_recalc_object')
    layout.prop(datablock, 'use_extra_recalc_data')

    layout.separator()
