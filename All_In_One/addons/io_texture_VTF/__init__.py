from pathlib import Path
from .vtf import import_texture, export_texture
from .vmt import VMT
from . import blender_material
import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty, EnumProperty
import os.path
import sys

# Add shared library to the path
sys.path.append(".ValveFileSystem")

bl_info = {
    "name": "Source Engine VTF Texture import",
    "author": "RED_EYE",
    "version": (2, 0,),
    "blender": (2, 80, 0),
    'warning': 'Uses a lot of ram (1Gb for 4k texture)',
    "location": "File > Import-Export > Source Engine texture import (VTF)",
    "description": "Import-Export Source Engine texture import (VTF)",
    # "wiki_url": "http://www.barneyparker.com/blender-json-import-export-plugin",
    # "tracker_url": "http://www.barneyparker.com/blender-json-import-export-plugin",
    "category": "Learnbgame",
}
print(
    'Appending "{}" to PATH'.format(
        os.path.abspath(
            os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class VTFImporter_OT_operator(bpy.types.Operator):
    """Load Source Engine VTF texture"""
    bl_idname = "import_texture.vtf"
    bl_label = "Import VTF"
    bl_options = {'UNDO'}

    filepath = StringProperty(
        subtype='FILE_PATH',
    )
    files = CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement)

    load_alpha = BoolProperty(default=True,
                              name='Load alpha into separate image')
    only_alpha = BoolProperty(default=False, name='Only load alpha')
    filter_glob = StringProperty(default="*.vtf", options={'HIDDEN'})

    def execute(self, context):
        directory = Path(self.filepath).parent.absolute()
        for file in self.files:
            import_texture(str(directory / file.name),
                           self.load_alpha, self.only_alpha)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VMTImporter_OT_operator(bpy.types.Operator):
    """Load Source Engine VMT material"""
    bl_idname = "import_texture.vmt"
    bl_label = "Import VMT"
    bl_options = {'UNDO'}

    filepath = StringProperty(
        subtype='FILE_PATH',
    )

    filter_glob = StringProperty(default="*.vmt", options={'HIDDEN'})
    game = StringProperty(name="PATH TO GAME", subtype='FILE_PATH', default="")
    override = BoolProperty(default=False, name='Override existing?')

    def execute(self, context):
        vmt = VMT(self.filepath, self.game)
        mat = blender_material.BlenderMaterial(vmt)
        mat.load_textures()
        if mat.create_material(
                self.override) == 'EXISTS' and not self.override:
            self.report({'INFO'}, '{} material already exists')
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VTFExport_OT_operator(bpy.types.Operator):
    """Export VTF texture"""
    bl_idname = "export_texture.vtf"
    bl_label = "Export VTF"

    filename_ext = ".vtf"

    filter_glob = StringProperty(default="*.vtf", options={'HIDDEN'})

    filepath = StringProperty(
        subtype='FILE_PATH',
    )

    filename = StringProperty(
        name="File Name",
        description="Name used by the exported file",
        maxlen=255,
        subtype='FILE_NAME',
    )

    imgFormat = EnumProperty(
        name="VTF Type Preset",
        description="Choose a preset. It will affect the result's format and flags.",
        items=(('RGBA8888Simple', "RGBA8888 Simple", "RGBA8888 format, format-specific Eight Bit Alpha flag only"),
               ('RGBA8888Normal', "RGBA8888 Normal Map",
                "RGBA8888 format, format-specific Eight Bit Alpha and Normal Map flags"),
               ('DXT1Simple', "DXT1 Simple", "DXT1 format, no flags"),
               ('DXT5Simple', "DXT5 Simple",
                "DXT5 format, format-specific Eight Bit Alpha flag only"),
               ('DXT1Normal', "DXT1 Normal Map",
                "DXT1 format, Normal Map flag only"),
               ('DXT5Normal', "DXT5 Normal Map", "DXT5 format, format-specific Eight Bit Alpha and Normal Map flags")),
        default='RGBA8888Simple',
    )

    def execute(self, context):
        sima = context.space_data
        ima = sima.image
        if ima is None:
            self.report({"ERROR_INVALID_INPUT"}, "No Image provided")
        else:
            print(context)
            export_texture(ima, self.filepath, self.imgFormat)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            blend_filepath = context.blend_data.filepath
            if not blend_filepath:
                blend_filepath = "untitled"
            else:
                blend_filepath = os.path.splitext(blend_filepath)[0]
                self.filepath = os.path.join(
                    os.path.dirname(blend_filepath),
                    self.filename + self.filename_ext)
        else:
            self.filepath = os.path.join(
                os.path.dirname(
                    self.filepath),
                self.filename +
                self.filename_ext)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import(self, context):
    self.layout.operator(
        VTFImporter_OT_operator.bl_idname,
        text="VTF texture (.vtf)")
    self.layout.operator(
        VMTImporter_OT_operator.bl_idname,
        text="VMT texture (.vmt)")


def export(self, context):
    curImg = context.space_data.image
    if curImg is None:
        self.layout.operator(
            VTFExport_OT_operator.bl_idname,
            text='Export to VTF')
    else:
        self.layout.operator(VTFExport_OT_operator.bl_idname, text='Export to VTF').filename = \
            os.path.splitext(curImg.name)[0]


classes = (
    VTFImporter_OT_operator,
    VMTImporter_OT_operator,
    VTFExport_OT_operator)
register_, unregister_ = bpy.utils.register_classes_factory(classes)


def register():
    register_()
    # bpy.utils.register_module(__name__)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)
    bpy.types.IMAGE_MT_image.append(export)


def unregister():
    # bpy.utils.unregister_module(__name__)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.types.IMAGE_MT_image.remove(export)
    unregister_()


if __name__ == "__main__":
    register()
