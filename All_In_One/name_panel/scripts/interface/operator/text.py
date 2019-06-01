
# imports
import bpy
from bpy.types import Operator
from ...text import cheatsheet

# generate cheatsheet
class generate(Operator):
    '''
        Generate regular expression cheatsheet.
    '''
    bl_idname = 'wm.regular_expression_cheatsheet'
    bl_label = 'Create Cheatsheet'
    bl_description = 'Create a text reference for regular expressions.'
    bl_options = {'UNDO', 'INTERNAL'}

    # execute
    def execute(self, context):
        '''
            Execute the operator.
        '''

        # cheatsheet
        if not 'Regular Expressions Cheatsheet' in bpy.data.texts:

            # write
            bpy.data.texts.new('Regular Expressions Cheatsheet').write(cheatsheet)

            # place cursor
            bpy.data.texts['Regular Expressions Cheatsheet'].current_line_index = 0

            # info messege
            self.report({'INFO'}, 'See \'Regular Expressions Cheatsheet\' in text editor')
        return {'FINISHED'}
