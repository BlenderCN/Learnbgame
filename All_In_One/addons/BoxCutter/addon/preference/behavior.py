import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty

from .. utility import names


class bc(PropertyGroup):

    quick_execute: BoolProperty(
        name = names['quick_execute'],
        description = 'Quickly execute cuts on release',
        default = False)

    parent_shape: BoolProperty(
        name = names['parent_shape'],
        description = 'Parent cutters to the target',
        default = False)

    autohide_shapes: BoolProperty(
        name = 'Auto Hide Shapes',
        description = 'Hide previously made unselected cutters on cut',
        default = True)

    apply_slices: BoolProperty(
        name = names['apply_slices'],
        description = 'Apply slice cuts on the slice objects',
        default = False)

    auto_smooth: BoolProperty(
        name = names['auto_smooth'],
        description = 'Auto smooth geometry when cutting into it',
        default = True)

    make_active: BoolProperty(
        name = names['make_active'],
        description = 'Make the shape active when holding shift to keep it',
        default = True)

    use_multi_edit: BoolProperty(
        name = names['use_multi_edit'],
        description = 'Bring created mesh objects into edit mode',
        default = True)

    simple_trace: BoolProperty(
        name = names['simple_trace'],
        description = 'Use simple bound cubes when ray tracing (Faster)',
        default = False)

    sort_modifiers: BoolProperty(
        name = names['sort_modifiers'],
        description = 'Sort modifier order',
        default = True)

    sort_bevel: BoolProperty(
        name = 'Sort Bevel',
        description = 'Ensure bevel modifiers are placed after any boolean modifiers created',
        default = True)

    sort_bevel_last: BoolProperty(
        name = 'Sort Bevel Last',
        description = 'Sort by only keeping the final bevel modifier last, ignoring all others',
        default = False)

    sort_weighted_normal: BoolProperty(
        name = 'Sort Weighted Normal',
        description = 'Ensure weighted normal modifiers are placed after any boolean modifiers created',
        default = True)

    sort_array: BoolProperty(
        name = 'Sort Array',
        description = 'Ensure array modifiers are placed after any boolean modifiers created',
        default = True)

    sort_mirror: BoolProperty(
        name = 'Sort Mirror',
        description = 'Ensure mirror modifiers are placed after any boolean modifiers created',
        default = True)

    sort_solidify: BoolProperty(
        name = 'Sort Soldify',
        description = 'Ensure solidify modifiers are placed after any boolean modifiers created',
        default = False)

    sort_triangulate: BoolProperty(
        name = 'Sort Triangulate',
        description = 'Ensure triangulate modifiers are placed after any boolean modifiers created',
        default = True)

    sort_simple_deform: BoolProperty(
        name = 'Sort Simple Deform',
        description = 'Ensure simple deform modifiers are placed after any boolean modifiers created',
        default = True)

    keep_modifiers: BoolProperty(
        name = names['keep_modifiers'],
        description = 'Choose what modifiers are applied on the shape',
        default = True)

    keep_bevel: BoolProperty(
        name = 'Keep Bevel',
        description = 'Keep shape bevel modifiers',
        default = True)

    keep_array: BoolProperty(
        name = 'Keep Array',
        description = 'Keep shape array modifier',
        default = True)

    keep_solidify: BoolProperty(
        name = 'Keep Soldify',
        description = 'Keep shape solidify modifier',
        default = True)

    keep_screw: BoolProperty(
        name = 'Keep Screw',
        description = 'Keep shape spin modifier',
        default = False)

    keep_mirror: BoolProperty(
        name = 'Keep Mirror',
        description = 'Keep shape mirror modifier',
        default = True)

    keep_lattice: BoolProperty(
        name = 'Keep Lattice',
        description = 'Keep shape lattice modifier',
        default = False)

    ngon_snap_angle: IntProperty(
        name = names['ngon_snap_angle'],
        description = 'Snap angle when using ngon',
        min = 1,
        soft_max = 45,
        max = 180,
        default = 15)

    snap: BoolProperty(
        name = 'Snap',
        description = 'Snap points when holding CTRL',
        default = False)

    snap_increment: BoolProperty(
        name = 'Snap Incremental',
        description = 'Snap to increments',
        default = False)

    increment_amount: FloatProperty(
        name = 'Increment Amount',
        description = 'Snap increment amount',
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.1)

    increment_lock: BoolProperty(
        name = 'Increment Lock',
        description = 'Snap increment without holding CTRL',
        default = False)

    snap_grid: BoolProperty(
        name = 'Snap Grid',
        description = 'Snap to world or cursor grid',
        default = False)

    snap_vert: BoolProperty(
        name = 'Snap Verts',
        description = 'Snap to verts',
        default = True)

    snap_edge: BoolProperty(
        name = 'Snap Edges',
        description = 'Snap to mid points of edges',
        default = True)

    snap_face: BoolProperty(
        name = 'Snap Face',
        description = 'Snap to face center',
        default = True)

    use_dpi_factor: BoolProperty(
        name = 'Use DPI Factor',
        description = ('Use DPI factoring when drawing and choosing dimensions.\n'
                       'Note: Having this enabled can cause behavior issues on some machines'),
        default = True)

def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.behavior, 'quick_execute', layout.row())
    label_row(preference.behavior, 'apply_slices', layout.row())
    label_row(preference.behavior, 'make_active', layout.row())
    label_row(preference.behavior, 'auto_smooth', layout.row())
    label_row(preference.behavior, 'parent_shape', layout.row())
    label_row(preference.behavior, 'use_multi_edit', layout.row())
    label_row(preference.behavior, 'simple_trace', layout.row())
    label_row(preference.behavior, 'sort_modifiers', layout.row())

    if preference.behavior.sort_modifiers:
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(preference.behavior, 'sort_bevel_last', text='', icon='SORT_ASC')
        row.separator()
        row.prop(preference.behavior, 'sort_bevel', text='', icon='MOD_BEVEL')
        row.prop(preference.behavior, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
        row.prop(preference.behavior, 'sort_array', text='', icon='MOD_ARRAY')
        row.prop(preference.behavior, 'sort_mirror', text='', icon='MOD_MIRROR')
        row.prop(preference.behavior, 'sort_solidify', text='', icon='MOD_SOLIDIFY')
        row.prop(preference.behavior, 'sort_simple_deform', text='', icon='MOD_SIMPLEDEFORM')
        row.prop(preference.behavior, 'sort_triangulate', text='', icon='MOD_TRIANGULATE')

    label_row(preference.behavior, 'keep_modifiers', layout.row())

    if preference.behavior.keep_modifiers:
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(preference.behavior, 'keep_bevel', text='', icon='MOD_BEVEL')
        row.prop(preference.behavior, 'keep_solidify', text='', icon='MOD_SOLIDIFY')
        row.prop(preference.behavior, 'keep_array', text='', icon='MOD_ARRAY')
        row.prop(preference.behavior, 'keep_mirror', text='', icon='MOD_MIRROR')
        row.prop(preference.behavior, 'keep_screw', text='', icon='MOD_SCREW')
        row.prop(preference.behavior, 'keep_lattice', text='', icon='MOD_LATTICE')

    layout.separator()

    label_row(preference.behavior, 'use_dpi_factor', layout.row(), label='Use DPI Factoring')
