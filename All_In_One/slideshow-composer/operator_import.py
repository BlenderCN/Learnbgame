import bpy
from . import file_utils
from . import strips


class ImportFiles(bpy.types.Operator, strips.StripsCreator):
    bl_idname = "slideshow_composer.import_files"
    bl_label = "Import files"
    bl_description = "Import selected files"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        file_list = [x['name'] for x in self.files]
        self.create_strips(files=file_utils.find_files_recursively_in_dir(self.directory, file_list))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ImportDirectory(bpy.types.Operator, strips.StripsCreator):
    bl_idname = "slideshow_composer.import_directory"
    bl_label = "Import directory"
    bl_description = "Import all files from a directory"
    bl_options = {'REGISTER', 'UNDO'}

    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        path_list = [self.directory]
        self.create_strips(files=file_utils.find_files_recursively(path_list))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
