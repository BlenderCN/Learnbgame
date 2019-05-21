import bpy
import os

from .misc_functions import return_shot_infos_from_path

class ND_render_settings(bpy.types.Operator):
    bl_idname = "nd.play_shot"
    bl_label = "Play Current"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    possible_states = [
                ("0","Render","Render"),
                ("1","Render proxy","Render proxy"),
                ("2","Playblast","Playblast"),
                ]
    state= bpy.props.EnumProperty(name="State", default="2", items=possible_states)
    
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

    def execute(self, context):
        scn=bpy.context.scene
        rd=scn.render
        blend_path=bpy.data.filepath
        blend_name=os.path.splitext(os.path.basename(blend_path))[0]
        name=blend_name+"_"+scn.name+"_"+scn.camera.name
        
        old_fp=rd.filepath
        
        #get shot number
        shot, cat, dir=return_shot_infos_from_path(blend_path)

        #playblast
        if self.state=='2':
            tmp=os.path.join(dir, "004_PLAYBLAST")
            playblast_path=os.path.join(tmp, name)
            abs_folder=playblast_path
            abs_filepath=os.path.join(playblast_path, name+"_PLAYBLAST_####")

        #proxy
        elif self.state=='1':
            tmp=os.path.join(os.path.join(dir, "005_RENDER"), "PROXYS")
            proxy_path=os.path.join(tmp, name)
            abs_folder=proxy_path
            abs_filepath=os.path.join(proxy_path, name+"_RENDER_PROXY_####")
            
        #render
        elif self.state=='0':
            tmp=os.path.join(os.path.join(dir, "005_RENDER"), "MASTERS")
            render_path=os.path.join(tmp, name)
            abs_folder=render_path
            abs_filepath=os.path.join(render_path, name+"_RENDER_MASTER_####")
        
        if os.path.isdir(abs_folder):
            if len(os.listdir(abs_folder))!=0:
                ext=os.path.splitext(os.listdir(abs_folder)[0])[1]
                
                rd.filepath=bpy.path.relpath(abs_filepath+ext)
        
                #play
                bpy.ops.render.play_rendered_anim()
                
                rd.filepath=old_fp
            else:
                
                inf="ND - no rendered images"
                print(inf)
                self.report({'WARNING'}, inf)
        else:
            inf="ND - no corresponding folder"
            print(inf)
            self.report({'WARNING'}, inf)

        return {"FINISHED"}