import bpy
import os

from ..preferences import get_addon_preferences
from ..misc_functions import absolute_path, suppress_files_pattern

#purge all cache files
class VCachePurgeAll(bpy.types.Operator):
    bl_idname = "vcache.purge_all"
    bl_label = "Purge all Viewport Cache"
    bl_description = "Purge All Viewport Cache Files"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        chk=0
        if len(os.listdir(cachefolder))!=0:
            chk=1
        return chk==1
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
                
        [ os.remove(os.path.join(cachefolder, f)) for f in os.listdir(cachefolder) ]
        self.report({'INFO'}, "VCache files deleted")
        return {'FINISHED'}

#purge project files
class VCachePurgeProject(bpy.types.Operator):
    bl_idname = "vcache.purge_project"
    bl_label = "Purge Project Viewport Cache"
    bl_description = "Purge Project Viewport Cache Files"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        if bpy.data.is_saved:
            blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        else:
            blendname='untitled'
        chk=0
        for f in os.listdir(cachefolder):
            if blendname in f:
                chk=1
        return chk==1
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        if bpy.data.is_saved:
            blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        else:
            blendname='untitled'
        
        pattern=blendname + "___"
        suppress_files_pattern(cachefolder, pattern)
        self.report({'INFO'}, "VCache Project files deleted")
        return {'FINISHED'}
    
#purge scene files
class VCachePurgeScene(bpy.types.Operator):
    bl_idname = "vcache.purge_scene"
    bl_label = "Purge Scene Viewport Cache"
    bl_description = "Purge Current Scene Viewport Cache Files"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        if bpy.data.is_saved:
            blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        else:
            blendname='untitled'
        scenename=bpy.context.scene.name
        match=blendname + "___" + scenename + "___cache_"
        chk=0
        for f in os.listdir(cachefolder):
            if match in f:
                chk=1
        return chk==1
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        if bpy.data.is_saved:
            blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        else:
            blendname='untitled'
        scenename=bpy.context.scene.name
        
        pattern=blendname + "___" + scenename + "___cache_"
        suppress_files_pattern(cachefolder, pattern)
        self.report({'INFO'}, "VCache Scene files deleted")
        return {'FINISHED'}
    
#purge all cache files except this project
class VCachePurgeAllExceptProject(bpy.types.Operator):
    bl_idname = "vcache.purge_all_except_project"
    bl_label = "Purge except Current Project"
    bl_description = "Purge All Viewport Cache Files except Cache from Current Project"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        chk=0
        if len(os.listdir(cachefolder))!=0:
            chk=1
        return chk==1
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        
        [ os.remove(os.path.join(cachefolder, f)) for f in os.listdir(cachefolder) if ("___cache___" + blendname + "___") not in f ]
        self.report({'INFO'}, "VCache files deleted")
        return {'FINISHED'}