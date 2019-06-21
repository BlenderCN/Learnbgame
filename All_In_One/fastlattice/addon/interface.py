import bpy

def operator(operator, context):

    layout = operator.layout

    object = context.object if 'fast-lattice' in context.object else None

    if object:

        row = layout.row()
        row.prop(context.object.data, 'points_u')
        row.prop(context.object.data, 'interpolation_type_u', text='')

        row = layout.row()
        row.prop(context.object.data, 'points_v')
        row.prop(context.object.data, 'interpolation_type_v', text='')

        row = layout.row()
        row.prop(context.object.data, 'points_w')
        row.prop(context.object.data, 'interpolation_type_w', text='')

        row = layout.row()
        row.prop(context.object.data, 'use_outside')

        row = layout.row()
        row.label(text='Display:')

        row = layout.row()
        row.prop(operator, 'show_wire')
        row.prop(operator, 'show_all_edges')


def panel_start(panel, context):

    layout = panel.layout

    column = layout.column(align=True)

    column.label(text='Fast Lattice:')
    column.prop(context.window_manager.fast_lattice, 'method', text='')
    column.prop(context.window_manager.fast_lattice, 'interpolation_type', text='')
    column.prop(context.window_manager.fast_lattice, 'accuracy', slider=True)

    column.operator('object.fast_lattice')


def panel_finish(panel, context):

    layout = panel.layout

    if 'fast-lattice' in context.object:

        column = layout.column(align=True)

        column.label(text='Fast Lattice:')
        column.operator('object.fast_lattice_cleanup')
