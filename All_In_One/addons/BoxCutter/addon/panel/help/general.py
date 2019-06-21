import bpy

from bpy.types import Panel

from ... utility import addon


# TODO: ctrl, alt, shift modifier key bahavior states
class BC_PT_help_general(Panel):
    bl_label = 'Help'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.workspace'
    bl_options = {'HIDE_HEADER'}
    bl_parent_id = 'BC_PT_help'


    def draw(self, context):
        layout = self.layout

        bc = context.window_manager.bc

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

        if not bc.running:
            layout.label(text='Hold LMB + Drag to draw a shape')

        else:
            if option.operation == 'NONE' or option.operation == 'EXTRUDE' and not option.modified:
                layout.label(text='LMB - Confirm')
                layout.label(text='RMB - Cancel')

            elif option.operation == 'DRAW':
                layout.label(text='LMB Release - Extrude')
                layout.label(text='RMB - Cancel')

            elif option.operation != 'NONE':
                layout.label(text='LMB - Lock')
                layout.label(text='RMB - Cancel')

            elif option.operation == 'DRAW' and option.shape_type == 'NGON':
                layout.label(text='LMB - Place Point')
                layout.label(text='RMB - Remove Point')

            layout.label(text='Alt + Scroll - Cycle Cutters')

            if option.shape_type == 'NGON':

                layout.label(text='CTRL - Angle Snapping')

            layout.separator()
            layout.label(text='Tilde - Rotate 90 Fitted')
            layout.label(text='TAB - Lock Shape')
            layout.label(text='E - Extrude')
            layout.label(text='O - Offset')

            layout.separator()
            layout.label(text='H - Toggle Wires Only')

            layout.separator()
            layout.label(text='X - Slice')
            layout.label(text='Z - Inset')
            layout.label(text='J - Join')
            layout.label(text='K - Knife')
            layout.label(text='A - Make')

            layout.label(text=F'V - {"Array" if not option.operation == "ARRAY" else "Clear Array"}')
            layout.label(text=F'T - {"Solidify" if not option.operation == "SOLIDIFY" else "Clear Solidify"}')
            layout.label(text=F'B - {"Bevel" if not option.operation == "BEVEL" else "Clear Bevel"}')
            layout.label(text='Q - Contour Bevel')

            layout.separator()
            layout.label(text='. - Change origin')
            layout.label(text='1, 2, 3 - Mirror (X, Y, Z)')

        layout.separator()
        layout.label(text='D - Pie Menu')
        layout.label(text='Ctrl + D - Behavior Helper')
