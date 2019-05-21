bl_info= {
    "name": "bLandscape Tools",
    "author": "Miroslav Horvath",
    "version": (0, 2),
    "blender": (2, 7, 9),
    "location": "View3D > Properties > bLandscape Tools",
    "description": "Tools for virtual landscaping",
    "warning": "",
    "wiki_url": "https://github.com/paxetgloria/bLandscapeTools/wiki",
    "tracker_url": "https://github.com/paxetgloria/bLandscapeTools/issues",
    "support" : "COMMUNITY",
    "category": "Learnbgame"
}

import sys
import os
if "bpy" in locals():
    import imp

    imp.reload(bLT_main)
    imp.reload(bLT_utils)
    print("bLT: Reloaded multifiles")
else:
    from . import bLT_main
    from . import bLT_utils

    print("bLT: Imported multifiles")
    
import bpy

from bpy.types import AddonPreferences
from bpy.props import StringProperty,CollectionProperty,IntProperty,BoolProperty,PointerProperty

class AddonPref_bLT(AddonPreferences):
    bl_idname = __name__

    GDALPath = StringProperty(name="GDAL path",
        description="Path to GDAL",
        maxlen= 1024,
        subtype='DIR_PATH',
        default='c:\Program Files\GDAL\\')
        
        
    OutputPath = StringProperty(name="Output path",
        description="Path to Output folder",
        maxlen= 1024,
        subtype='DIR_PATH',
        default='{}\\Documents\\'.format(os.environ['USERPROFILE']))
    
    OpenCVInstalled = BoolProperty(default=False)
    
    def draw(self, context):
        layout = self.layout   
        box = layout.box()
        box.prop(self, "GDALPath")
        box.prop(self, "OutputPath")
        box.operator("a.install_opencv",icon='TEXTURE')
        if self.OpenCVInstalled:
            box.label('OpenCV installed!',icon='FILE_TICK')
        else:
            box.label('OpenCV has not been installed yet!',icon='ERROR')
        
classes = (
    bLT_main.OP_AP_InstallOpenCV,
    bLT_main.LocationItems,
    bLT_main.TexturePaintBrush,
    bLT_main.UL_Locations_list,
    bLT_main.OP_UI_SwitchLocations,
    bLT_main.OP_UI_RemoveLocation,
    bLT_main.VIEW3D_ProjectSettings,
    bLT_main.VIEW3D_DataSource,
    bLT_main.VIEW3D_LocationsManager,
    bLT_main.VIEW3D_TerrainEditing,
    bLT_main.VIEW3D_SurfacePainting,
    bLT_main.VIEW3D_ViewportSettings,
    bLT_main.VIEW3D_bLTilities,
    bLT_main.OP_CreateProject,
    bLT_main.OP_ImportLocation,
    bLT_main.OP_CreateLocation,
    bLT_main.OP_CommitLocation,
    bLT_main.OP_PickLocation,
    bLT_main.OP_DrawSplashScreen,
    bLT_main.OP_AssignMeshTerrainModifier,
    bLT_main.OP_AddMeshTerrainModifier,
    bLT_main.OP_ApplyMeshTerrainModifier,
    bLT_main.OP_AddSplineTerrainModifier,
    bLT_main.OP_ApplySplineTerrainModifier,
    bLT_main.OP_AppearanceTexturedWire,
    bLT_main.OP_AppearanceTexturedNoWire,
    bLT_main.OP_AppearanceSmooth,
    bLT_main.OP_AppearanceFlat,
    bLT_main.OP_AppearanceMatCapNoWire,
    bLT_main.OP_AppearanceMatCapWire,
    bLT_main.OP_CreateFlatTerrain,
    bLT_main.OP_CreateSurfaceMask,
    bLT_main.OP_CheckSurfaceMaskFull,
    AddonPref_bLT  
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    os.environ['PATH'] = ''.join(('{}\lib;'.format(bLT_utils.getPaths()[1]),os.environ['PATH']))
    
    try:
        import cv2
        bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OpenCVInstalled = True
    except:
        bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OpenCVInstalled = False
    
    
    bpy.types.Scene.locationgroups = CollectionProperty(type=bLT_main.LocationItems)
    bpy.types.Scene.locationgroups_index = IntProperty(default=-1)
    bpy.types.Scene.TexturePaintBrushNames = CollectionProperty(type=bLT_main.TexturePaintBrush)
    bpy.types.Scene.hasSea = BoolProperty(default=False)
    
    dataFolder = bLT_utils.getPaths()[2]

    import zipfile
    zip_ref = zipfile.ZipFile('{}\\bLandscapeTools.zip'.format(dataFolder), 'r')
    zip_ref.extractall('{}\\AppData\\Roaming\\Blender Foundation\\Blender\\{}.{}\\scripts\\startup\\bl_app_templates_user'.format(os.environ['USERPROFILE'],bpy.app.version[0],bpy.app.version[1]))
    zip_ref.close()

    bpy.context.user_preferences.filepaths.use_relative_paths = False
    bpy.context.user_preferences.filepaths.show_thumbnails = True
    bpy.context.user_preferences.system.use_mipmaps = False
    bpy.context.user_preferences.view.use_mouse_depth_navigate = True
    bpy.context.user_preferences.view.use_zoom_to_mouse = True
    bpy.context.user_preferences.view.use_rotate_around_active = True
    bpy.context.user_preferences.view.use_auto_perspective = True
    bpy.context.user_preferences.system.use_select_pick_depth = True
    bpy.context.user_preferences.system.select_method = 'GL_QUERY'


    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.locationgroups
    del bpy.types.Scene.locationgroups_index
    del bpy.types.Scene.TexturePaintBrushNames
    del bpy.types.Scene.hasSea

if __name__ == "__main__":
    register()