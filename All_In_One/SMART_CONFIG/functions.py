import bpy
import sys
import addon_utils
import os
import shutil

from .addon_prefs import get_addon_preferences

def update_progress_console(job_title, progress):
    length = 20 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()
    
def change_permissions_recursive(path, mode):
    if os.path.isfile(path)==True:
        os.chmod(path, mode)
    elif os.path.isdir(path)==True:
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in [os.path.join(root,d) for d in dirs]:
                os.chmod(dir, mode)
        for file in [os.path.join(root, f) for f in files]:
                os.chmod(file, mode)

def recursive_copy_dir_tree(sourceRoot, destRoot):
    if not os.path.exists(destRoot):
        return False
    ok = True
    for path, dirs, files in os.walk(sourceRoot):
        relPath = os.path.relpath(path, sourceRoot)
        destPath = os.path.join(destRoot, relPath)
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        for file in files:
            srcFile = os.path.join(path, file)
            destFile = os.path.join(destRoot,os.path.relpath((os.path.join(path, file)), sourceRoot))
            if os.path.isfile(destFile):
                ok = False
                continue
            shutil.copy2(srcFile, destFile)
    return{'FINISHED'}

def print_addon_modules(self, context):
    prefs=addon_preferences = get_addon_preferences()
    print()
    print("Smart Config warning : List of activated Addons Modules to export")
    print("Smart Config warning : This list does not take into account the per addon export exclusion settings")
    print()
    for mod_name in bpy.context.user_preferences.addons.keys():
        if mod_name not in prefs.exception_list:
            if prefs.use_trunk_exception==True and mod_name not in prefs.trunk_exception:
                print("    "+mod_name)
            elif prefs.use_trunk_exception==False:
                print("    "+mod_name)
    return{'FINISHED'}
