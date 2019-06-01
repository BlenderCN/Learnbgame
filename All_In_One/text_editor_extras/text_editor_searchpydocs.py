import bpy


def search_pydocs(input_string):
    '''
    opens a browser with the search term, if can access.
    '''
    try:
        import webbrowser
        search_head = 'http://docs.python.org/py3k/search.html?q='
        search_tail = '&check_keywords=yes&area=default'
        search_term = input_string
        webbrowser.open(''.join([search_head, search_term, search_tail]))
    except:
        print('unable to browse docs online')
        


class TextSearchDocs(bpy.types.Operator):
    bl_label = ""
    bl_idname = "txt.search_pydocs"
    
    def execute(self, context):
        bpy.ops.text.copy()
        search_pydocs(context.window_manager.clipboard)
        return {'FINISHED'}

