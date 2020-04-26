import bpy
import os
import csv

from ..preferences import get_addon_preferences
from ..functions.misc_functions import absolute_path, create_dir

from ..global_variable import filter_list

class FontSelectorAddFiltered(bpy.types.Operator):
    bl_idname = "fontselector.add_filtered"
    bl_label = ""
    bl_description = "Add Font to Filter"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        addon_preferences = get_addon_preferences()
        new = addon_preferences.prefs_filter
        return new != ''
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        new = addon_preferences.prefs_filter
        prefpath = absolute_path(addon_preferences.prefs_folderpath)
        preffilter = os.path.join(prefpath, filter_list)
        
        filterlist=[]
        
        #get filtered
        create_dir(prefpath)
        if os.path.isfile(preffilter)==True:
            with open(preffilter, 'r', newline='') as csvfile:
                line = csv.reader(csvfile, delimiter='\n')
                for l in line:
                    l1=str(l).replace("[", "")
                    l2=l1.replace("]", "")
                    l3=l2.replace("'", "")
                    l4=l3.replace('"', "")
                    filterlist.append(l4)
        
        #add new one
        chk_existing = 0
        for f in filterlist :
            if new == f :
                chk_existing = 1
                break
        if chk_existing == 0 :
            filterlist.append(new)
        else:
            info = new + ' already in Filtered Fonts'
            self.report({'INFO'}, info)
        
        #create external file
        if len(filterlist) != 0 and chk_existing == 0 :
            nfile = open(preffilter, "w")
            for f in filterlist:
                nfile.write(f+"\n")
            nfile.close()
            
            info = new + ' added to Filtered Fonts'
            self.report({'INFO'}, info)
        
            addon_preferences.prefs_filter=""
            
        return {'FINISHED'}