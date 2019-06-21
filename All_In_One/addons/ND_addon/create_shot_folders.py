import bpy
import os
import shutil

from .misc_functions import find_shot_folder

class ND_create_shot_folders(bpy.types.Operator):
    bl_idname = "nd.create_shot_folders"
    bl_label = "Create Shot Folders"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    shot_number=bpy.props.IntProperty(name="Shot Number", default=0)

    @classmethod
    def poll(cls, context):
        return find_shot_folder()!=''
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=150, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "shot_number")
        
    def execute(self, context):
        shot_folder=find_shot_folder()
        base=os.path.join(shot_folder, "00")
        new=os.path.join(shot_folder, str(self.shot_number).zfill(2))
        if os.path.isdir(new)==False:
            shutil.copytree(base, new)
            inf="ND - Shot "+ str(self.shot_number) + " created"
            print(inf)
            self.report({'INFO'}, inf)
        else:
            inf="ND - Shot "+ str(self.shot_number) + " already exists"
            print(inf)
            self.report({'WARNING'}, inf)
        return {"FINISHED"}
        