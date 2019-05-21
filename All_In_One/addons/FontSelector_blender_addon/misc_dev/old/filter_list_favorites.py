import bpy
import os
import csv

from ..preferences import get_addon_preferences

from ..function_load_favorites import load_favorites

class FontSelectorFilterFavorite(bpy.types.Operator):
    bl_idname = "fontselector.filter_favorites"
    bl_label = ""
    bl_description = "Filter Font List to show only favorites Fonts"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        active=bpy.context.active_object
        if active is not None:
            active_type=active.type
        else:
            active_type=""
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = addon_preferences.prefs_folderpath
        return prefs!='' and active_type=='FONT'
    
    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = addon_preferences.prefs_folderpath
        prefpath = os.path.abspath(bpy.path.abspath(prefs))
        prefflist = os.path.join(prefpath, "fontselector_fontlist")
        preffav = os.path.join(prefpath, "fontselector_favorites")
        fontlist=bpy.data.window_managers['WinMan'].fontselector_list
        favtoggle=bpy.context.active_object.data.fontselector_favs
        sub_idx = bpy.context.active_object.data.fontselector_sub_index
        active_subdir=bpy.data.window_managers['WinMan'].fontselector_sub[sub_idx]
        sub=bpy.context.active_object.data.fontselector_use_sub
                
        
        
        if os.path.isdir(prefpath)==True:
            if os.path.isfile(prefflist)==True:
                if favtoggle==False and sub==False:
                    bpy.ops.fontselector.load_fontlist()
                elif favtoggle==False and sub==True:
                    bpy.ops.fontselector.filter_subdirfonts()
                else:
                    #remove existing font list
                    if len(fontlist)>0:
                        for i in range(len(fontlist)-1,-1,-1):
                            fontlist.remove(i)
                    if os.path.isfile(preffav)==True:
                        with open(preffav, 'r', newline='') as csvfile:
                            line = csv.reader(csvfile, delimiter='\n')
                            for l in line:
                                l1=str(l).replace("[", "")
                                l2=l1.replace("]", "")
                                l3=l2.replace("'", "")
                                l4=l3.replace('"', "")
                                n=l4.split(" || ")[0]
                                p=l4.split(" || ")[1]
                                s=l4.split(" || ")[2]
                                if sub==True:
                                    if s==active_subdir.name:
                                        newfont=fontlist.add()
                                        newfont.name=n
                                        newfont.filepath=p
                                        newfont.subdirectory=s
                                else:
                                    newfont=fontlist.add()
                                    newfont.name=n
                                    newfont.filepath=p
                                    newfont.subdirectory=s
                                        
                    else:
                        info = 'No Favorite Fonts'
                        self.report({'ERROR'}, info) 
                        print("Font Selector Warning : No Favorite Fonts")
                
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