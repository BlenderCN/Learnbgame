import bpy


def search_blenderscripting(input_string):
    '''
    opens a browser with the search term, if can access 
    blenderscripting blogspot.
    '''
    try:
        import webbrowser
        search_string = 'http://blenderscripting.blogspot.com/search?q={}'
        webbrowser.open(search_string.format(input_string))
    except:
        print('unable to locate blenderscripting.blogspot.com')
        


class TextSearchBlenderScripting(bpy.types.Operator):
    bl_label = ""
    bl_idname = "txt.search_blenderscripting"
    
    def execute(self, context):
        bpy.ops.text.copy()
        search_blenderscripting(context.window_manager.clipboard)
        return {'FINISHED'}

