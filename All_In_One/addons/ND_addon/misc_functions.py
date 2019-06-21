import bpy
import os
import platform
import subprocess

from .prefs import get_addon_preferences

#create prop if doesn't exist
def create_prop():
    winman=bpy.data.window_managers['WinMan']
    try:
        prop=winman.nd_props[0]
        return(prop)
    except IndexError:
        new=winman.nd_props.add()
        return(new)

#find shot folder
def find_shot_folder():
    prefs=get_addon_preferences()
    prefs_folder=prefs.prefs_folderpath
    
    winman=bpy.data.window_managers['WinMan']
    prop=winman.nd_props[0]
    
    shot_folder_file=os.path.join(prefs_folder, 'shots_folder.txt')
    f = open(shot_folder_file,"r") 
    shot_folder=f.read()
    
    if os.path.isdir(shot_folder):
        return (shot_folder)
    else:
        return('')

#find folder from filebrowser
def find_folder_filebrowser():
    prefs=get_addon_preferences()
    prefs_folder=prefs.prefs_folderpath
    
    winman=bpy.data.window_managers['WinMan']
    prop=winman.nd_props[0]
    shot=str(prop.shot_index).zfill(2)
    
    shot_folder_file=os.path.join(prefs_folder, 'shots_folder.txt')
    f = open(shot_folder_file,"r") 
    shot_folder=f.read()
    
    shot=os.path.join(shot_folder, shot)
    
    if os.path.isdir(shot):
        return (shot)
    else:
        return('')
    
#update function for filebrowser shot
def update_folderpath_shot(self, context):
    area=context.area
    
    folder=find_folder_filebrowser()
    #change directory
    if folder!='':
        area.spaces[0].params.directory=convert_windowspath_to(folder)
        
#update function for filebrowser custom path
def update_folderpath_path(self, context):
    winman=bpy.data.window_managers['WinMan']
    prop=winman.nd_props[0]
    
    area=context.area
    try:
        folder=prop.dirpath_coll[prop.path_index]
        area.spaces[0].params.directory=convert_windowspath_to(folder.path)
    except IndexError:
        pass
        
#get content of txt file
def get_content_txt(filepath):
    f = open(filepath,"r") 
    content=f.read()
    return (content)

#clear collection prop
def clear_coll_prop(prop):
    if len(prop)>=1:
        for i in range(len(prop)-1,-1,-1):
            prop.remove(i)
    return(prop)

#find os
def convert_windowspath_to(windows_path):
    if platform.system()=='Darwin':
        newpath=windows_path.replace('\\\\motionorama\\', '/Volumes/').replace('\\', '/')
    elif platform.system()=='Linux':
        newpath=windows_path.replace('\\\\motionorama\\', '/mnt/').replace('\\', '/')
    elif platform.system()=='Windows':
        newpath=windows_path
    return(newpath)

#create custom path from path and prop
def create_custom_path_props(path, prop):
    for f in os.listdir(path):
        new=prop.add()
        new.name=f.split('.txt')[0]
        new.path=get_content_txt(os.path.join(path, f))
        
#create props for render settings
def create_render_settings_props(path, prop):
    for f in os.listdir(path):
        new=prop.add()
        new.name=f.split('.json')[0]
        new.path=os.path.join(path, f)
        
#open specific folder
def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
        
#find shot from location
def return_shot_infos_from_path(path):
    dir1=os.path.dirname(path)
    cat=os.path.basename(dir1)
    
    dir2=os.path.dirname(dir1)
    shot_str=os.path.basename(dir2)
    
    try:
        shot=int(shot_str)
    except:
        shot=00
    return(shot, cat, dir2)
    
#suppress files in folder
def suppress_files_in_folder(folderpath):
    for f in os.listdir(folderpath):
        file=os.path.join(folderpath, f)
        try:
            os.remove(file)
        except:
            print("ND - impossible to remove "+f)
            
#suppress file
def suppress_file(filepath):
    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except:
            print("ND - impossible to remove "+filepath)
            
#activate metadatas
def activate_metadatas():
    scn=bpy.context.scene
    rd=scn.render
    
    rd.use_stamp_time = True
    rd.use_stamp_date = True
    rd.use_stamp_render_time = True
    rd.use_stamp_frame = True
    rd.use_stamp_scene = True
    rd.use_stamp_memory = True
    rd.use_stamp_camera = True
    rd.use_stamp_lens = True
    rd.use_stamp_filename = True
    rd.use_stamp_marker = True
    rd.use_stamp_sequencer_strip = False
    rd.use_stamp_strip_meta = False
    rd.use_stamp_note = True
    
#activate stamp metadatas
def activate_stamp_metadatas():
    scn=bpy.context.scene
    rd=scn.render
    
    rd.use_stamp = True
    rd.stamp_font_size = 12
    rd.use_stamp_labels = True
    rd.stamp_foreground = (1, 1, 1, 1)
    rd.stamp_background = (0, 0, 0, 0.5)
    
#create folder if doesn't exist
def create_folder(path):
    if os.path.isdir(path)==False:
        os.mkdir(path)
        print("ND - "+path+" folder created")