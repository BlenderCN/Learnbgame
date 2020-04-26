import bpy
import webbrowser

from .prefs import get_addon_preferences

class ND_GoToSpreadSheet(bpy.types.Operator):
    bl_idname = "nd.gotospreadsheet"
    bl_label = "Go to spreadsheet"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        prefs=get_addon_preferences()
        url=prefs.spreadsheet_url
        webbrowser.open(url)
        return {"FINISHED"}