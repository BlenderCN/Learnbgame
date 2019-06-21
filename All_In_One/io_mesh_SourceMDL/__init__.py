import bpy
from pathlib import Path

bl_info = {
    "name": "Source Engine model_path import + textures (.mdl, .file_data, .vtx)",
    "author": "RED_EYE",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > SourceEngine MDL (.mdl, .file_data, .vtx) ",
    "description": "Addon allows to import Source Engine models",
    'warning': 'May crash blender',
    # "wiki_url": "http://www.barneyparker.com/blender-json-import-export-plugin",
    # "tracker_url": "http://www.barneyparker.com/blender-json-import-export-plugin",
    "category": "Learnbgame",
}

from bpy.props import StringProperty, BoolProperty, CollectionProperty


class MDLImporter_OT_operator(bpy.types.Operator):
    """Load Source Engine MDL models"""
    bl_idname = "import_mesh.mdl"
    bl_label = "Import Source mdl model"
    bl_options = {'UNDO'}

    filepath = StringProperty(
        subtype='FILE_PATH',
    )
    files = CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    normal_bones = BoolProperty(name="Make normal skeleton or original from source?", default=False, subtype='UNSIGNED')
    join_clamped = BoolProperty(name="Join clamped meshes?", default=False, subtype='UNSIGNED')
    write_qc = BoolProperty(name="Write QC file", default=False, subtype='UNSIGNED')
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    def execute(self, context):
        from . import io_Mdl
        directory = Path(self.filepath).parent.absolute()
        for file in self.files:
            importer = io_Mdl.IOMdl(str(directory / file.name),
                                    join_bones=self.normal_bones, join_clamped=self.join_clamped)
            if self.write_qc:
                from . import QC
                qc = QC.QC(importer.MDL)
                qc_file = bpy.data.texts.new('{}.qc'.format(Path(file.name).stem))
                qc.write_header(qc_file)
                qc.write_models(qc_file)
                qc.write_skins(qc_file)
                qc.write_misc(qc_file)
                qc.write_sequences(qc_file)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VmeshImporter_OT_operator(bpy.types.Operator):
    """Load Source2 Engine VMESH models"""
    bl_idname = "import_mesh.vmesh"
    bl_label = "Import vmehs_c"
    bl_options = {'UNDO'}

    filepath = StringProperty(
        subtype='FILE_PATH',
    )
    filter_glob = StringProperty(default="*.vmesh_c", options={'HIDDEN'})

    def execute(self, context):
        from .Source2 import Vmesh_IO
        # doTexture = True
        # if self.properties.WorkDir == '': doTexture = False
        # io_MDL.IO_MDL(self.filepath, working_directory=self.properties.WorkDir,
        #               import_textures=doTexture and self.properties.Import_textures,
        #               normal_bones=self.properties.normal_bones)
        Vmesh_IO.VMESH_IO(self.filepath).build_meshes()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VmdlImporter_OT_operator(bpy.types.Operator):
    """Load Source2 Engine VMESH models"""
    bl_idname = "import_mesh.vmdl"
    bl_label = "Import vmdl_c"
    bl_options = {'UNDO'}

    filepath = StringProperty(
        subtype='FILE_PATH',
    )

    # WorkDir = StringProperty(name="path to folder with gameinfo.txt", maxlen=1024, default="", subtype='FILE_PATH')
    # Import_textures = BoolProperty(name="Import textures?\nLARGE TEXTURES MAY CAUSE OUT OF MEMORY AND CRASH",
    #                                default=False, subtype='UNSIGNED')
    import_meshes = BoolProperty(name="Import meshes", default=True, subtype='UNSIGNED')
    filter_glob = StringProperty(default="*.vmdl_c", options={'HIDDEN'})

    def execute(self, context):
        from .Source2 import Vmdl_IO
        Vmdl_IO.Vmdl_IO(self.filepath, self.import_meshes)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

classes = (VmdlImporter_OT_operator, VmeshImporter_OT_operator,MDLImporter_OT_operator)
register_, unregister_ = bpy.utils.register_classes_factory(classes)

def menu_import(self, context):
    self.layout.operator(MDLImporter_OT_operator.bl_idname, text="Source model (.mdl)")
    self.layout.operator(VmeshImporter_OT_operator.bl_idname, text="Source2 mesh (.vmesh_c)")
    self.layout.operator(VmdlImporter_OT_operator.bl_idname, text="Source2 model (.vmdl_c)")


def register():
    register_()
    # bpy.utils.register_module(__name__)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    # bpy.utils.unregister_module(__name__)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    unregister_()


if __name__ == "__main__":
    register()
