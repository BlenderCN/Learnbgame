'''
Addon Development Tool
Copyright 2015 Nathan Craddock

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Addon Development Tool",
    "description": "Removes redundancy and repetition in the creating and testing of Blender addons",
    "author": "Nathan Craddock",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "Properties shelf of the text editor",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Text Editor"
}

import bpy
from bpy.types import Panel, AddonPreferences, PropertyGroup, UIList, Operator
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.app.handlers import persistent

import os
import zipfile
import json


#######################################################################################
# FUNCTIONS
#######################################################################################

@persistent
def get_projects(dummy):
    # Import projects from JSON file
    projects_file = bpy.utils.script_path_user() + os.sep + "ADTProjects.json"
    project_list = bpy.context.scene.project_list
    names = [p.name for p in project_list]

    with open(projects_file) as readfile:
        projects = json.load(readfile)

    for p in projects:
        if p[0] not in names:
            bpy.context.scene.project_list.add()
            bpy.context.scene.project_list_index = len(bpy.context.scene.project_list) - 1
            bpy.context.scene.project_list[bpy.context.scene.project_list_index].name = p[0]
            bpy.context.scene.project_list[bpy.context.scene.project_list_index].location = p[1]
            bpy.context.scene.project_list[bpy.context.scene.project_list_index].is_addon = True


@persistent
def save_projects(dummy):
    # Save project list to a JSON file
    projects_file = bpy.utils.script_path_user() + os.sep + "ADTProjects.json"
    project_list = bpy.context.scene.project_list
    
    # Don't save if there aren't any addons
    if len(bpy.context.scene.project_list) is not 0:
        projects = []

        for p in project_list:
            project = [p.name, p.location, p.is_addon]

            projects.append(project)

        with open(projects_file, 'w') as savefile:
            json.dump(projects, savefile)


def get_files(context, ending=""):
    # Return a list with of the files from the current project
    project = context.scene.project_list[context.scene.project_list_index]
    path = bpy.path.abspath(project.location)

    project_files = []
    # For single-file addons
    if os.path.isfile(path):
        file = os.path.basename(path)
        if file.endswith(ending):
            project_files.append(file)

    # Multi-file addons
    else:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if name.endswith(ending):
                    project_files.append(os.path.join(root, name).replace(path, ""))

    return project_files

def get_file_names(file_paths):
    file_names = []
    for file in file_paths:
        file_names.append(os.path.basename(file))
        
    return file_names

def close_files(context, all):
    # Closes files
    # All will toggle between all files, or the files in the project

    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            if all:
                for file in bpy.data.texts:
                    # Make the file the active file in the text editor
                    area.spaces[0].text = file

                    bpy.ops.text.unlink()
            else:
                files = get_file_names(get_files(context, '.py'))
                for file in bpy.data.texts:
                    if file.name in files:
                        # Make the file the active file in the text editor
                        area.spaces[0].text = file

                        bpy.ops.text.unlink()
            break

def is_project_valid(context):
    # Checks if addon has a bl_info
    # If a package, check for __init__.py
    # Returns a list
    info = []
    mainfile = ""
    
    project = context.scene.project_list[context.scene.project_list_index]
    path = bpy.path.abspath(project.location)
    
    # Determine whether it is a multifile addon and get mainfile name
    if os.path.isdir(path):
        if '__init__.py' not in os.listdir(path):
            info.append("missing __init__.py")
            
        else:
            mainfile = path + os.sep + '__init__.py'
            found = False
            
            with open(mainfile) as f:
                for line in iter(f):
                    l = line.replace(' ', '')
                    if l.startswith('bl_info'):
                        found = True
                        break
            
            if not found:
                info.append('missing bl_info')
    else:
        mainfile = path
        
        if os.path.basename(path) == "__init__.py":
            info.append("__init__.py is only for packages")
    
        found = False
        with open(mainfile) as f:
            for line in iter(f):
                l = line.replace(' ', '')
                if l.startswith('bl_info'):
                    found = True
                    break
                
        if not found:
            info.append('missing bl_info')
                
    #return info
    return []

def zip_project(location, files, path, name):
    # Saves specified folder to specified location as a zip file
    zip = zipfile.ZipFile(location, 'w')

    for file in files:
        zip.write(path + file, name + os.sep + file)

    zip.close()
    

#######################################################################################
# UI
#######################################################################################            

class AddonDevelopmentProjectPanel(Panel):
    """ Creates a panel in the text editor """
    bl_label = "Addon Development Tool"
    bl_idname = "TEXT_PT_addon_dev"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        project_list = context.scene.project_list
        list_index = context.scene.project_list_index

        layout = self.layout

        row = layout.row()
        row.template_list("AddonProjectUIList", "", context.scene, "project_list", context.scene, "project_list_index",
                          rows=5)

        row = layout.row(align=True)
        row.operator('addon_dev_tool.new_addon')
        #row.operator('addon_dev_tool.new_script')
        row.operator('addon_dev_tool.delete_project')

        # Only if a valid project is selected
        if list_index >= 0 and len(project_list) > 0:
            item = project_list[list_index]
            
            if not os.path.exists(item.location):
                layout.prop(item, 'location', icon='ERROR')
            else:
                layout.prop(item, 'location')

            if not item.location == "" and os.path.exists(bpy.path.abspath(item.location)):
                layout.separator()

                col = layout.column(align=True)
                row = col.row(align=True)
                row.operator('addon_dev_tool.open_files')
                row.operator('addon_dev_tool.close_files')

                row = col.row(align=True)
                row.operator('addon_dev_tool.new_project_file')
                row.operator('addon_dev_tool.close_all_files')

                row = col.row(align=True)
                row.operator('addon_dev_tool.refresh_files', icon='FILE_REFRESH')

                layout.separator()
                col = layout.column(align=True)
                if item.is_addon:
                    col.operator('addon_dev_tool.install_addon')
                    col.operator('addon_dev_tool.remove_addon')
                else:
                    row.operator('addon_dev_tool.run_script')
                    
                row = layout.row()
                row.operator('addon_dev_tool.export')

                # Info Box
                info = is_project_valid(context)
                if len(info) > 0:
                    box = layout.box()
                    for i in info:
                        box.label(text=i)
                

    def draw_header(self, context):
        """ Just for fun """
        layout = self.layout
        # layout.label(icon='FILE_TEXT')


class Project(PropertyGroup):
    """ Holds location, name, etc of each project """

    name = StringProperty(name="Name", description="The name of the current project", default="untitled")

    location = StringProperty(name="Location", description="The location of the project on the users machine",
                              default="", subtype='FILE_PATH')

    is_addon = BoolProperty(name="Addon", description="Is the project a script or an addon?", default=True)

    project_files = []


class AddonProjectUIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        addon_icon = 'FILE_TEXT'
        script_icon = 'FILE_SCRIPT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            if item.is_addon:
                layout.prop(item, 'name', emboss=False, icon=addon_icon)
            else:
                layout.prop(item, 'name', emboss=False, icon=script_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon=addon_icon)
            
            
#######################################################################################
# OPERATORS
#######################################################################################
class ADTNewAddon(Operator):
    bl_label = "New Addon"
    bl_idname = "addon_dev_tool.new_addon"
    bl_description = "Create a new addon"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.project_list.add()
        context.scene.project_list_index = len(context.scene.project_list) - 1
        context.scene.project_list[context.scene.project_list_index].is_addon = True

        return {'FINISHED'}


class ADTNewScript(Operator):
    bl_label = "New Script"
    bl_idname = "addon_dev_tool.new_script"
    bl_description = "Create a new script"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.project_list.add()
        context.scene.project_list_index = len(context.scene.project_list) - 1
        context.scene.project_list[context.scene.project_list_index].is_addon = False

        return {'FINISHED'}


class ADTDeleteProject(Operator):
    bl_label = "Delete Project"
    bl_idname = "addon_dev_tool.delete_project"
    bl_description = "Remove project from list (Will not delete files)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        """ You can only delete if there is something in the list!"""
        return len(context.scene.project_list) > 0

    def execute(self, context):
        list = context.scene.project_list
        index = context.scene.project_list_index

        list.remove(index)

        if index > 0:
            context.scene.project_list_index = index - 1

        return {'FINISHED'}


class ADTOpenFiles(Operator):
    bl_label = "Open Project Files"
    bl_idname = 'addon_dev_tool.open_files'
    bl_description = "Open files from current project in the text editor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        file_names = get_file_names(get_files(context, '.py'))

        unopened = False

        for name in file_names:
            if name not in bpy.data.texts:
                unopened = True

        return unopened

    def execute(self, context):
        project = bpy.context.scene.project_list[bpy.context.scene.project_list_index]
        path = bpy.path.abspath(project.location)

        # Open files in the text editor from the current project
        files = get_files(context, '.py')

        for file in files:
            if file not in bpy.data.texts:
                if os.path.isdir(path):
                    bpy.ops.text.open(filepath=path + file)
                elif os.path.isfile(path):
                    bpy.ops.text.open(filepath=path)

        return {'FINISHED'}


class ADTNewProjectFile(Operator, ExportHelper):
    bl_label = "New Project File"
    bl_idname = 'addon_dev_tool.new_project_file'
    bl_description = "Create a new file for the project and open it in the editor"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".py"
    
#    @classmethod
#    def poll(self, context):
#        # Make sure it is a multi file addon
#        location = context.scene.project_list[context.scene.project_list_index].location
#        
#        if os.path.isdir(location):
#            return True

    # Set the filepath to the project location
    def invoke(self, context, event):
        location = context.scene.project_list[context.scene.project_list_index].location

        if self.filepath == "":
            self.filepath = location

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Create the file
        print("Creating", self.filepath)
        f = open(self.filepath, 'w', encoding='utf-8')
        f.close()

        # Open the file in the text editor
        text = bpy.data.texts.load(self.filepath)

        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces[0].text = text
                break

        return {'FINISHED'}


class ADTCloseFiles(Operator):
    bl_label = "Close Project Files"
    bl_idname = 'addon_dev_tool.close_files'
    bl_description = "Close files from current project in the text editor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        sce = context.scene
        files = get_files(context, 'py')
        files_open = False

        for file in bpy.data.texts:
            if file.name in files:
                files_open = True

        return files_open

    def execute(self, context):
        close_files(context, False)

        return {'FINISHED'}


class ADTCloseAllFiles(Operator):
    bl_label = "Close All Files"
    bl_idname = 'addon_dev_tool.close_all_files'
    bl_description = "Closes all files in the text editor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return len(bpy.data.texts) > 0

    def execute(self, context):
        close_files(context, True)

        return {'FINISHED'}


class ADTRefreshFiles(Operator):
    bl_label = "Refresh Files"
    bl_idname = 'addon_dev_tool.refresh_files'
    bl_description = "Refresh all open project files in the text editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Find all modified files from the project and update them
        file_names = get_file_names(get_files(context, '.py'))

        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                for file in bpy.data.texts:
                    if file.name in file_names:
                        # Make the file the active file in the text editor
                        area.spaces[0].text = file

                        if file.is_modified:
                            bpy.ops.text.reload()
                            
        self.report({'INFO'}, "Loaded external changes")

        return {'FINISHED'}


class ADTInstallAddon(Operator):
    bl_label = "Install Addon"
    bl_idname = 'addon_dev_tool.install_addon'
    bl_description = "Install and enable the addon"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        i = is_project_valid(context)
        if len(i) is 0:
            return True

    def execute(self, context):
        project = context.scene.project_list[context.scene.project_list_index]
        path = project.location
        temp = bpy.utils.script_path_user()
        project_files = get_files(context)

        # If it is a multi-file addon get the folder
        if os.path.isdir(path):
            if path.endswith(os.sep):
                addon_name = os.path.basename(path.rstrip(os.sep))
                
                zip_project(temp + os.sep + addon_name + ".zip", project_files, path, addon_name)
                
                print(addon_name)

                bpy.ops.wm.addon_install(overwrite=True, filepath=temp + os.sep + addon_name + ".zip")

                bpy.ops.wm.addon_enable(module=addon_name)

                # remove the temporary zip file
                os.remove(temp + os.sep + addon_name + ".zip")

        # Otherwise, get the name of the file
        elif os.path.isfile(path):
            addon_name = os.path.basename(path)

            bpy.ops.wm.addon_install(overwrite=True, filepath=path)
            bpy.ops.wm.addon_enable(module=os.path.splitext(addon_name)[0])
        
        self.report({'INFO'}, "Installed addon {0}".format(project.name))
        return {'FINISHED'}


class ADTRemoveAddon(Operator):
    bl_label = "Uninstall Addon"
    bl_idname = 'addon_dev_tool.remove_addon'
    bl_description = "Remove the addon"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        project = context.scene.project_list[context.scene.project_list_index]
        path = project.location
        addon_name = ""
        
        if os.path.isdir(path):
            addon_name = os.path.basename(path.rstrip(os.sep))
        elif os.path.isfile(path):
            addon_name = os.path.basename(path)
            
        addon_name = os.path.splitext(addon_name)[0]

        return addon_name in bpy.context.user_preferences.addons.keys()

    def execute(self, context):
        project = context.scene.project_list[context.scene.project_list_index]
        path = project.location
        addon_name = ""
        
        if os.path.isdir(path):
            addon_name = os.path.basename(path.rstrip(os.sep))
        elif os.path.isfile(path):
            addon_name = os.path.basename(path)
            
        addon_name = os.path.splitext(addon_name)[0]

        bpy.ops.wm.addon_remove(module=addon_name)
        print(addon_name)
        
        self.report({'INFO'}, "Uninstalled addon {0}".format(addon_name))

        return {'FINISHED'}
    

class ADTExport(Operator, ExportHelper):
    bl_label = "Export For Distribution"
    bl_idname = 'addon_dev_tool.export'
    bl_description = "Export the file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".zip"

    def execute(self, context):
        project = context.scene.project_list[context.scene.project_list_index]
        path = project.location
        temp = bpy.utils.script_path_user()
        project_files = get_files(context)

        # If it is a multi-file addon get the folder
        if os.path.isdir(path):
            if path.endswith(os.sep):
                addon_name = os.path.basename(path.rstrip(os.sep))
                
                zip_project(self.filepath, project_files, path, addon_name)

        # Otherwise, get the name of the file
        elif os.path.isfile(path):
            addon_name = os.path.basename(path)
            
            zip = zipfile.ZipFile(self.filepath, 'w')

            for file in project_files:
                zip.write(path, file)

            zip.close()

            
        self.report({'INFO'}, "Exported addon {0}".format(project.name))
        return {'FINISHED'}  


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.project_list = CollectionProperty(type=Project)
    bpy.types.Scene.project_list_index = IntProperty(name="Index for project_list", default=0)

    bpy.app.handlers.load_post.append(get_projects)
    bpy.app.handlers.scene_update_pre.append(save_projects)


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.project_list
    del bpy.types.Scene.project_list_index

    bpy.app.handlers.load_post.remove(get_projects)
    bpy.app.handlers.scene_update_pre.remove(save_projects)
