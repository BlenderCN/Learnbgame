
bl_info = {
    "name": "GES, GEM and GEO format",
    "author": "Shekn Itrch",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import-Export whole scene and material libraries to *.ges or *.gem format. Export only Cycles materials",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame",
    }

if "bpy" in locals():
    import importlib
    if "export_ges" in locals():
        importlib.reload(export_ges)


import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)


'''class ImportGES(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.ges"
    bl_label = "Import GES"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".ges"
    filter_glob = StringProperty(
        default="*.ges",
        options={'HIDDEN'},
    )

    def execute(self, context):
        print("Call import GES")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout'''

#------------------------------------------------
#------------------------------------------------
#------------------Export------------------------
#------------------------------------------------
#------------------------------------------------


class ExportGES(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.ges"
    bl_label = 'Export GES'
    bl_options = {'PRESET'}

    filename_ext = ".ges"
    filter_glob = StringProperty(
        default="*.ges",
        options={'HIDDEN'},
    )
    mode = EnumProperty(items=(("ALL_SCENE", "All scene", ""),
                               ("SELECTED_OBJECTS", "Selected objects", ""),
                               ("ALL_MATERIALS", "All materials", ""),
                               ("SELECTED_MATERIAL", "Selected material", "")),
                        name="Mode",
                        description="",
                        default="ALL_SCENE")
    is_copy_textures = BoolProperty(name="Copy textures",
                                    description="",
                                    default=True)
    texture_path_mode = EnumProperty(items=(("RELATIVE", "Relative", ""),
                                            ("ABSOLUTE", "Absolute", "")),
                                     name="Texture and meshes path mode",
                                     description="",
                                     default="RELATIVE")

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")
        keywords = self.as_keywords(ignore=("check_existing", "filter_glob"))
        from . import export_ges
        return export_ges.save(self, context, **keywords)


'''def menu_func_import(self, context):
    self.layout.operator(ImportGES.bl_idname,
                         text="General Export Scene (.ges)")'''


def menu_func_export(self, context):
    self.layout.operator(ExportGES.bl_idname, text="General Export Scene(.ges)")

classes = (
    # ImportGES,
    ExportGES,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
