import bpy
import os

from .prefs import get_addon_preferences
from .misc_functions import return_shot_infos_from_path, suppress_files_in_folder, activate_metadatas, activate_stamp_metadatas, create_folder, clear_coll_prop, create_render_settings_props
from .render_settings_functions import read_json, apply_render_settings_from_dataset

class ND_render_settings(bpy.types.Operator):
    bl_idname = "nd.render_settings"
    bl_label = "Set Render Settings"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    index=bpy.props.IntProperty(min=0, default=0)
    
    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved==True
    
    def invoke(self, context, event):
        winman=bpy.data.window_managers['WinMan']
        prop=winman.nd_props[0]
        
        prefs=get_addon_preferences()
        path=prefs.prefs_folderpath
        renderpath=os.path.join(path, 'render_settings')
        
        #erase list
        custompath=clear_coll_prop(prop.render_coll)
        
        #create new list
        create_render_settings_props(renderpath, prop.render_coll)

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        winman=bpy.data.window_managers['WinMan']
        prop=winman.nd_props[0]
        
        layout = self.layout
        layout.template_list("NDUIList", "", prop, "render_coll", self, "index", rows=5)

    def execute(self, context):
        winman=bpy.data.window_managers['WinMan']
        prop=winman.nd_props[0]
        
        scn=bpy.context.scene
        rd=scn.render
        
        try:
            json_file=prop.render_coll[self.index].path
            datas=read_json(json_file)
            apply_render_settings_from_dataset(datas)
            
            #general settings
            activate_metadatas()
            
            #override settings
            rd.use_file_extension = True
            rd.use_render_cache = False
            rd.use_freestyle = False    
            
            inf="ND - settings loaded"
            print(inf)
            self.report({'INFO'}, inf)
            
        except IndexError:
            inf="ND - No settings"
            print(inf)
            self.report({'WARNING'}, inf)


        return {"FINISHED"}