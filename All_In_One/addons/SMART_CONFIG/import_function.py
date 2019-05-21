import bpy
import os
import sys
import shutil
import csv
import addon_utils
import stat

from bpy_extras.io_utils import ImportHelper
from bpy.props import IntProperty, CollectionProperty , StringProperty , BoolProperty, EnumProperty

from .functions import update_progress_console, change_permissions_recursive, recursive_copy_dir_tree

### Import Preset Operator ###
class SmartConfig_Import(bpy.types.Operator, ImportHelper):
    bl_idname = "smartconfig.import_config"
    bl_label = "Import Configuration"
    filename_ext = ".sc"
    filter_glob = StringProperty(default="*.sc", options={'HIDDEN'})
    filepath = StringProperty(default="smart config")
    
    ##### prop #####
    install_userfolder = BoolProperty(
            name="Shared folder",
            description="Install Addons in Shared folder instead of Blender installation folder\nAll Blender versions on this computer will have access to installed Addons\nWarning : Installed Addons will not be portable",
            default=True,
            )
    import_startup_file = BoolProperty(
            name="Install Blender Startup File",
            description="Install Blender Startup File if available",
            default=True,
            )
    import_bookmarks = BoolProperty(
            name="Install Bookmarks File",
            description="Install Blender Bookmarks File if available",
            default=True,
            )
    import_users_prefs = BoolProperty(
            name="Install User Preferences File",
            description="Install Blender User Preferences File if available",
            default=True,
            )
    import_presets = BoolProperty(
            name="Install Preset Files",
            description="Install Blender Preset Files if available",
            default=True,
            )
    import_config_folders = BoolProperty(
            name="Install Configuration Folders",
            description="Install Blender Configuration Folders if available (some addons use these to save preferences...)",
            default=True,
            )
    import_datafiles_folders = BoolProperty(
            name="Install Datafiles Folders",
            description="Install Blender Datafiles Folders in Export (some addons use these to save presets...)",
            default=True,
            )
    
    #### DRAW ####
    def draw(self, context):
        layout = self.layout
                
        box = layout.box()
        box.label('Import Settings :', icon='SCRIPTWIN')
        box.prop(self, 'install_userfolder')
        box.prop(self, 'import_startup_file')
        box.prop(self, 'import_bookmarks')
        box.prop(self, 'import_users_prefs')
        box.prop(self, 'import_presets')
        box.prop(self, 'import_config_folders')
        box.prop(self, 'import_datafiles_folders')
    
    def execute(self, context):
        return smartconfig_import_config(self.filepath, context, self.import_datafiles_folders, self.import_startup_file, self.install_userfolder, self.import_bookmarks, self.import_users_prefs, self.import_presets, self.import_config_folders)
    
### Import function ###
def smartconfig_import_config(filepath, context, import_datafiles_folders, import_startup_file, install_userfolder, import_bookmarks, import_users_prefs, import_presets, import_config_folders):
    temp=os.path.join(os.path.dirname(filepath), "_sc_temp_")
    chk_p=0
    wrong=[]
    # suppress previous temp folder
    if os.path.isdir(temp)==True:
        try:
            shutil.rmtree(temp)
        except:
            try:
                change_permissions_recursive(temp, 0o777)
                shutil.rmtree(temp)
            except:
                print('Smart Config warning : Unable to delete previous temp folder, please delete it manually')
                chk_p=1
    # create temp folder
    if chk_p==0:
        os.makedirs(os.path.join(os.path.dirname(filepath), "_sc_temp_"))
        # error handler
        try:
            tempfolder=os.path.join(temp, "addons")
            user_path=bpy.utils.resource_path('USER')
            chk2=0
            to_install=[]
            try:
                print()
                print('Smart Config warning : Unpacking File')
                shutil.unpack_archive(filepath, temp, 'zip')
                csvfile=os.path.join(temp, "to_install.txt")
                with open(csvfile, 'r') as f:
                    total=(sum(1 for row in f))
            except shutil.ReadError:
                print('Smart Config warning : Wrong File Format')
                chk2=1
            if chk2==0:
                # addons
                nb=0
                job="Smart Config warning : Importing Addons"
                print()
                if install_userfolder==True:
                    addfolder=bpy.utils.user_resource('SCRIPTS', "addons")
                    addfolder2=os.path.join(bpy.utils.script_paths()[1], "addons")
                else:
                    addfolder=os.path.join(bpy.utils.script_paths()[1], "addons")
                    addfolder2=bpy.utils.user_resource('SCRIPTS', "addons")
                for file in os.listdir(tempfolder):
                    #messages
                    nb+=1
                    chk=0
                    filep=os.path.join(tempfolder,file)
                    if os.path.isfile(filep):
                        for mod in addon_utils.modules():
                            if file==str(mod).split("'")[1]+".py":
                                chk=1
                        for f in os.listdir(addfolder2):
                            if f==file:
                                chk=1
                        if chk==0:
                            shutil.copy2(os.path.join(tempfolder, file), os.path.join(addfolder, os.path.basename(file)))
                    elif os.path.isdir(filep):
                        for f in os.listdir(addfolder):
                            if file==f:
                                chk=1
                        for f in os.listdir(addfolder2):
                            if f==file:
                                chk=1
                        if chk==0:
                            shutil.copytree(os.path.join(tempfolder, file), os.path.join(addfolder, os.path.basename(file)))
                    update_progress_console(job, nb/total)
                with open(csvfile, 'r') as f:
                    for line in f.readlines():
                        name=line.split("\n")[0]
                        if name!="" and name not in bpy.context.user_preferences.addons.keys():
                            try:
                                bpy.ops.wm.addon_enable(module=name)
                            except:
                                try:
                                    addon_utils.disable(name)
                                    bpy.ops.wm.addon_disable(module=name)
                                    bpy.ops.wm.addon_enable(module=name)
                                except:
                                    wrong.append(name)
                    print("Smart Config warning : "+str(total)+" addons activated")
                #startup_file
                if import_startup_file==True:
                    path_s=os.path.join(temp, "startup.blend")
                    if os.path.isfile(path_s)==True:
                        path_d=os.path.join(os.path.join(user_path, "config"),"startup.blend")
                        shutil.copy(path_s, path_d)
                        print('Smart Config warning : Startup File installed')
                # copy bookmarks file
                if import_bookmarks==True:
                    path_s=os.path.join(temp, "bookmarks.txt")
                    if os.path.isfile(path_s)==True:
                        path_d=os.path.join(os.path.join(user_path, "config"),"bookmarks.txt")
                        shutil.copy(path_s, path_d)
                        print('Smart Config warning : Bookmarks File installed')
                # copy userprefs file
                if import_users_prefs==True:
                    path_s=os.path.join(temp, "userpref.blend")
                    if os.path.isfile(path_s)==True:
                        path_d=os.path.join(os.path.join(user_path, "config"),"userpref.blend")
                        shutil.copy(path_s, path_d)
                        print('Smart Config warning : User Preferences File installed')
                # copy presets folder
                if import_presets==True:
                    path_p=os.path.join(temp, "presets")
                    if os.path.isdir(path_p)==True:
                        path_d=os.path.join(os.path.join(user_path, "scripts"),"presets")
                        recursive_copy_dir_tree(path_p, path_d)
                        print('Smart Config warning : Preset Folders installed')
                # copy config folders
                if import_config_folders==True:
                    path_p=os.path.join(temp, "config")
                    if os.path.isdir(path_p)==True:
                        config_d=os.path.join(user_path, "config")
                        recursive_copy_dir_tree(path_p, config_d)
                        print('Smart Config warning : Config Folders installed')
                # copy datafiles folder
                if import_datafiles_folders==True:
                    path_p=os.path.join(temp, "datafiles")
                    if os.path.isdir(path_p)==True:
                        path_d=os.path.join(user_path, "datafiles")
                        recursive_copy_dir_tree(path_p, path_d)
                        print('Smart Config warning : Datafiles Folders installed')
                        
            try:
                shutil.rmtree(temp)
            except:
                try:
                    change_permissions_recursive(temp, 0o777)
                    shutil.rmtree(temp)
                except:
                    print('Smart Config warning : Unable to delete temp folder - Please delete it manually')
            # error report
            if len(wrong)!=0:
                if addon_preferences.errors_report==True:
                    error=os.path.join(os.path.dirname(filepath), (os.path.basename(filepath).split(".sc")[0]+"_import_errors.txt"))
                    errorfile = open(error, "w")
                    errorfile.write("IMPOSSIBLE TO ACTIVATE THESE ADDONS :\n\n")
                    for a in wrong:
                        errorfile.write(a+"\n")
                    errorfile.close()
                for a in wrong:
                    print('Smart Config warning : Addon Problem with - '+a)
                    
            print()
            print('Smart Config warning : Import Finished')
        except:
            shutil.rmtree(temp)
            print('Smart Config warning : Unexpected Error')
    return {'FINISHED'} 
    
### IMPORT MENU
def smart_config_menu_import_config(self, context):
    self.layout.operator('smartconfig.import_config', text="Smart Configuration (.sc)", icon='SCRIPTWIN')