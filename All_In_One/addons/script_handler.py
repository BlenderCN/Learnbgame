bl_info = {
    "name": "ScriptHandler",
    "author": "Jacob Morris",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Text Editor -> Properties -> MISC -> ScriptHandler",
    "description": "Makes project and file handling easier in the text editor, and makes it simpler to reload and run scripts",
    "category": "Learnbgame",
}



from bpy.types import Panel, PropertyGroup, UIList, Operator, OperatorFileListElement
from bpy.props import StringProperty, CollectionProperty, IntProperty, PointerProperty, BoolProperty
from pathlib import Path
import bpy
from bpy_extras.io_utils import ImportHelper
from os import path

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Original Author = Jacob Morris
# Email Address = blendingjake@gmail.com



# ---------------------------------------------------------------------------------------------
# MISC FUNCTIONS
# ---------------------------------------------------------------------------------------------
def on_file_index_change(_, context):
    props = context.scene.script_handler

    if props.projects:
        project = props.projects[props.project_index]

        if project.files:
            file = project.files[project.file_index]

            block = bpy.data.texts.get(file.filename, None)
            if block is not None:
                context.space_data.text = block


# ---------------------------------------------------------------------------------------------
# PANEL
# ---------------------------------------------------------------------------------------------
class ScriptHandlerPanel(Panel):
    bl_idname = "OBJECT_PT_script_handler"
    bl_label = "ScriptHandler"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        props = scn.script_handler

        layout.label(text="Projects")

        row = layout.row()
        row.template_list("OBJECT_UL_script_handler_projects", "", props, "projects", props, "project_index", rows=5)

        col = row.column()
        col.operator("ops.sh_move_project_up", text="", icon="TRIA_UP")
        col.operator("ops.sh_move_project_down", text="", icon="TRIA_DOWN")
        col.operator("ops.sh_remove_project", text="", icon="X")

        layout.operator("ops.sh_add_project", icon="ADD")
        layout.operator("ops.sh_rename_project", icon="CONSOLE")
        layout.prop(props, "new_project_name")

        if 0 <= props.project_index < len(props.projects):
            layout.separator()
            layout.label(text="Files")

            project = props.projects[props.project_index]

            row = layout.row()
            row.template_list("OBJECT_UL_script_handler_files", "", project, "files", project, "file_index",
                              rows=7)

            col = row.column()
            col.operator("ops.sh_move_file_up", text="", icon="TRIA_UP")
            col.operator("ops.sh_move_file_down", text="", icon="TRIA_DOWN")
            col.operator("ops.sh_remove_file", text="", icon="X")

            layout.operator("ops.sh_add_files", icon="FILEBROWSER")

            layout.separator()
            layout.operator("ops.sh_load_reload_files", icon="FILE_REFRESH")

            layout.separator()
            layout.operator("ops.sh_run_files", icon="PLAY")

            layout.separator()
            layout.operator("ops.sh_save_project_files", icon="WINDOW")

            layout.separator()
            layout.operator("ops.sh_remove_project_files", icon="REMOVE")


# ---------------------------------------------------------------------------------------------
# UI LISTS
# ---------------------------------------------------------------------------------------------
class OBJECT_UL_script_handler_projects(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        row.label(text=item.name)
        row.label(text="{} File(s)".format(len(item.files)))


class OBJECT_UL_script_handler_files(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        row.label(text=item.filename)
        row.prop(item, "runnable")


# ---------------------------------------------------------------------------------------------
# PROJECT OPERATORS
# ---------------------------------------------------------------------------------------------
class AddProject(Operator):
    bl_idname = "ops.sh_add_project"
    bl_label = "Add Project"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.new_project_name:
            project_names = set([x.name for x in props.projects])

            if props.new_project_name not in project_names:
                project = props.projects.add()
                project.name = props.new_project_name
                props.project_index = len(props.projects) - 1
            else:
                self.report({"INFO"}, "A project already exists with the name {}".format(props.new_project_name))

        return {"FINISHED"}


class RemoveProject(Operator):
    bl_idname = "ops.sh_remove_project"
    bl_label = "Remove Project"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            # remove files
            for file in props.projects[props.project_index].files:
                block = bpy.data.texts.get(file.filename, None)

                if block is not None:
                    context.space_data.text = block
                    bpy.ops.text.unlink()

            props.projects.remove(props.project_index)
            props.project_index = max(0, props.project_index - 1)

        return {"FINISHED"}


class MoveProjectUp(Operator):  # "UP" = closer to 0
    bl_idname = "ops.sh_move_project_up"
    bl_label = "Move Project Up"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.project_index > 0:  # do we have room to move towards 0 by one unit?
            props.projects.move(props.project_index, props.project_index-1)
            props.project_index = max(0, props.project_index-1)

        return {"FINISHED"}


class MoveProjectDown(Operator):  # "DOWN" = closer to len(list)
    bl_idname = "ops.sh_move_project_down"
    bl_label = "Move Project Down"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.project_index < len(props.projects):  # do we have room to move towards the end?
            props.projects.move(props.project_index, props.project_index+1)
            props.project_index = min(len(props.projects)-1, props.project_index+1)

        return {"FINISHED"}


class RenameProject(Operator):
    bl_idname = "ops.sh_rename_project"
    bl_label = "Rename Project"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects and props.new_project_name != "":
            project_names = set([x.name for x in props.projects])

            if props.new_project_name not in project_names:
                props.projects[props.project_index].name = props.new_project_name
            else:
                self.report({"INFO"}, "A project already exists with the name {}".format(props.new_project_name))

        return {"FINISHED"}


# ---------------------------------------------------------------------------------------------
# FILE OPERATORS
# ---------------------------------------------------------------------------------------------
class AddFiles(Operator, ImportHelper):
    bl_idname = "ops.sh_add_files"
    bl_label = "Add File(s)"
    bl_options = {"UNDO", "INTERNAL"}

    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            project_files = set([x.filename for x in project.files])
            loaded_files = set([x.name for x in bpy.data.texts])

            for file in self.files:
                if file.name and file.name not in project_files:
                    new_file = project.files.add()
                    new_file.filepath = path.join(self.directory, file.name)
                    new_file.filename = file.name

                    if file.name not in loaded_files:
                        bpy.ops.text.open(filepath=new_file.filepath)
                    else:
                        self.report({"INFO"}, "The file named {} is already loaded".format(file.name))
                else:
                    self.report({"INFO"}, "This project already has a file named {}".format(file.name))

        return {"FINISHED"}


class RemoveFile(Operator):
    bl_idname = "ops.sh_remove_file"
    bl_label = "Remove File"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            if project.files:
                block = bpy.data.texts.get(project.files[project.file_index].filename, None)
                if block is not None:
                    context.space_data.text = block
                    bpy.ops.text.unlink()

                project.files.remove(project.file_index)
                project.file_index = max(0, project.file_index - 1)

        return {"FINISHED"}


class MoveFileUp(Operator):  # "UP" = closer to 0
    bl_idname = "ops.sh_move_file_up"
    bl_label = "Move File Up"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            if project.file_index > 0:  # do we have room to move towards 0 by one unit?
                project.files.move(project.file_index, project.file_index-1)
                project.file_index = max(0, project.file_index-1)

        return {"FINISHED"}


class MoveFileDown(Operator):  # "DOWN" = closer to len(list)
    bl_idname = "ops.sh_move_file_down"
    bl_label = "Move File Down"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            if project.file_index < len(project.files):  # do we have room to move towards the end?
                project.files.move(project.file_index, project.file_index+1)
                project.file_index = min(len(project.files)-1, project.file_index+1)

        return {"FINISHED"}


class LoadReloadFiles(Operator):
    bl_idname = "ops.sh_load_reload_files"
    bl_label = "(Re)Load Files"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            project_files = set()
            for file in project.files:
                project_files.add(file.filename)

                if file.filename in bpy.data.texts:
                    context.space_data.text = bpy.data.texts[file.filename]
                    bpy.ops.text.reload()
                else:
                    bpy.ops.text.open(filepath=file.filepath)

            if project.files and project.files[project.file_index].filename in bpy.data.texts:
                context.space_data.text = bpy.data.texts[project.files[project.file_index].filename]

        return {"FINISHED"}


class RunFiles(Operator):
    bl_idname = "ops.sh_run_files"
    bl_label = "Run Files"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            cur_block = context.space_data.text
            for file in project.files:
                if file.runnable:
                    if file.filename not in bpy.data.texts:  # load before running if needed
                        bpy.ops.text.open(filepath=file.filepath)
                    else:
                        context.space_data.text = bpy.data.texts[file.filename]

                    bpy.ops.text.run_script()

            if cur_block is not None:
                context.space_data.text = cur_block

        return {"FINISHED"}


class SaveProjectFiles(Operator):
    bl_idname = "ops.sh_save_project_files"
    bl_label = "Save Project Files"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            cur_block = context.space_data.text
            for file in project.files:
                if file.filename in bpy.data.texts:
                    context.space_data.text = bpy.data.texts[file.filename]
                    bpy.ops.text.save()

            if cur_block is not None:
                context.space_data.text = cur_block

        return {"FINISHED"}


class RemoveProjectFiles(Operator):
    bl_idname = "ops.sh_remove_project_files"
    bl_label = "Remove Project Files"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.script_handler

        if props.projects:
            project = props.projects[props.project_index]

            for file in project.files:
                if file.filename in bpy.data.texts:
                    context.space_data.text = bpy.data.texts[file.filename]
                    bpy.ops.text.unlink()

        return {"FINISHED"}


# ---------------------------------------------------------------------------------------------
# DATA STORAGE
# ---------------------------------------------------------------------------------------------
class FileProperties(PropertyGroup):
    filename: StringProperty(name="Name")
    filepath: StringProperty(name="Path")
    runnable: BoolProperty(name="Runnable", default=False)


class ProjectProperties(PropertyGroup):
    name: StringProperty(name="Name")
    files: CollectionProperty(type=FileProperties)
    file_index: IntProperty(update=on_file_index_change)


class ScriptHandlerProperties(PropertyGroup):
    projects: CollectionProperty(type=ProjectProperties)
    project_index: IntProperty(update=on_file_index_change)

    new_project_name: StringProperty(name="Project Name")


classes = (  # order is important to avoid errors while registering
    AddProject,
    RemoveProject,
    RenameProject,
    MoveProjectUp,
    MoveProjectDown,

    AddFiles,
    RemoveFile,

    MoveFileUp,
    MoveFileDown,

    LoadReloadFiles,
    RunFiles,

    SaveProjectFiles,
    RemoveProjectFiles,

    ScriptHandlerPanel,

    OBJECT_UL_script_handler_projects,
    OBJECT_UL_script_handler_files,

    FileProperties,
    ProjectProperties,
    ScriptHandlerProperties
)


# ---------------------------------------------------------------------------------------------
# REGISTRATION
# ---------------------------------------------------------------------------------------------
def register():
    from bpy.utils import register_class
    from bpy.types import Scene

    for cls in classes:
        register_class(cls)

    Scene.script_handler = PointerProperty(type=ScriptHandlerProperties)


def unregister():
    from bpy.utils import unregister_class
    from bpy.types import Scene

    for cls in classes:
        unregister_class(cls)

    del Scene.script_handler


if __name__ == "__main__":
    register()
