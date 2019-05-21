bl_info = {
    'name': 'Text Editor Chroma key',
    'author': 'Dealga McArdle (zeffii) <digitalaphasia.com>',
    'version': (0, 7, 0),
    'blender': (2, 5, 9),
    'location': 'text editor > header > chroma button',
    'description': 'makes it all pretty',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Text Editor'}


import bpy

def draw_item(self, context):
    layout = self.layout
    layout.operator("txt.set_text_prefs", icon='COLOR')


class SetTextPreferences(bpy.types.Operator):
    bl_label = ""
    bl_idname = "txt.set_text_prefs"
    
    def execute(self, context):
        st = context.space_data
        st.show_line_numbers = True
        st.show_word_wrap = True
        st.show_syntax_highlight = True
        st.show_margin = True
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SetTextPreferences)
    bpy.types.TEXT_HT_header.prepend(draw_item)

def unregister():
    bpy.utils.unregister_class(SetTextPreferences)
    bpy.types.TEXT_HT_header.remove(draw_item)

if __name__ == "__main__":
    register()