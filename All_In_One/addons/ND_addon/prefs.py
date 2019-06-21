import bpy
import os

addon_name = os.path.basename(os.path.dirname(__file__))

class VCacheAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = addon_name
    
    prefs_folderpath = bpy.props.StringProperty(
            name="Preferences Folder Path",
            default=r"\\motionorama\MOTIONORAMA_DRIVE\----ELEMENTS\BLENDER\ne_pas_toucher_blender_common_scripts\config\notre_dame_prefs",
            description="Folder where Prefs Files will be stored",
            subtype="DIR_PATH",
            )
            
    source=bpy.props.StringProperty(subtype="DIR_PATH", name='Source', default=r"C:\Users\GRAPHISTE 001\AppData\Roaming\Blender Foundation\Blender\2.79\scripts\addons\ND_addon_blender")
    destination=bpy.props.StringProperty(subtype="DIR_PATH", name='Destination', default=r"\\motionorama\MOTIONORAMA_DRIVE\----ELEMENTS\BLENDER\ne_pas_toucher_blender_common_scripts\scripts\addons\ND_addon_blender_share")
    editing_folder=bpy.props.StringProperty(subtype="DIR_PATH", name='Editing Folder', default=r"M:\PROGRAM_33\NOTRE_DAME\002_PROD\001_PROJECTS\003_EDITING")
    spreadsheet_url=bpy.props.StringProperty(name='Spreadsheet URL', default=r"https://docs.google.com/spreadsheets/d/1-KIbJUdhPctKJBhjSaxth3IBxeJtPZMPDp7qmxA6S2E/")
            
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'prefs_folderpath')
        layout.prop(self, 'editing_folder')
        layout.prop(self, 'spreadsheet_url')
        box=layout.box()
        box.label("Debug")
        box.prop(self, "source")
        box.prop(self, "destination")
        box.operator("nd.deploy_addon", icon='ERROR')
        

# get addon preferences
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)