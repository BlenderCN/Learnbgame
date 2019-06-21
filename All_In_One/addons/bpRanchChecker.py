bl_info = {
    "name": "Ranch Checker",
    "description": "Check your scene",
    "author": "Mohamed Bakhoche",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Toolbar > RanchChecher",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

import bpy
import os
import json
import urllib
from urllib.request import urlopen, urlretrieve
from bpy.types import Panel

class print_text(bpy.types.Operator):
    bl_label = "Print text"
    bl_idname = "class.printtext"
    
    def execute(self, context):
        opurl = urlopen('http://mohbakh.pythonanywhere.com/softwareVersion/').read().decode('UTF-8')
        jsonprint = json.loads(opurl)
        
        softwareList = []

        for i in range(len(jsonprint)):
            softwareList.append(jsonprint[i]["software_version"])
        #print (softwareList)
        for s in softwareList:
            s_split = s.split("/")
            #print (s_split)
            if s_split[0] == "BLENDER":

                print ("is supported")
                
        
        return {'FINISHED'}

class RanchChecker(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Rench Checker'
    bl_category = 'Checker'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="ranch")
        layout.operator("class.printtext")

def register():
    bpy.utils.register_class(RanchChecker)
    bpy.utils.register_class(print_text)
    
def unregister():
    bpy.utils.unregister_class(RanchChecker)
    bpy.utils.unregister_class(print_text)
    
if __name__ == "__main__":
    register()