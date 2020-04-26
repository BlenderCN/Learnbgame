import bpy
import os

from .misc_functions import return_shot_infos_from_path, suppress_files_in_folder, activate_metadatas, activate_stamp_metadatas, create_folder
from .render_settings_functions import read_json, apply_render_settings_from_dataset

class ND_output_settings(bpy.types.Operator):
    bl_idname = "nd.output_settings"
    bl_label = "Set Output Settings"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    possible_states = [
                ("0","Render","Render"),
                ("1","Render proxy","Render proxy"),
                ("2","Playblast","Playblast"),
                ("3","Playblast OK","Playblast OK"),
                ]
    state= bpy.props.EnumProperty(name="State", default="2", items=possible_states)
    suppress_previous=bpy.props.BoolProperty(name="Suppress previous render", default=False)
    relative=bpy.props.BoolProperty(name="Relative Path", default=True)
    
    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved==True and context.scene.camera is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "state")
        row=layout.row()
        row.prop(self, "suppress_previous")
        if self.state not in {'2','3'}:
            row.prop(self, "relative")

    def execute(self, context):
        scn=bpy.context.scene
        rd=scn.render

        blend_path=bpy.data.filepath
        blend_name=os.path.splitext(os.path.basename(blend_path))[0]
        name=blend_name+"_"+scn.name+"_"+scn.camera.name
        
        prefix="RENDER_SETTINGS_"
        
        #get shot number
        shot, cat, dir=return_shot_infos_from_path(blend_path)
    
        name_sc=prefix+blend_name+"_"+scn.name+".json"
        name_cam=prefix+blend_name+"_"+scn.name+"_"+scn.camera.name+".json"
        json_sc=os.path.join(os.path.join(dir, "006_MISC"), name_sc)
        json_cam=os.path.join(os.path.join(dir, "006_MISC"), name_cam)
        
        if os.path.isfile(json_cam):
            json_file=json_cam
        elif os.path.isfile(json_sc):
            json_file=json_sc
        else:
            json_file=""

        #general settings
        activate_metadatas()
        
        #relative path
        if self.state!='2' and self.relative==True:
            bpy.ops.file.make_paths_relative()
        
        #playblast
        if self.state=='2':
            tmp=os.path.join(dir, "004_PLAYBLAST")
            playblast_path=os.path.join(tmp, name)
            abs_filepath=os.path.join(playblast_path, name+"_PLAYBLAST_####")
            #create folder if needed
            create_folder(playblast_path)
            #rd.resolution_percentage = 50
            rd.image_settings.file_format = 'PNG'
            rd.image_settings.color_mode = 'RGBA'
            rd.image_settings.compression = 15
            rd.image_settings.color_depth = '8'
            #rd.use_overwrite = True
            activate_stamp_metadatas()
            
                #playblast ok
        elif self.state=='3':
            tmp=os.path.join(dir, "004_PLAYBLAST")
            playblast_path=os.path.join(tmp, "000_PLAYBLAST_OK")
            abs_filepath=os.path.join(playblast_path, "SHOT"+str(shot).zfill(2)+"_PLAYBLAST_OK_####")
            #create folder if needed
            create_folder(playblast_path)
            rd.resolution_percentage = 100
            rd.image_settings.file_format = 'PNG'
            rd.image_settings.color_mode = 'RGB'
            rd.image_settings.compression = 15
            rd.image_settings.color_depth = '8'
            rd.use_overwrite = True
            activate_stamp_metadatas()

        #proxy
        elif self.state=='1':
            tmp=os.path.join(os.path.join(dir, "005_RENDER"), "PROXYS")
            proxy_path=os.path.join(tmp, name)
            abs_filepath=os.path.join(proxy_path, name+"_RENDER_PROXY_####")
            #create folder if needed
            create_folder(proxy_path)
            #rd.resolution_percentage = 50
            #suppress previous render if needed
            if self.suppress_previous==True:
                suppress_files_in_folder(proxy_path)
            #get render settings
            #get render layer and passes
            activate_stamp_metadatas()

        #render
        elif self.state=='0':
            tmp=os.path.join(os.path.join(dir, "005_RENDER"), "MASTERS")
            render_path=os.path.join(tmp, name)
            abs_filepath=os.path.join(render_path, name+"_RENDER_MASTER_####")
            #create folder if needed
            create_folder(render_path)
            rd.resolution_percentage = 100
            #suppress previous render if needed
            if self.suppress_previous==True:
                suppress_files_in_folder(render_path)
            #get render settings
            #get render layer and passes
            rd.use_stamp=False
            
        rd.filepath=bpy.path.relpath(abs_filepath)

        inf="ND - output set"
        print(inf)
        self.report({'INFO'}, inf)
        return {"FINISHED"}