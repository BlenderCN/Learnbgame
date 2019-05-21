import bpy


def search_bpydocs(input_string):
    '''
    opens a browser with the search term, if can access.
    '''
    try:
        from urllib.request import urlopen
        d = urlopen('http://www.blender.org/documentation/250PythonDoc')
        d = d.read()
        s_path = str(d).split("/")[2]

        import webbrowser
        s_head = 'http://www.blender.org/documentation/'
        s_slug = '/search.html?q='
        s_tail = '&check_keywords=yes&area=default'
        s_term = input_string
        webbrowser.open(''.join([s_head, s_path, s_slug, s_term, s_tail]))
    except:
        print('unable to browse docs online')
        


class TextSearchBpyDocs(bpy.types.Operator):
    bl_label = ""
    bl_idname = "txt.search_bpydocs"
    
    def execute(self, context):
        bpy.ops.text.copy()
        search_bpydocs(context.window_manager.clipboard)
        return {'FINISHED'}

