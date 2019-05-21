import bpy
import os
import sys
import shutil

from bpy_extras.io_utils import ExportHelper
from bpy.props import IntProperty, CollectionProperty , StringProperty , BoolProperty, EnumProperty

from .addon_prefs import get_addon_preferences
from .functions import update_progress_console, change_permissions_recursive

### Addons List Props ###
class SmartConfig_Addons_List(bpy.types.PropertyGroup):
    name = StringProperty(name="Module", default="")
    to_avoid = BoolProperty(name="Avoid this addon", default=False)

### Export Config Operator ###
class SmartConfig_Export(bpy.types.Operator, ExportHelper):
    bl_idname = "smartconfig.export_config"
    bl_label = "Export Configuration"
    filename_ext = ".sc"
    filter_glob = StringProperty(default="*.sc", options={'HIDDEN'})
    filepath = StringProperty(default="smart config")
    
    ##### prop #####
    include_startup_file = BoolProperty(
            name="Include Startup File",
            description="Include Blender Startup File in Export",
            default=False,
            )
    include_bookmarks = BoolProperty(
            name="Include Bookmarks File",
            description="Include Blender Bookmarks File in Export",
            default=False,
            )
    include_users_prefs = BoolProperty(
            name="Include User Preferences File",
            description="Include Blender User Preferences File in Export",
            default=False,
            )
    include_presets = BoolProperty(
            name="Include Preset Files",
            description="Include Blender Preset Files in Export",
            default=False,
            )
    include_config_folders = BoolProperty(
            name="Include Configuration Folders",
            description="Include Blender Configuration Folders in Export (some addons use these to save preferences...)",
            default=False,
            )
    include_datafiles_folders = BoolProperty(
            name="Include Datafiles Folders",
            description="Include Blender Datafiles Folders in Export (some addons use these to save presets...)",
            default=False,
            )
    exclude_addons = StringProperty(
            name="Addons to exclude",
            description="Addon Modules to exclude for this export, separated with a comma",
            default="",
            )
    addons_list = CollectionProperty(type=SmartConfig_Addons_List)
    show_list = BoolProperty(
            name="Show list of Addons",
            description="Show list of Addons and select those to be excluded from Export",
            default=False,
            )
         
    
    def __init__(self):
        addon_preferences = get_addon_preferences()
        for mod_name in bpy.context.user_preferences.addons.keys():
            if mod_name not in addon_preferences.exception_list and 'SMART-CONFIG' not in mod_name:
                if addon_preferences.use_trunk_exception==True:
                    if mod_name not in addon_preferences.trunk_exception:
                        new=self.addons_list.add()
                        new.name=mod_name
                else:
                    new=self.addons_list.add()
                    new.name=mod_name
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label('Export Settings :', icon='SCRIPTWIN')
        box.prop(self, 'include_startup_file')
        box.prop(self, 'include_bookmarks')
        box.prop(self, 'include_users_prefs')
        box.prop(self, 'include_presets')
        box.prop(self, 'include_config_folders')
        box.prop(self, 'include_datafiles_folders')
        box2 = box.box()
        row=box2.row(align=True)
        if self.show_list==False:
            row.prop(self, 'show_list', text='', icon='TRIA_RIGHT', emboss=False)
        else:
            row.prop(self, 'show_list', text='', icon='TRIA_DOWN', emboss=False)
        row.label('Addons to exclude')
        row.operator('smartconfig.print_addons', text='', icon='INFO')
        if self.show_list==True:
            col=box2.column(align=True)
            for n in self.addons_list:
                row=col.row(align=True)
                row.label(n.name)
                row.prop(n, 'to_avoid', text='')
        
    def execute(self, context):
        return smartconfig_export_config(self.filepath, context, self.include_datafiles_folders, self.addons_list, self.include_startup_file, self.include_bookmarks, self.include_users_prefs, self.include_presets, self.include_config_folders)
    

### Export function ###
def smartconfig_export_config(filepath, context, include_datafiles_folders, addons_list, include_startup_file, include_bookmarks, include_users_prefs, include_presets, include_config_folders):
    addon_preferences = get_addon_preferences()
    exception=[]
    wrong=[]
    if addon_preferences.use_trunk_exception==True:
        for f in addon_preferences.trunk_exception.split(","):
            exception.append(f)
    if addon_preferences.exception_list!="":
        for f in addon_preferences.exception_list.split(","):
            exception.append(f)
        
    # clean old files
    chk_p=0
    if os.path.isfile(filepath)==True:
        try:
            os.remove(filepath)
        except:
            try:
                change_permissions_recursive(filepath, 0o777)
                os.remove(filepath)
            except:
                print('Smart Config warning : Unable to delete previous file, please delete it manually')
                chk_p=1
    tempdir=os.path.join((os.path.dirname(filepath)), (os.path.basename(filepath).split(".sc")[0]+"_temp_"))
    if os.path.isdir(tempdir):
        try:
            shutil.rmtree(tempdir)
        except:
            try:
                change_permissions_recursive(tempdir, 0o777)
                shutil.rmtree(tempdir)
            except:
                print('Smart Config warning : Unable to delete previous file, please delete it manually')
                chk_p=1
                
    if chk_p==0:
        # create tempdir to copy files
        os.makedirs(tempdir)
        os.makedirs(os.path.join(tempdir, "addons"))
        addondir=os.path.join(tempdir, "addons")
        user_path=bpy.utils.resource_path('USER')
        total=len(bpy.context.user_preferences.addons.keys())
        nb=0
        job="Smart Config warning : Exporting Addons"
        print()
        #create csv file
        csvfile=os.path.join(tempdir, "to_install.txt")
        nfile = open(csvfile, "w")
        # copy addons
        for mod_name in bpy.context.user_preferences.addons.keys():
            nb+=1
            chk3=0
            if 'SMART-CONFIG' in mod_name:
                chk3=1
            else:
                for a in addons_list:
                    if a.to_avoid==True and a.name==mod_name:
                        chk3=1
                if chk3==0:
                    for e in exception:
                        if e==mod_name:
                            chk3=1
            if chk3==0:
                chk4=0
                try:
                    mod = sys.modules[mod_name]
                    chk4=1
                except KeyError:
                    wrong.append(mod_name)
                if chk4==1:
                    nfile.write(mod_name+"\n")
                    path_s=os.path.abspath(mod.__file__)
                    #single file addon
                    if os.sep not in path_s.split("addons"+os.sep)[1]:
                        path_d=os.path.join(addondir, (path_s.split("addons"+os.sep)[1]))
                        shutil.copy2(path_s, path_d)
                    #multi file addon
                    else:
                        folder_name=(path_s.split("addons"+os.sep)[1]).split(os.sep)[0]
                        path_fs=os.path.dirname(path_s)
                        path_fd=os.path.join(addondir,folder_name)
                        shutil.copytree(path_fs, path_fd)
            update_progress_console(job, nb/total)
        #close csv
        nfile.close()
        # copy startup file
        if include_startup_file==True:
            path_s=os.path.join(os.path.join(user_path, "config"),"startup.blend")
            path_d=os.path.join(tempdir, "startup.blend")
            shutil.copy2(path_s, path_d)
        # copy bookmarks file
        if include_bookmarks==True:
            path_s=os.path.join(os.path.join(user_path, "config"),"bookmarks.txt")
            path_d=os.path.join(tempdir, "bookmarks.txt")
            shutil.copy2(path_s, path_d)
        # copy userprefs file
        if include_users_prefs==True:
            path_s=os.path.join(os.path.join(user_path, "config"),"userpref.blend")
            path_d=os.path.join(tempdir, "userpref.blend")
            shutil.copy2(path_s, path_d)
        # copy presets folder
        if include_presets==True:
            path_s=os.path.join(os.path.join(user_path, "scripts"),"presets")
            path_d=os.path.join(tempdir, "presets")
            shutil.copytree(path_s, path_d)
        # copy datafiles folder
        if include_datafiles_folders==True:
            path_s=os.path.join(user_path, "datafiles")
            path_d=os.path.join(tempdir, "datafiles")
            shutil.copytree(path_s, path_d)
        # copy config folders
        if include_config_folders==True:
            config=os.path.join(user_path, "config")
            config_d=os.path.join(tempdir, "config")
            for file in os.listdir(config):
                if os.path.isdir(os.path.join(config,file))==True:
                    path_s=os.path.join(config, file)
                    path_d=os.path.join(config_d, file)
                    shutil.copytree(path_s, path_d)
        # create zip and delete temp
        print("Smart Config warning : Creating Archive")
        zipfile=shutil.make_archive(filepath, 'zip', tempdir)
        try:
            shutil.rmtree(tempdir)
        except:
            try:
                change_permissions_recursive(tempdir, 0o777)
                shutil.rmtree(tempdir)
            except:
                print('Smart Config warning : Unable to delete temp folder - Please delete it manually')
        basezip = os.path.splitext(zipfile)[0]
        os.rename(zipfile, basezip)
        
        print()
        print('Smart Config warning : Export Completed')
        #error reporting
        if len(wrong)!=0:
            if addon_preferences.errors_report==True:
                error=os.path.join(os.path.dirname(filepath), (os.path.basename(filepath).split(".sc")[0]+"_export_errors.txt"))
                errorfile = open(error, "w")
                errorfile.write("PROBLEMATIC'S ADDONS :\n\n")
                for a in wrong:
                    errorfile.write(a+"\n")
                errorfile.close()
            for a in wrong:
                print('Smart Config warning : Addon Problem with - '+a)
    
    else:
        print('Smart Config warning : Unexpected Error')
            
    return {'FINISHED'} 
    
### EXPORT CONFIGURATION MENU
def smart_config_menu_export_config(self, context):
    self.layout.operator('smartconfig.export_config', text="Smart Configuration (.sc)", icon='SCRIPTWIN')