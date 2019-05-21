import bpy
from pathlib import Path

bl_info = {
    "name": "Overlord2 model import + textures",
    "author": "RED_EYE",
    "version": (0, 1),
    "blender": (2, 29, 0),
    "location": "File > Import-Export > Overlord2 model (.prp)(converted to json) ",
    "description": "Addon allows to import Overlord2 models(converted to json)",
    "category": "Import-Export"
}

from bpy.props import StringProperty, BoolProperty, CollectionProperty


class Overlord2_OT_operator(bpy.types.Operator):
    """Load Overlord2 prp(converted to json) models"""
    bl_idname = "import_mesh.prp"
    bl_label = "Import Overlord2 model"
    bl_options = {'UNDO'}

    filepath = StringProperty(
        subtype='FILE_PATH',
    )
    files = CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    normal_bones = BoolProperty(name="Make normal skeleton?", default=False, subtype='UNSIGNED')
    join_clamped = BoolProperty(name="Join clamped meshes?", default=False, subtype='UNSIGNED')
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        from . import PRP_Import
        directory = Path(self.filepath).parent.absolute()
        for file in self.files:
            importer = PRP_Import.PRPIO(str(directory / file.name), join_bones=self.normal_bones)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import(self, context):
    self.layout.operator(Overlord2_OT_operator.bl_idname, text="Overlord2 model (.prp)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
