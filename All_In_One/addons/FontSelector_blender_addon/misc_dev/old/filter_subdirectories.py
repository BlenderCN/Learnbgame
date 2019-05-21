import bpy
import os
import csv

from ..preferences import get_addon_preferences
from ..function_load_favorites import load_favorites

class FontSelectorFilterSubdirFonts(bpy.types.Operator):
    bl_idname = "fontselector.filter_subdirfonts"
    bl_label = ""
    bl_description = "Filter Font List to show only selected subdirectory Fonts"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active=bpy.context.active_object
        if active is not None:
            active_type=active.type
        else:
            active_type=""
        return active_type=='FONT' and len(bpy.data.window_managers['WinMan'].fontselector_sub)!=0

    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = addon_preferences.prefs_folderpath
        prefpath = os.path.abspath(bpy.path.abspath(prefs))
        prefflist = os.path.join(prefpath, "fontselector_fontlist")
        fontlist = bpy.data.window_managers['WinMan'].fontselector_list
        active=bpy.context.active_object
        sub_idx = active.data.fontselector_sub_index
        active_subdir=bpy.data.window_managers['WinMan'].fontselector_sub[sub_idx]

                
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
                        if s==active_subdir.name:
                            newfont=fontlist.add()
                            newfont.name=n
                            newfont.filepath=p
                            newfont.subdirectory=s
                            
        load_favorites()
                            
        return {'FINISHED'}