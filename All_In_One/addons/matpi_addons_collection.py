# ##### BEGIN GPL LICENSE BLOCK #####
#
#  matpi_addons_collection.py
#  Global configurator and downloader for Matpi's addons collection
#  Copyright (C) 2015 Quentin Wenger
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####



bl_info = {"name": "Matpi's Add-ons Collection (Configurator)",
           "description": "Global configurator and downloader for Matpi's addons collection",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 1),
           "blender": (2, 73, 0),
           "location": "User Preferences -> Add-ons -> Matpi's Addons Collection (Configurator) -> Preferences",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "System"
           }


base_url = "https://raw.githubusercontent.com/qwenger/BAddons/master/%s"
addons_list_name = "ADDONS_LIST.pkl"
prefs_name = "PREFERENCES.pkl"
self_name = "matpi_addons_collection.py"


#TODO: props to redefault at unregister
# -> matpiaddonprops
# -> really wanted?

#TODO: is_expanded as attr of addonwrapper
# -> operators (expand, unexpand)
# -> no need for addons_list
# -> ATM kept because maybe other per-addon bpy props needed?

import bpy
import addon_utils
import os
import sys
import shutil
import urllib.error
import urllib.request
import pickle
import importlib



addons = {}




class ReportOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_report"
    bl_label = "Report"

    report_text = ""
    report_icon = 'INFO'

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({self.report_icon}, self.report_text)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)

    def draw(self, context):
        self.layout.label("Refreshing Info")
        row = self.layout.row()
        row.label(icon=self.report_icon, text=self.report_text)

    
    


def reportConnectivityError():
    bpy.types.WM_OT_matpi_addons_report.report_text = "Couldn't access to online repo." \
        " Please check your internet connectivity."
    bpy.ops.wm.matpi_addons_report('INVOKE_DEFAULT')


def reportPathNotEmpty():
    bpy.types.WM_OT_matpi_addons_report.report_text = "Addons path" \
        " %s is not empty, won't be deleted." % bpy.context.window_manager.matpi_addons_props.addons_path
    bpy.ops.wm.matpi_addons_report('INVOKE_DEFAULT')
    



def retrieveFileFromURL(url):

    try:
        return urllib.request.urlopen(url).read().decode().replace("\r\n", "\n")

    except urllib.error.URLError:
        reportConnectivityError()
        return None



def retrieveOnlineRepoStructure():

    struct_url = base_url % addons_list_name

    try:
        return pickle.loads(urllib.request.urlopen(struct_url).read())

    except urllib.error.URLError:
        reportConnectivityError()
        return None




def retrieveLocalRepoStructure():

    path = bpy.context.window_manager.matpi_addons_props.addons_path

    addons = {}

    if os.path.exists(path):

        current_dir = os.getcwd()

        if not "" in sys.path:
            sys.path.append("")

        for item in os.listdir(path):
        
            if os.path.isdir(os.path.join(path, item)):
                if os.path.exists(os.path.join(path, item, "__init__.py")):
                    os.chdir(os.path.join(path))
                    mod = importlib.import_module(item)
                    # XXX: for some reason, following line needed. Bug?
                    mod = importlib.reload(mod)
                    info = mod.bl_info
                    del mod

                else:
                    os.chdir(os.path.join(path, item))
                    first_file = os.listdir()[0].split(".")[0]
                    mod = importlib.import_module(first_file)
                    # XXX: for some reason, following line needed. Bug?
                    mod = importlib.reload(mod)
                    info = mod.bl_info
                    del mod

                addons[item] = info

        os.chdir(current_dir)
        

    return addons





def installAddonFolder(struct, local_path, online_path):
    try:
        os.mkdir(local_path)
    except FileNotFoundError:
        return False

    for file_ in struct["_files"]:
        data = retrieveFileFromURL(online_path % file_)

        if data is None:
            return False

        with open(os.path.join(local_path, file_), "w") as f:
            f.write(data)
    
    for dir_ in struct["_dirs"]:
        success = installAddonFolder(struct["_dirs"][dir_], os.path.join(local_path, dir_), online_path % (dir_ + "%s"))

        if not success:
            return False

    return True


def installFile(local_path, online_path):
    data = retrieveFileFromURL(online_path)

    if data is None:
        return False

    with open(local_path, "w") as f:
        f.write(data)

    return True


class StaticPreferences(object):
    def __init__(self):
        self.initialized = False
        self.addons_enabled = []


def retrieveStaticPreferences(default_addons_path=None):
    if default_addons_path is None:
        addons_path = bpy.context.window_manager.matpi_addons_props.addons_path
    else:
        addons_path = default_addons_path

    name = os.path.join(addons_path, prefs_name)

    if os.path.exists(name):
        with open(name, "rb") as f:
            return pickle.load(f)
    else:
        return StaticPreferences()


def saveStaticPreferences(static_pref):
    addons_path = bpy.context.window_manager.matpi_addons_props.addons_path
    name = os.path.join(addons_path, prefs_name)

    if os.path.exists(addons_path):
        with open(name, "wb") as f:
            pickle.dump(static_pref, f, 4)

        

class MatpiAddonWrapper(object):
        
    def __init__(self, addon_name, info, is_installed=False):

        self.is_installed = is_installed
        self.name = addon_name

        self.file_name = None

        self.info = info

        self.local_version = []
        self.online_version = []

        self.is_updatable = False

        self.is_enabled = False

        self.mod = None

        self.index = id(self)

        class EnableAddonOperator(bpy.types.Operator):
            bl_idname = "wm.mcollection_addon_enable%s" % self.index
            bl_label = "Enable"
            bl_options = {'INTERNAL'}

            @classmethod
            def poll(cls, context):
                return not self.is_enabled

            def execute(op_self, context):
                self.enable()
                return {'FINISHED'}


        class DisableAddonOperator(bpy.types.Operator):
            bl_idname = "wm.mcollection_addon_disable%s" % self.index
            bl_label = "Disable"
            bl_options = {'INTERNAL'}

            @classmethod
            def poll(cls, context):
                return self.is_enabled

            def execute(op_self, context):
                self.disable()
                return {'FINISHED'}

            
        class InstallAddonOperator(bpy.types.Operator):
            bl_idname = "wm.mcollection_addon_install%s" % self.index
            bl_label = "Install"
            bl_options = {'INTERNAL'}

            @classmethod
            def poll(cls, context):
                return not self.is_installed

            def execute(op_self, context):
                self.install(context)
        
                return {'FINISHED'}


        class UninstallAddonOperator(bpy.types.Operator):
            bl_idname = "wm.mcollection_addon_uninstall%s" % self.index
            bl_label = "Uninstall"
            bl_options = {'INTERNAL'}

            @classmethod
            def poll(cls, context):
                return self.is_installed

            def execute(op_self, context):
                self.uninstall(context)
                return {'FINISHED'}


        class UpdateAddonOperator(bpy.types.Operator):
            bl_idname = "wm.mcollection_addon_update%s" % self.index
            bl_label = "Update"
            bl_options = {'INTERNAL'}

            @classmethod
            def poll(cls, context):
                return self.is_updatable

            def execute(op_self, context):
                self.update(context)
                #op_self.report({'INFO'}, str(self.index))

                #self.is_installed = False
                
                return {'FINISHED'}


        self.operators = (
            EnableAddonOperator,
            DisableAddonOperator,
            InstallAddonOperator,
            UninstallAddonOperator,
            UpdateAddonOperator)


        self.register()
        

    
    def draw(self, context, layout):
        box = layout.box()
        top_row = box.row()

        for prop in context.window_manager.matpi_addons_list:
            if prop.addon_name == self.name:
                break

        if prop.is_expanded:
            top_row.prop(prop, "is_expanded", icon='TRIA_DOWN',
                icon_only=True, text="", emboss=False)

            col = box.column()
            
            split = col.row().split(percentage=0.15)
            split.label(text="Description:")
            split.label(text=self.info["description"])

            split = col.row().split(percentage=0.15)
            split.label(text="Location:")
            split.label(text=self.info["location"])

            if self.local_version:
                split = col.row().split(percentage=0.15)
                split.label(text="Local Version:")
                split.label(text=".".join(str(n) for n in self.local_version), translate=False)

            if self.online_version:
                split = col.row().split(percentage=0.15)
                split.label(text="Online Version:")
                split.label(text=".".join(str(n) for n in self.online_version), translate=False)
            
            if self.info["warning"]:
                split = col.row().split(percentage=0.15)
                split.label(text="Warning:")
                split.label(text='  ' + self.info["warning"], icon='ERROR')
            
        else:
            top_row.prop(prop, "is_expanded", icon='TRIA_RIGHT',
                icon_only=True, text="", emboss=False)

        
        split = top_row.split(percentage=0.6)

        split.label(text=self.info["name"])
        sub_row = split.row()

        if self.is_installed:
            sub_sub_row = sub_row.row(align=True)
            sub_sub_row.operator("wm.mcollection_addon_uninstall%s" % self.index, icon='X')

            if self.is_updatable:
                sub_sub_row.operator("wm.mcollection_addon_update%s" % self.index, icon='FF')

            if self.is_enabled:
                sub_row.operator("wm.mcollection_addon_disable%s" % self.index, icon='CHECKBOX_HLT',
                    text="", emboss=False)
                
            else:
                sub_row.operator("wm.mcollection_addon_enable%s" % self.index, icon='CHECKBOX_DEHLT',
                    text="", emboss=False)

        else:
            sub_row.operator("wm.mcollection_addon_install%s" % self.index, icon='NLA_PUSHDOWN')

    
    def register(self):
        for op in self.operators:
            try:
                bpy.utils.register_class(op)
            except RuntimeError:
                print("Could not register: %s" % op.bl_idname)


    def unregister(self):
        for op in self.operators:
            try:
                bpy.utils.unregister_class(op)
            except RuntimeError:
                print("Could not unregister: %s" % op.bl_idname)
    

    def update(self, context):
        status = self.is_enabled

        self.uninstall(context)
        self.install(context)

        self.is_updatable = False

        if status:
            self.enable()


    def install(self, context):
        online_struct = retrieveOnlineRepoStructure()

        if online_struct is not None:
            path = bpy.context.window_manager.matpi_addons_props.addons_path
            local_path = os.path.join(path, self.name)
            online_path = base_url % (self.name + "/%s")

            success = installAddonFolder(online_struct["_addons"][self.name], local_path, online_path)

            if not success:
                try:
                    shutil.rmtree(local_path)
                except FileNotFoundError:
                    pass
                return

            self.info = online_struct["_addons"][self.name]["_info"]
            self.online_version = self.info["version"]
            self.local_version = self.online_version

            self.is_enabled = False
            self.is_installed = True
            

            bpy.ops.wm.matpi_addons_refresh()


    def uninstall(self, context):
        if self.is_enabled:
            self.disable()

        path = bpy.context.window_manager.matpi_addons_props.addons_path

        try:
            shutil.rmtree(os.path.join(path, self.name))
        except FileNotFoundError:
            pass

        self.is_enabled = False
        self.is_installed = False


    def enable(self):

        path = bpy.context.window_manager.matpi_addons_props.addons_path

        try:
            if os.path.exists(os.path.join(path, self.name, "__init__.py")):
                self.file_name = self.name

            else:
                addon_path = os.path.join(path, self.name)
                if addon_path not in sys.path:
                    sys.path.append(addon_path)
                self.file_name = os.listdir(addon_path)[0].split(".")[0]

            self.mod = importlib.import_module(self.file_name)
            self.mod.register()
            self.is_enabled = True

            static_prefs = retrieveStaticPreferences()
            static_prefs.addons_enabled.append(self.name)
            saveStaticPreferences(static_prefs)

        except (ImportError, FileNotFoundError):
            pass


    def disable(self):

        if self.mod is not None:
            self.mod.unregister()
            self.mod = None

        self.is_enabled = False


        static_prefs = retrieveStaticPreferences()
        static_prefs.addons_enabled.remove(self.name)
        saveStaticPreferences(static_prefs)
        


class InitializeOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_initialize"
    bl_label = "Initialize"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = context.window_manager.matpi_addons_props
            
        if not os.path.exists(props.addons_path):
            os.makedirs(props.addons_path)    
            self.report({'INFO'}, "Created folder %s" % props.addons_path)

        if not props.addons_path in sys.path:
            sys.path.append(props.addons_path)

        props.initialized = True

        static_prefs = retrieveStaticPreferences()
        static_prefs.initialized = True
        saveStaticPreferences(static_prefs)

        return {'FINISHED'}



class RefreshOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_refresh"
    bl_label = "Refresh"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.matpi_addons_props
        return props.initialized

    def execute(self, context):

        # update addons infos from online repo

        online_struct = retrieveOnlineRepoStructure()

        props = context.window_manager.matpi_addons_props
        addons_list = context.window_manager.matpi_addons_list

        if online_struct is None:
            connected = False

        else:
            connected = True
            for addon_name in online_struct["_addons"]:
                if addon_name in addons:
                    addon_wrapper = addons[addon_name]
                    addon_wrapper.info = online_struct["_addons"][addon_name]["_info"]
                else:
                    addon_wrapper = MatpiAddonWrapper(addon_name, online_struct["_addons"][addon_name]["_info"], False)
                    addons[addon_name] = addon_wrapper
                    addon_prop = addons_list.add()
                    addon_prop.addon_name = addon_name

                addon_wrapper.online_version = online_struct["_addons"][addon_name]["_info"]["version"]

        # update the master from online repo

        online_version = online_struct["_system_files"][self_name]
        props.online_version = ".".join(str(n) for n in online_version)

        if online_version > bl_info["version"]:
            props.updatable = True

        # update addons infos from local repo

        local_struct = retrieveLocalRepoStructure()

        for addon_name, info in local_struct.items():
            if addon_name in addons:
                addon_wrapper = addons[addon_name]
                addon_wrapper.info = info

            else:
                addon_wrapper = MatpiAddonWrapper(addon_name, info, False)
                addons[addon_name] = addon_wrapper
                addon_prop = addons_list.add()
                addon_prop.addon_name = addon_name

            addon_wrapper.local_version = info["version"]
            addon_wrapper.is_updatable = tuple(addon_wrapper.online_version) > tuple(addon_wrapper.local_version)

                
        # delete outdated addons (only if connected)

        if connected:
            for addon_prop in addons_list:
                name = addon_prop.addon_name
                if name not in online_struct["_addons"] and name not in local_struct:
                    addons[name].disable()
                    addons[name].unregister()
                    del addons[name]
                    addons_list.remove(addon_prop)

        return {'FINISHED'}


class InstallAllOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_installall"
    bl_label = "Install All"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return any(not addon.is_installed for addon in addons.values())

    def execute(self, context):
        for addon in addons.values():
            if not addon.is_installed:
                addon.install(context)
        
        return {'FINISHED'}


class UninstallAllOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_uninstallall"
    bl_label = "Uninstall All"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return any(addon.is_installed for addon in addons.values())

    def execute(self, context):
        for addon in addons.values():
            if addon.is_installed:
                addon.uninstall(context)
                
        bpy.ops.wm.matpi_addons_refresh()
        
        return {'FINISHED'}


class EnableAllOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_enableall"
    bl_label = "Enable All Installed"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return any(not addon.is_enabled for addon in addons.values())

    def execute(self, context):
        for addon in addons.values():
            if addon.is_installed and not addon.is_enabled:
                addon.enable()
        
        return {'FINISHED'}


class DisableAllOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_disableall"
    bl_label = "Disable All Installed"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return any(addon.is_enabled for addon in addons.values() if addon.is_installed)

    def execute(self, context):
        for addon in addons.values():
            if addon.is_installed and addon.is_enabled:
                addon.disable()
        
        return {'FINISHED'}


class UpdateAllOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_updateall"
    bl_label = "Update All Installed"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return any(addon.is_updatable for addon in addons.values() if addon.is_installed)

    def execute(self, context):
        for addon in addons.values():
            if addon.is_installed and addon.is_updatable:
                addon.update(context)

        bpy.ops.wm.matpi_addons_refresh()

        return {'FINISHED'}



class UpdateMasterOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_updatemaster"
    bl_label = "Update Configurator"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.matpi_addons_props
        return props.updatable

    def execute(self, context):
        props = context.window_manager.matpi_addons_props

        path = props.addons_path
        local_path = os.path.join(path, self_name)
        online_path = base_url % self_name

        success = installFile(local_path, online_path)

        if not success:
            try:
                shutil.rmtree(local_path)
            except FileNotFoundError:
                pass
            return {'CANCELLED'}

        props.updatable = False

        return {'FINISHED'}



class RemoveFolderOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_removefolder"
    bl_label = "Remove Folder"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.matpi_addons_props.initialized

    def execute(self, context):
        props = context.window_manager.matpi_addons_props

        for addon in addons.values():
            if addon.is_installed:
                addon.uninstall(context)
            #addon.unregister()

        try:
            shutil.rmtree(props.addons_path)
        except FileNotFoundError:
            pass
        
        props.initialized = False
        
        return {'FINISHED'}



class CopyFilePathOperator(bpy.types.Operator):
    bl_idname = "wm.matpi_addons_copyfilepath"
    bl_label = "Copy File Path"
    bl_description = "Click to copy Path to Clipboard"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.matpi_addons_props
        return props.initialized and props.online_version > ".".join(str(n) for n in bl_info["version"]) and not props.updatable

    def execute(self, context):
        props = context.window_manager.matpi_addons_props
        text = os.path.join(props.addons_path, self_name)
        context.window_manager.clipboard = text
        self.report({'INFO'}, "Copied Path to Clipboard")
        return {'FINISHED'}



class MatpiAddonsCollectionPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__


    def draw(self, context):
        layout = self.layout
        
        props = context.window_manager.matpi_addons_props

        if props.initialized:
            row = layout.row()

            split = row.split(percentage=0.15)
            split.label(text="Folder Path:")
            split2 = split.split(percentage=0.8)
            split2.label(text=props.addons_path)
            split2.operator("wm.matpi_addons_removefolder", icon='CANCEL')

            if props.online_version > ".".join(str(n) for n in bl_info["version"]):
                layout.separator()
                if props.updatable:
                    row = layout.row()
                    split = row.split()
                    split.label(text="Online Version is newer (%s)." % props.online_version, icon='INFO')
                    split.operator("wm.matpi_addons_updatemaster")
                else:
                    col = layout.column()
                    col.label(text="Master Addon updated on disk, you should reinstall it from path (click to copy to Clipboard):", icon='ERROR')
                    col.operator("wm.matpi_addons_copyfilepath", text=os.path.join(props.addons_path, self_name), emboss=False)

            layout.separator()
            
            row = layout.row()
            split = row.split()

            col = split.column()
            col.operator("wm.matpi_addons_refresh", icon='FILE_REFRESH')
            col.operator("wm.matpi_addons_updateall", icon='FF')

            col = split.column(align=True)
            col.operator("wm.matpi_addons_installall", icon='NLA_PUSHDOWN')
            col.operator("wm.matpi_addons_uninstallall" ,icon='X')

            col = split.column(align=True)
            col.operator("wm.matpi_addons_enableall", icon='CHECKBOX_HLT')
            col.operator("wm.matpi_addons_disableall", icon='CHECKBOX_DEHLT')


            layout.separator()

            for addon in addons.values():
                addon.draw(context, layout)

        else:
            col = layout.column()
            col.label("The addons will be saved in:")
            col.label("%s" % props.addons_path)

            row = layout.row()
            row.operator("wm.matpi_addons_initialize")
    
        

    
    @classmethod
    def register(cls):
        pass

        #cls.initialized = False


    @classmethod
    def unregister(cls):
        pass

        """
        for addon in cls.addons:
            addon.unregister()
        """
    

    



def register():

    default_addons_path = os.path.normpath(
        os.path.join(bpy.utils.script_paths()[-1], "matpi_addons"))

    static_prefs = retrieveStaticPreferences(default_addons_path)
    

    class MatpiAddon(bpy.types.PropertyGroup):

        addon_name = bpy.props.StringProperty(
            name="Addon Name",
            description="",
            default="")

        is_expanded = bpy.props.BoolProperty(
            name="is_expanded",
            description="",
            default=False)
        

    class MatpiAddonsProps(bpy.types.PropertyGroup):
        """
        bpy.context.user_preferences.matpi_addons_props
        """
        initialized = bpy.props.BoolProperty(
            name="Initialized",
            description="",
            default=static_prefs.initialized)
        
        addons_path = bpy.props.StringProperty(
            name="Path",
            description="",
            default=default_addons_path)

        updatable = bpy.props.BoolProperty(
            name="Updatable",
            description="",
            default=False)

        online_version = bpy.props.StringProperty(
            name="Online Version",
            description="",
            default=".".join(str(n) for n in bl_info["version"]))
        

    bpy.utils.register_module(__name__)

    bpy.types.WindowManager.matpi_addons_props = bpy.props.PointerProperty(type=MatpiAddonsProps)
    bpy.types.WindowManager.matpi_addons_list = bpy.props.CollectionProperty(type=MatpiAddon)

    # retrieve local existing addons
    
    addons_struct = retrieveLocalRepoStructure()

    addons_list = bpy.context.window_manager.matpi_addons_list
        
    for addon_name, info in addons_struct.items():
        addon_wrapper = MatpiAddonWrapper(addon_name, info, True)
        addon_wrapper.local_version = info["version"]
        addons[addon_name] = addon_wrapper
        
        addon_prop = addons_list.add()
        addon_prop.addon_name = addon_name
        
        if addon_name in static_prefs.addons_enabled:
            addon_wrapper.enable()
        

def unregister():
    for addon in addons.values():
        addon.unregister()
        
    bpy.utils.unregister_module(__name__)

    if hasattr(bpy.context.window_manager, "matpi_addons_props"):
        del bpy.types.WindowManager.matpi_addons_props
    if hasattr(bpy.context.window_manager, "matpi_addons_list"):
        del bpy.types.WindowManager.matpi_addons_list
    
