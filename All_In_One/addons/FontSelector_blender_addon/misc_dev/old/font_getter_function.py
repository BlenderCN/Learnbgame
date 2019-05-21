import bpy
import csv
import os

from .preferences import get_addon_preferences
from .functions.misc_functions import create_dir, absolute_path, clear_collection, get_size
from .function_load_font_subdir import load_font_subdir
from .function_load_favorites import load_favorites

from .global_variable import *
  
def execute(self, context):
    #get addon prefs
    dlist = bpy.data.fonts
    addon_preferences = get_addon_preferences()
    fplist = addon_preferences.font_folders
    prefpath = absolute_path(addon_preferences.prefs_folderpath)

    #define preference files
    preffav = os.path.join(prefpath, fav_list)
    prefflist = os.path.join(prefpath, font_list)
    preffilter = os.path.join(prefpath, filter_list)
    prefsubdir = os.path.join(prefpath, subdir_list)
    size_file_output = os.path.join(prefpath, size_file)

    fontlist=bpy.data.window_managers['WinMan'].fontselector_list
    dupelist=[]
    subdir=[]
    filterlist=[]
    
    #get filters
    if os.path.isdir(prefpath) == True :
        if os.path.isfile(preffilter) == True :
            with open(preffilter, 'r', newline='') as csvfile :
                line = csv.reader(csvfile, delimiter='\n')
                for l in line:
                    l1=str(l).replace("[", "")
                    l2=l1.replace("]", "")
                    l3=l2.replace("'", "")
                    l4=l3.replace('"', "")
                    filterlist.append(l4)

    #clean unused
    if len(dlist) > 0:
        bpy.ops.fontselector.remove_unused()
    
    #check if external folder exist and create it if not
    create_dir(prefpath)
    
    #clear list
    clear_collection(fontlist)
    
    
    #loop for subdir, total count and get size
    chkdir = 0
    count_total = 0
    size_total = 0
    for fp in fplist :
        if fp.folderpath != "" :
            path = absolute_path(fp.folderpath)
            size_total += get_size(path)     
            if os.path.isdir(path) :
                chkdir = 1
                for dirpath, dirnames, files in os.walk(path):
                    #count typo to treat
                    for f3 in files:
                        exte = os.path.splitext(f3)[1]
                        if any(exte == ext for ext in extensions):
                            count_total += 1
                    #memorize subdirs
                    for f2 in os.listdir(dirpath):
                        filename, file_extension = os.path.splitext(f2)
                        if any(file_extension == ext for ext in extensions) and dirpath not in subdir :
                            subdir.append(dirpath)
    
    chkfont = 0
    count = 0
    for d in subdir:
        for file in os.listdir(d) :
            filename, file_extension = os.path.splitext(file)
            if any(file_extension == ext for ext in extensions):
                count += 1
                #try to load file
                if file in filterlist :
                    print(str(count)+"/"+str(count_total)+" fonts treated --- "+file+" avoided")
                else :
                    chkfont = 1
                    chklocaldupe = 0
                    for font in bpy.data.fonts:
                        fname = os.path.basename(absolute_path(font.filepath))
                        #check for dupe
                        if os.path.join(d, file) == absolute_path(font.filepath) or file == fname:
                            chklocaldupe = 1
                            print(str(count)+"/"+str(count_total)+" fonts treated --- "+file+" avoided")
                            break
                    if chklocaldupe == 0:
                        try:
                            bpy.data.fonts.load(filepath=os.path.join(d, file))
                            print(str(count)+"/"+str(count_total)+" fonts treated --- "+file+" imported")
                        except RuntimeError:
                            filterlist.append(file)
                            print(str(count)+"/"+str(count_total)+" fonts treated --- "+file+" corrupted, filtered out")
                        

    if chkdir == 1 and chkfont == 1 :      

        nfile = open(prefflist, "w")
        for f in bpy.data.fonts :
            chkdupe = 0
            for d in dupelist :
                if absolute_path(f.filepath) == d:
                    chkdupe = 1
                    break
            if chkdupe == 0 :
                nfpath = absolute_path(f.filepath)
                nfile.write(f.name+" || "+nfpath+' || '+os.path.basename(os.path.dirname(nfpath))+"\n")
                dupelist.append(nfpath)
            if f.users==0:
                bpy.data.fonts.remove(f, do_unlink=True)
        nfile.close()

        if os.path.isfile(prefflist)==True :
            bpy.ops.fontselector.load_fontlist()
            info='Font Selector : Font List refreshed'
            #print(info)#
            self.report({'INFO'}, info)

        if os.path.isfile(preffav)==True :
            load_favorites()

    elif chkdir == 0 :
        info = 'No valid Font Folder, check Preferences'
        self.report({'ERROR'}, info)  
        
    elif chkfont == 0 :
        info = 'No valid Font in Folders, check Preferences'
        self.report({'ERROR'}, info)
        
    #write filterlist
    if len(filterlist) != 0:
        if os.path.isdir(prefpath)==False:
            os.makedirs(prefpath)
        nfile2 = open(preffilter, "w")
        for f in filterlist:
            nfile2.write(f+"\n")
        nfile2.close()
        
    #write subdir list
    if len(subdir) != 0:
        if os.path.isdir(prefpath)==False:
            os.makedirs(prefpath)
        nfile3 = open(prefsubdir, "w")
        for d in subdir:
            nfile3.write(os.path.basename(d)+"\n")
        nfile3.close()
        load_font_subdir()

    #delete previous count file
    for file in os.listdir(prefpath) :
        if "fontselector_size_" in file :
            os.remove(os.path.join(prefpath, file))
    #write size file
    open(size_file_output + str(size_total), 'a').close()