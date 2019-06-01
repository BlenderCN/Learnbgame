bl_info = {
    "name": "Import multiple FBX files",
    "author": "chombor, poor",
    "version": (0, 0, 0, 0),
    "blender": (2, 78, 5),
    "location": "File > Import-Export",
    "description": "Import multiple FBX files",
    "wiki_url": "https://github.com/chombor/pyb/",
    "category": "Learnbgame",
}


import os
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import (StringProperty, CollectionProperty)


class ImportMultipleFbxs(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.multiple_fbxs"
    bl_label = "Import multiple FBX's"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})
    files = CollectionProperty(type=bpy.types.PropertyGroup)


    def execute(self, context):
        folder = (os.path.dirname(self.filepath))
        for i in self.files:
            path_to_file = (os.path.join(folder, i.name))
            bpy.ops.import_scene.fbx(filepath = path_to_file,)
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportMultipleFbxs.bl_idname, text="FBX Batch (.fbx)")
def register():
    bpy.utils.register_class(ImportMultipleFbxs)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
def unregister():
    bpy.utils.unregister_class(ImportMultipleFbxs)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
