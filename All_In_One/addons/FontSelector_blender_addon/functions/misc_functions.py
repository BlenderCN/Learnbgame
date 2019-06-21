import bpy
import os
import sys
import platform
import subprocess

from ..global_variable import extensions, warning_font_path

# open folder in explorer
def open_folder_in_explorer(path) :
        if platform.system() == "Windows":
                os.startfile(path)
        elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
        else:
                subprocess.Popen(["xdg-open", path])

# export menu
def menu_export_favorites(self, context) :
    self.layout.operator('fontselector.export_fonts', text="Fonts export", icon='FILE_FONT')

# clear collection
def clear_collection(collection) :
        if len(collection)>=1:
            for i in range(len(collection)-1,-1,-1):
                collection.remove(i)

# absolute path
def absolute_path(path) :
        apath = os.path.abspath(bpy.path.abspath(path))
        return apath

# get size of folder and subdir in bytes
def get_size(folderpath) :
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folderpath):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# create directory if doesn't exist
def create_dir(dir_path) :
        if os.path.isdir(dir_path) == False :
                os.makedirs(dir_path)

# remove unused font datablocks and return number of fonts removed
def remove_unused_font() :
        removed_fonts_count = 0
        for f in bpy.data.fonts :
            if f.users == 0 :
                removed_fonts_count += 1
                bpy.data.fonts.remove(f, do_unlink=True)
        return removed_fonts_count

# get all font files in dir and subdir ((font path, font subdir, file name)(subdir name, subdir path))
def get_all_font_files(base_dir) :
        font_files_list = []
        subdir_list = []
        for (root, directories, filenames) in os.walk(base_dir) :
                for file in filenames :
                        extension = os.path.splitext(file)[1]
                        if any(extension == ext for ext in extensions) :

                                dupe_check = 0
                                font_path = os.path.join(root, file)
                                subdir = os.path.basename(os.path.dirname(font_path))
                                font_files_list.append([font_path, subdir, file])

                                # create the subdir list
                                for dir in subdir_list :
                                        if dir[0] == subdir :
                                                dupe_check = 1
                                                break
                                if dupe_check == 0 :
                                        subdir_list.append([subdir, root])
        return font_files_list, subdir_list

# suppress existing file
def suppress_existing_file(filepath) :
    if os.path.isfile(filepath) :
        os.remove(filepath)

# print progression update
def update_progress(job_title, count, total_count) :
    progress = count / total_count

    length = 20 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " Fonts Treated\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()

# turn on avoid_changes props for selected object
def avoid_changes_selected() :
    avoid_list = []

    # text objects
    for obj in bpy.data.objects :
        if obj.type == 'FONT' and obj.select_get :
            obj.data.fontselector_avoid_changes = True
            avoid_list.append(obj.data)

    # text strips
    for scn in bpy.data.scenes :
        seq = scn.sequence_editor.sequences_all
        for strip in seq :
            if strip.type == 'TEXT' and strip.select :
                strip.fontselector_avoid_changes = True
                avoid_list.append(strip)

    return avoid_list

# create warning font datablock
def create_warning_font() :
    try :
        datablock = bpy.data.fonts['FontSelector_symbols_warning']
    except KeyError :
        datablock = bpy.data.fonts.load(filepath = warning_font_path)
    return datablock