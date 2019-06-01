import bpy

from ..global_messages import *

### CODES ###
# 1 = startup changes in font folder message
# 2 = error subdirectory font folder doesn't exist anymore
# 3 = saved font folders with deleted inexistent folder
# 4 = unable to save font folder, no existent one
# 5 = font installed, refreshing invitation
# 6 = persmission denied for font installation
# 7 = no existing font list, please refresh
# 8 = missing font in new list, check text object
# 9 = error font doesn't exist anymore

class FontSelectorDialogMessage(bpy.types.Operator):
    bl_idname = "fontselector.dialog_message"
    bl_label = "FontSelector Dialog"
    bl_options = {'INTERNAL'}
 
    code : bpy.props.IntProperty()
    customstring : bpy.props.StringProperty()
 
    def execute(self, context):
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
 
    def draw(self, context):
        # startup changes in font folder message
        if self.code == 1 :
            self.layout.label(text = changes_msg, icon = 'ERROR')
            self.layout.operator("fontselector.modal_refresh", icon='FILE_REFRESH')
        
        # error subdirectory font folder doesn't exist anymore
        elif self.code == 2 :
            self.layout.label(text = subdirectory_error, icon = 'ERROR')
            self.layout.label(text = changes_msg)
            self.layout.operator("fontselector.modal_refresh", icon='FILE_REFRESH')

        # saved font folders with deleted inexistent folder
        elif self.code == 3 :
            self.layout.label(text = fontfolder_saved)
            self.layout.label(text = fontfolder_deleted, icon = 'ERROR')
            for folder in self.customstring.split(", ") :
                self.layout.label(text = folder)

        # unable to save font folder, no existent one
        elif self.code == 4 :
            self.layout.label(text = fontfolder_not_saved, icon = 'ERROR')
            self.layout.label(text = fontfolder_deleted)
            for folder in self.customstring.split(", ") :
                self.layout.label(text = folder)

        # font installed, refreshing invitation
        elif self.code == 5 :
            self.layout.label(text = font_installed, icon = 'INFO')
            self.layout.operator("fontselector.modal_refresh", icon='FILE_REFRESH')
        
        # persmission denied for font installation
        elif self.code == 6 :
            self.layout.label(text = permission_denied, icon = 'ERROR')
            self.layout.label(text = self.customstring)

        # error subdirectory font folder doesn't exist anymore
        elif self.code == 7 :
            self.layout.label(text = no_font_list_msg, icon = 'ERROR')
            self.layout.operator("fontselector.modal_refresh", icon='FILE_REFRESH')

        # persmission denied for font installation
        elif self.code == 8 :
            self.layout.label(text = missing_font, icon = 'ERROR')
            self.layout.label(text = check_locate_font)
            self.layout.label(text = self.customstring)

        # error subdirectory font folder doesn't exist anymore
        elif self.code == 9 :
            self.layout.label(text = font_file_error, icon = 'ERROR')