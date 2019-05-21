
# imports
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from ...function import options

# reset
class reset(Operator):
    '''
        Reset option values.
    '''
    bl_idname = 'wm.reset_name_panel_settings'
    bl_label = 'Reset Settings'
    bl_description = 'Reset settings to the default values.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # panel
    panel = BoolProperty(
        name = 'Name Panel',
        description = 'Reset the setting values for the name panel.',
        default = False
    )

    # auto
    auto = BoolProperty(
        name = 'Auto Name',
        description = 'Reset the setting values for batch auto name.',
        default = True
    )

    # names
    names = BoolProperty(
        name = 'Auto Name \N{Rightwards Arrow} Names',
        description = 'Reset the setting values for batch auto name \N{Rightwards Arrow} name settings.',
        default = False
    )

    # name
    name = BoolProperty(
        name = 'Batch Name',
        description = 'Reset the setting values for batch name.',
        default = True
    )

    # copy
    copy = BoolProperty(
        name = 'Batch Name Copy',
        description = 'Reset the setting values for batch name copy.',
        default = True
    )

    # draw
    def draw(self, context):
        '''
            Draw the operator panel/menu.
        '''

        # layout
        layout = self.layout

        # column
        column = layout.column()

        # options
        column.prop(self, 'panel')
        column.prop(self, 'auto')
        column.prop(self, 'names')
        column.prop(self, 'name')
        column.prop(self, 'copy')

    # execute
    def execute(self, context):
        '''
            Execute the operator.
        '''

        # reset
        options.reset(context, self.panel, self.auto, self.names, self.name, self.copy)
        return {'FINISHED'}
