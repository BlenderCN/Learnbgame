import bpy,os

addon = os.path.basename(os.path.dirname(__file__))

def menu_func(self, context):
    layout = self.layout
    row = layout.row(align=True)
    customize_UI_prefs = context.user_preferences.addons[addon].preferences.customize
    if not customize_UI_prefs :
        row.operator("customizeui.customize_ui",text='Customize')
    else :
        row.operator("customizeui.apply_ui",text='Apply UI')
