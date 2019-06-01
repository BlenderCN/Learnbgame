import bpy
import os
import csv

from ..preferences import get_addon_preferences
from ..function_load_favorites import load_favorites

class FontSelectorLoadFontList(bpy.types.Operator):
    bl_idname = "fontselector.load_fontlist"
    bl_label = ""
    bl_description = "Load Font List from external Font Selector preferences File"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = addon_preferences.prefs_folderpath
        return prefs!=''
    
    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = addon_preferences.prefs_folderpath
        prefpath = os.path.abspath(bpy.path.abspath(prefs))
        prefflist = os.path.join(prefpath, "fontselector_fontlist")
        preffav = os.path.join(prefpath, "fontselector_favorites")
        fontlist=bpy.data.window_managers['WinMan'].fontselector_list
        
        #remove existing font list
        if len(fontlist)>0:
            for i in range(len(fontlist)-1,-1,-1):
                fontlist.remove(i)
        
        if os.path.isdir(prefpath)==True:
            if os.path.isfile(prefflist)==True:
                with open(prefflist, 'r', newline='') as csvfile:
                    line = csv.reader(csvfile, delimiter='\n')
                    for l in line:
                        l1=str(l).replace("[", "")
                        l2=l1.replace("]", "")
                        l3=l2.replace("'", "")
                        l4=l3.replace('"', "")
                        n=l4.split(" || ")[0]
                        p=l4.split(" || ")[1]
                        s=l4.split(" || ")[2]
                        newfont=fontlist.add()
                        newfont.name=n
                        newfont.filepath=p
                        newfont.subdirectory=s
                if os.path.isfile(preffav)==True:
                    load_favorites()
            else:
                info = 'Preference File does not exist, check Preference Folder path'
                self.report({'ERROR'}, info)  
                print("Font Selector Warning : Preference File does not exist, check Preference Folder path")  
        else:
            info = 'Folder does not exist, check Preference Folder path'
            self.report({'ERROR'}, info) 
            print("Font Selector Warning : Folder does not exist, check Preference Folder path")   
            
        return {'FINISHED'}