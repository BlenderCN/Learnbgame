import bpy
import os

from bpy.props import FloatVectorProperty

addon_name = os.path.basename(os.path.dirname(__file__))

class Palette_AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = addon_name
    
    prefs_folderpath = bpy.props.StringProperty(
            name="Preferences Folder Path",
            default=os.path.join(os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets"), "palettes"),
            description="Folder where Color Palettes will be stored",
            subtype="DIR_PATH",
            )
    col1 = FloatVectorProperty(name='Default Color 1', subtype='COLOR_GAMMA', default=(0.0,0.168,0.187), min=0, max=1)
    col2 = FloatVectorProperty(name='Default Color 2', subtype='COLOR_GAMMA', default=(0.0,0.234,0.260), min=0, max=1)
    col3 = FloatVectorProperty(name='Default Color 3', subtype='COLOR_GAMMA', default=(0.007,0.305,0.332), min=0, max=1)
    col4 = FloatVectorProperty(name='Default Color 4', subtype='COLOR_GAMMA', default=(0.0,0.401,0.444), min=0, max=1)
    col5 = FloatVectorProperty(name='Default Color 5', subtype='COLOR_GAMMA', default=(0.0,0.536,0.593), min=0, max=1)
    
    def draw(self, context):
        layout = self.layout
        col=layout.column()
        col.prop(self, 'prefs_folderpath')
        col=layout.column(align=True)
        row=col.row(align=True)
        row.label("Default Palette, the middle color will be default color value : ", icon='GROUP_VCOL')
        row=col.row(align=True)
        row.prop(self, 'col1', text='')
        row.prop(self, 'col2', text='')
        row.prop(self, 'col3', text='')
        row.prop(self, 'col4', text='')
        row.prop(self, 'col5', text='')
        

# get addon preferences
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)