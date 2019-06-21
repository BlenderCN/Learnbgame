import bpy,os

addon = os.path.basename(os.path.dirname(__file__))

class CustomPanels(bpy.types.PropertyGroup) :
    pass

class CustomizeUIPrefs(bpy.types.AddonPreferences):
    bl_idname = addon

    panels = bpy.props.PointerProperty(type = CustomPanels,options={'HIDDEN'})
    customize = bpy.props.BoolProperty(default = False,options={'HIDDEN'})
    #own_folder = bpy.props.StringProperty(subtype = 'FILE_PATH')

'''
class WorkspaceSettings(bpy.types.PropertyGroup) :

    pass
'''
