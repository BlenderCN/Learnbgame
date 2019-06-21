def operator(operator, context):

    layout = operator.layout

    column = layout.column(align=True)

    column.label(text='General:')
    column.prop(operator, 'amount')
    column.prop(operator, 'width')
    column.prop(operator, 'height')

    row = column.row(align=True)
    row.prop(operator, 'depth')
    row.prop(operator, 'uniform', text='', icon='ALIGN')

    column.label(text='Length X:')
    row = column.row(align=True)
    row.prop(operator, 'length_x_min', text='Min')
    row.prop(operator, 'length_x_max', text='Max')

    column.label(text='Length Y:')
    row = column.row(align=True)
    row.prop(operator, 'length_y_min', text='Min')
    row.prop(operator, 'length_y_max', text='Max')

    column.label(text='Thickness:')
    row = column.row(align=True)
    row.prop(operator, 'thickness_min', text='Min')
    row.prop(operator, 'thickness_max', text='Max')

    column.label(text='Details:')
    column.prop(operator, 'straight')
    # column.prop(operator, 'decoration')
    column.prop(operator, 'split')
    column.prop(operator, 'bevel')
    column.prop(operator, 'bevel_size')

    column.label(text='Resolution:')
    column.prop(operator, 'surface')

    column.label(text='Misc:')
    column.prop(operator, 'seed')

    # column.prop(operator, 'convert')

    row = column.row()
    column = row.column()
    column.active = False if operator.convert else True
    column.prop(operator, 'create_empty')

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space_data = space

    column.prop(space_data, 'show_relationship_lines')
    # column.prop(operator, 'tile')


def menu_entry(menu, context):

    if context.mode == 'OBJECT':

        layout = menu.layout

        layout.separator()

        layout.operator('object.pipe_nightmare', text='Pipes', icon='IPO')
