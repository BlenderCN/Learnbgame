import bpy


def search_stack(input_string):
    '''
    opens a browser with the search term, if can access 
    stack overflow.
    '''
    try:
        import webbrowser
        search_string = 'http://stackoverflow.com/search?q={}'
        input_string = input_string.replace(' ', '+')
        webbrowser.open(search_string.format(input_string))
    except:
        print('unable to locate stachoverflow')
        


class TextSearchStackOverflow(bpy.types.Operator):
    bl_label = ""
    bl_idname = "txt.search_stack"
    
    def execute(self, context):
        bpy.ops.text.copy()
        search_stack(context.window_manager.clipboard)
        return {'FINISHED'}

