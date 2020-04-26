import bpy


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


