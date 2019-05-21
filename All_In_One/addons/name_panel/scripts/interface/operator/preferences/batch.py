
# imports
import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

# operator
class operator(Operator):
    '''
        Default settings for the batch name operator.
    '''
    bl_idname = 'wm.batch_name_defaults'
    bl_label = 'Batch Name Defaults'
    bl_description = 'Current settings used for the batch name operator.'
    bl_options = {'INTERNAL'}

    # quick batch
    quickBatch = BoolProperty(
        name = 'Quick Batch',
        description = 'Quickly batch name datablocks visible in the name panel.',
        default = False
    )

    # check
    def check(self, context):
        return True

    # draw
    def draw(self, context):
        '''
            Operator body.
        '''

        from ..batch import operator
        operator.draw(self, context)

    # execute
    def execute(self, context):
        '''
            Execute the operator.
        '''

        return {'FINISHED'}

    # invoke
    def invoke(self, context, event):
        '''
            Invoke the operator panel/menu, control its width.
        '''
        size = 330 if not context.window_manager.BatchShared.largePopups else 460
        context.window_manager.invoke_props_dialog(self, width=size)
        return {'RUNNING_MODAL'}
