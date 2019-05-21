import bpy
from bpy.types import Menu
from . pie_utils import *


###########################################################
# RIGHT CLIC
###########################################################

class PieTextEditor(Menu):
    bl_idname = "pie.text_editor"
    bl_label = "Text editor"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # 4-LEFT
        pie.operator("text.custom_copy", text="Copy", icon='GREASEPENCIL')
        # 6-RIGHT
        if "#" in bpy.context.space_data.text.current_line.body:
            pie.operator("text.init_comment_uncomment", text="Uncomment")        
        else:
            pie.operator("text.init_comment_uncomment", text="Comment")
        # 2-BOTTOM
        pie.operator("text.custom_paste", text="Paste", icon='FILE_TICK')
        # 8-TOP
        addon_name = "code_autocomplete-master"
        if addon_name in [addon.module for addon in bpy.context.user_preferences.addons]:
            pie.operator("code_autocomplete.run_addon", text="Run addon", icon='PLAY')
        else:
            pie.operator("text.run_script", text="Run script", icon='PLAY')
        # 7-TOP-LEFT
        pie.operator("text.custom_cut", text="Cut", icon='SCULPTMODE_HLT')
        # 9-TOP-RIGHT
        pie.operator("text.init_choose_module", text="Choose module", icon='FILE_TEXT')
        # 1-BOTTOM-LEFT
        if addon_name in [addon.module for addon in bpy.context.user_preferences.addons]:
            pie.operator("wm.call_menu", text="Template").name="text_editor.insert_template_menu"
        else:
            pie.prop(context.space_data, "show_word_wrap", text="Wrap")
        # 3-BOTTOM-RIGHT
        row = pie.row(align=True)
        row.scale_y = 1.5
        row.operator("text.init_jump_to_class",text="To class")
        row.operator("text.init_jump_to_fonction",text="To fonction")





###########################################################
# SHIFT + RIGHT CLIC
###########################################################

class PieTextPlus(Menu):
    bl_idname = "pie.text_plus"
    bl_label = "Text editor"

    def draw(self, context):
        pie = self.layout.menu_pie()
        addon_name = "code_autocomplete-master"
        if addon_name in [addon.module for addon in bpy.context.user_preferences.addons]:
            # 4-LEFT
            pie.operator("text.properties", text="Properties", icon='OUTLINER_OB_SURFACE')
            # 6-RIGHT    
            pie.operator("wm.console_toggle", text="Console", icon='CONSOLE')                                 
            # 2-BOTTOM
            pie.operator("screen.area_dupli", text="Dupli window", icon='RENDERLAYERS')
            # 8_TOP 
            pie.operator("code_autocomplete.save_files", text="Save all files", icon='SAVE_COPY')               
            # 7-TOP-LEFT
            pie.prop(context.space_data, "show_word_wrap", text="Wrap") 
            # 9-TOP-RIGHT
            pie.operator("text.jump", text="Jump to line", icon='ANIM_DATA')
            
        else:
            # 4-LEFT
            pie.operator("text.properties", text="Properties", icon='OUTLINER_OB_SURFACE')
            # 6-RIGHT    
            pie.operator("wm.console_toggle", text="Console", icon='CONSOLE')                                 
            # 2-BOTTOM
            pie.operator("screen.area_dupli", text="Dupli window", icon='RENDERLAYERS')
            # 8_TOP 
            pie.operator("text.save", text="Save file", icon='SAVE_COPY') 