import bpy

from bpy.types import Panel

from ... utility import addon


class BC_PT_help_start_operation(Panel):
    bl_label = 'Start Operation'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.workspace'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'BC_PT_help'


    def draw(self, context):
        layout = self.layout

        bc = context.window_manager.bc

        row = layout.row()
        row.alignment = 'RIGHT'
        row.prop(bc, 'start_operation', text='', expand=True, icon_only=True)

        layout.label(text='Use this option to begin the operation')
        layout.label(text='with modifiers')
