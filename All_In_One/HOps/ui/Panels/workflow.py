import bpy
from bpy.types import Panel

from ... preferences import get_preferences

class HOPS_PT_workflow(Panel):
    bl_label = 'Workflow'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences()

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(preference, 'workflow', expand=True)

        row = column.row(align=True).split(factor=0.1, align=True)
        row.prop(preference, 'add_weighten_normals_mod', toggle=True)

        sub = row.row(align=True)
        sub.prop(preference, 'workflow_mode', expand=True)

        column.separator()

        row = column.row(align=True)
        row.prop(preference, 'sort_modifiers', text='sort modifiers', expand=True)

        sub = row.row(align=True)
        sub.alignment = 'RIGHT'

        if get_preferences().sort_bevel:
            sub.prop(get_preferences(), 'sort_bevel_last', text='', icon='SORT_ASC')
            sub.separator()
        sub.prop(preference, 'sort_bevel', text='', icon='MOD_BEVEL')
        sub.prop(preference, 'sort_array', text='', icon='MOD_ARRAY')
        sub.prop(preference, 'sort_mirror', text='', icon='MOD_MIRROR')
        sub.prop(preference, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
        sub.prop(preference, 'sort_simple_deform', text='', icon='MOD_SIMPLEDEFORM')
        sub.prop(preference, 'sort_triangulate', text='', icon='MOD_TRIANGULATE')

        column.separator()
